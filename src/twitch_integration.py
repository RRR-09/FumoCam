import json
import traceback
from asyncio import create_task
from asyncio import sleep as async_sleep
from datetime import datetime
from math import floor
from os import getenv, system
from time import strftime, time

from twitchio import Chatter as TwitchChatter
from twitchio import Message as TwitchMessage
from twitchio.ext import commands, routines

from chat_ocr import can_activate_ocr, do_chat_ocr
from config import ActionQueueItem, Twitch
from health import CFG, do_crash_check
from utilities import discord_log, error_log, log, log_process, notify_admin, output_log


class TwitchBot(commands.Bot):
    def __init__(self, token: str, channel_name: str):
        super().__init__(token=token, prefix="!", initial_channels=[channel_name])
        self.help_msgs = [
            f"For a full list of commands, visit {CFG.help_url}",
            "If you just want to play around, try '!m hello', '!move w 2', or '!nav shrimp'",
            f"For previous updates, visit {CFG.updates_url}",
        ]

    async def event_ready(self):
        print(f'[Twitch] Logged in as "{self.nick}"')
        await CFG.async_main()
        await self.run_subroutines()

    async def event_message(self, message: TwitchMessage):
        if message.echo:
            return
        msg_str = f"[Twitch] {message.author.display_name}: {message.content}"

        print(msg_str.encode("ascii", "ignore").decode("ascii", "ignore"))

        log_task = create_task(self.do_discord_log(message))

        if message.author.name not in CFG.twitch_blacklist:
            commands_task = create_task(self.handle_commands(message))
        else:
            if message.content.startswith("!dev"):
                await self.manual_dev_command(message)

        if await self.is_new_user(message.author.name):
            for msg in self.help_msgs:
                await message.channel.send(msg)

            await message.channel.send(
                f"Welcome to the stream {message.author.mention}! "
                "This is a 24/7 bot you can control with chat commands! See above."
            )

        try:
            await log_task
        except Exception:
            print(traceback.format_exc())
            notify_admin(f"```{traceback.format_exc()}```")

        if message.author.name not in CFG.twitch_blacklist:
            try:
                await commands_task
            except commands.errors.CommandNotFound:
                pass
            except Exception:
                print(traceback.format_exc())
                notify_admin(f"```{traceback.format_exc()}```")

    async def event_command_error(self, ctx: commands.Context, error: Exception):
        if type(error) == commands.errors.CommandNotFound:
            await ctx.send("[Not a valid command!]")
            return
        print(f'"{type(error)}"')
        print(f'"{commands.errors.CommandNotFound}"')
        traceback.print_exception(type(error), error, error.__traceback__)
        error_log(f"({type(error)})\n{error}\n{error.__traceback__}")

    async def is_new_user(self, username):
        if username in CFG.twitch_chatters:
            return False
        CFG.twitch_chatters.add(username)
        with open(CFG.twitch_chatters_path, "w") as f:
            json.dump(list(CFG.twitch_chatters), f)
        return True

    async def do_discord_log(self, message: TwitchMessage):
        author = message.author.display_name
        author_url = (
            f"https://www.twitch.tv/popout/becomefumocam/viewercard/{author.lower()}"
        )
        author_avatar = "https://brand.twitch.tv/assets/images/black.png"
        message = message.content
        await discord_log(message, author, author_avatar, author_url)

    async def get_args(self, ctx: commands.Context):
        msg = ctx.message.content
        prefix = ctx.prefix
        command_name = ctx.command.name
        return msg.replace(f"{prefix}{command_name}", "", 1).strip().split()

    async def is_dev(self, author: TwitchChatter):
        return author.name.lower() in Twitch.admins

    async def run_subroutines(self):
        print("[Twitch] Initializing Subroutines")
        subroutines = [
            routine_anti_afk,
            routine_check_better_server,
            routine_clock,
            routine_crash_check,
            routine_reboot,
            routine_ocr,
        ]
        for subroutine in subroutines:
            print(
                f"[Routine] Starting subroutine: {subroutine._coro.__name__.replace('routine_','')}"
            )
            subroutine.start()

    # Basic Commands

    @commands.command()
    async def help(self, ctx: commands.Context):
        for msg in self.help_msgs:
            await ctx.send(msg)

    @commands.command()
    async def backpack(self, ctx: commands.Context):
        await ctx.send(
            f"[{'Closing' if CFG.backpack_open else 'Opening'} backpack,"
            " please make sure it's closed when you're done!]"
        )
        await CFG.add_action_queue(ActionQueueItem("backpack_toggle"))

    @commands.command()
    async def click(self, ctx: commands.Context):
        await CFG.add_action_queue(ActionQueueItem("mouse_click"))

    @commands.command()
    async def grief(self, ctx: commands.Context):
        await CFG.add_action_queue(ActionQueueItem("grief"))

    @commands.command()
    async def hidemouse(self, ctx: commands.Context):
        await CFG.add_action_queue(ActionQueueItem("mouse_hide"))

    @commands.command()
    async def item(self, ctx: commands.Context):
        args = await self.get_args(ctx)
        if len(args) < 1:
            await ctx.send("[Please specify an item number! (Must be 1-8)")
            return
        try:
            item_number = int(args[0])
            if item_number not in CFG.backpack_item_positions:
                raise
        except Exception:
            await ctx.send("[Error! Invalid number specified. (Must be 1-8)]")
            return
        if not CFG.backpack_open:
            await ctx.send(
                "[Doesn't seem like the backpack is open! Clicking anyway, just in case."
                "(Use !backpack to open, if needed)]"
            )
        action = ActionQueueItem("backpack_item", {"item_number": item_number})
        await CFG.add_action_queue(action)

    @commands.command()
    async def jump(self, ctx: commands.Context):
        await CFG.add_action_queue(ActionQueueItem("jump"))

    @commands.command()
    async def mute(self, ctx: commands.Context):
        action = ActionQueueItem("mute", {"set_muted": None})
        await CFG.add_action_queue(action)

    @commands.command()
    async def mouse(self, ctx: commands.Context):
        args = await self.get_args(ctx)
        if len(args) < 2:
            await ctx.send(
                "[Please specify the two numbers (x and y) that you want the mouse to"
                " move away from center of the screen!]"
            )
            return
        try:
            x = int(args[0])
            y = int(args[1])
        except Exception:
            await ctx.send("[Error! Invalid number(s) specified.]")
            return
        action = ActionQueueItem("mouse_move", {"x": x, "y": y, "twitch_ctx": ctx})
        await CFG.add_action_queue(action)

    @commands.command()
    async def unmute(self, ctx: commands.Context):
        action = ActionQueueItem("mute", {"set_muted": False})
        await CFG.add_action_queue(action)

    @commands.command()
    async def respawnforce(self, ctx: commands.Context):
        await CFG.add_action_queue(ActionQueueItem("respawn_force"))

    @commands.command()
    async def respawn(self, ctx: commands.Context):
        await CFG.add_action_queue(ActionQueueItem("respawn"))

    @commands.command()
    async def sit(self, ctx: commands.Context):
        await CFG.add_action_queue(ActionQueueItem("sit"))

    @commands.command()
    async def use(self, ctx: commands.Context):
        await CFG.add_action_queue(ActionQueueItem("use"))

    # Complex commands/Commands with args
    async def camera_pitch_handler(
        self, pitch_camera_direction: str, ctx: commands.Context
    ):
        pitch: float = 45
        max_pitch: float = 180
        args = await self.get_args(ctx)
        if args:
            try:
                pitch = float(args[0])
                if not (max_pitch >= pitch > 0):
                    await ctx.send(
                        f"[{args[0]} is too high/low! Please use an angle between 0 and {max_pitch}.]"
                    )
                    return
            except Exception:
                await ctx.send("[Error! Invalid number specified.]")
                return

        action = ActionQueueItem(
            "camera_pitch",
            {
                "pitch_direction": pitch_camera_direction,
                "pitch_degrees": pitch,
            },
        )
        await CFG.add_action_queue(action)

    # Complex commands/Commands with args
    async def camera_turn_handler(
        self, turn_camera_direction: str, ctx: commands.Context
    ):
        turn_degrees: float = 45
        max_turn_degrees: float = 360
        args = await self.get_args(ctx)
        if args:
            try:
                turn_degrees = float(args[0])
                if not (max_turn_degrees >= turn_degrees > 0):
                    await ctx.send(
                        f"[{args[0]} is too high/low! Please use an angle between 0 and 360.]"
                    )
                    return
            except Exception:
                await ctx.send("[Error! Invalid number specified.]")
                return

        action = ActionQueueItem(
            "camera_turn",
            {
                "turn_direction": turn_camera_direction,
                "turn_degrees": turn_degrees,
            },
        )
        await CFG.add_action_queue(action)

    @commands.command()
    async def left(self, ctx: commands.Context):
        turn_camera_direction = "left"
        await self.camera_turn_handler(turn_camera_direction, ctx)

    @commands.command()
    async def right(self, ctx: commands.Context):
        turn_camera_direction = "right"
        await self.camera_turn_handler(turn_camera_direction, ctx)

    @commands.command()
    async def up(self, ctx: commands.Context):
        pitch_camera_direction = "up"
        await self.camera_pitch_handler(pitch_camera_direction, ctx)

    @commands.command()
    async def down(self, ctx: commands.Context):
        pitch_camera_direction = "down"
        await self.camera_pitch_handler(pitch_camera_direction, ctx)

    async def manual_dev_command(self, message: TwitchMessage):
        args = message.content.split(" ", 1)
        if len(args) < 2:
            await message.channel.send(
                "[Specify a message, this command is for emergencies! (Please do not misuse it)]"
            )
            return
        msg = args[-1]
        notify_admin(f"{message.author}: {msg}")
        await message.channel.send(
            "[Notified dev! As a reminder, you have been blacklisted by a trusted member, so your"
            " controls will not work. If you feel this is in error, use this commmand.]"
        )

    @commands.command()
    async def dev(self, ctx: commands.Context):
        args = await self.get_args(ctx)
        if not args:
            await ctx.send(
                "[Specify a message, this command is for emergencies! (Please do not misuse it)]"
            )
            return
        msg = " ".join(args)
        notify_admin(f"{ctx.message.author.display_name}: {msg}")
        await ctx.send(
            "[Notified dev! As a reminder, this command is only for emergencies. If you were unaware of this and used"
            " the command by mistake, please write a message explaining that or you may be timed-out/banned.]"
        )

    @commands.command()
    async def leap(self, ctx: commands.Context):
        forward_time = 0.4
        jump_time = 0.3
        max_forward_time = 1
        max_jump_time = 1
        args = await self.get_args(ctx)
        if len(args) > 0:
            try:
                number = float(args[0])
                if max_forward_time >= number > 0:
                    forward_time = number
                else:
                    await ctx.send(
                        f"[{args[0]} is too high/low! Please use a time between 0 and {max_forward_time}.]"
                    )
                    return
            except Exception:
                await ctx.send("[Error! Invalid number specified.]")
                return
        if len(args) > 1:
            try:
                number = float(args[1])
                if max_jump_time >= number > 0:
                    jump_time = number
                else:
                    await ctx.send(
                        f"[{args[1]} is too high/low! Please use a time between 0 and {max_jump_time}.]"
                    )
                    return
            except Exception:
                await ctx.send("[Error! Invalid number specified.]")
                return
        action = ActionQueueItem(
            "leap",
            {"forward_time": forward_time, "jump_time": jump_time},
        )
        await CFG.add_action_queue(action)

    @commands.command()  # Send message in-game
    async def m(self, ctx: commands.Context):
        args = await self.get_args(ctx)
        if not args:
            await ctx.send('[Please specify a message! (i.e. "!m Hello World!"]')
            return

        msg = " ".join(args)
        if len(msg) > 100:
            await ctx.send(
                "[In-game character limit is 100! Please shorten your message.]"
            )
            return
        is_dev = await self.is_dev(ctx.message.author)

        # Disable whisper functionality
        if msg.startswith("[") or msg.startswith("/w"):
            await ctx.send("[You do not have permission to whisper.]")
            return

        # Make muting dev-only
        elif msg.startswith("/mute") or msg.startswith("/unmute"):
            if is_dev:
                action = ActionQueueItem("chat", {"msgs": [msg]})
            else:
                await ctx.send("[You do not have permission to mute/unmute.]")
                return

        # Allow /e, disable all other commands from twitch
        elif msg.startswith("/"):
            if msg.startswith("/e"):
                CFG.current_emote = msg
                action = ActionQueueItem("chat", {"msgs": [msg]})
            else:
                return

        # Chat with CamDev Tag
        elif ctx.message.author.display_name == "BecomeFumoCam":
            action = ActionQueueItem(
                "chat_with_name", {"name": "[CamDev]:", "msgs": [msg]}
            )

        # Standard chat
        else:
            if ctx.message.author.display_name not in CFG.chat_trusted_users:
                await ctx.send("[Sorry! As a temporary security measure, users without the 'Trusted' role cannot send chat messages.]")
                await ctx.send("[Please check back in a few days!]")
                return

            action = ActionQueueItem(
                "chat_with_name",
                {"name": f"{ctx.message.author.display_name}:", "msgs": [msg]},
            )
        await CFG.add_action_queue(action)

    @commands.command()  # Send message in-game
    async def blacklist(self, ctx: commands.Context):
        if ctx.message.author.name.lower() not in CFG.vip_twitch_names:
            await ctx.send("[You do not have permission to run this command!]")
        args = await self.get_args(ctx)
        if not args:
            await ctx.send("[Please specify a user!]")
            return
        try:
            name = args[0].lower()
            if name[0] == "@":
                name = name[1:]
        except Exception:
            await ctx.send("[Please specify a user!]")
            return

        added = False
        if name not in CFG.twitch_blacklist:
            CFG.twitch_blacklist.append(name)
            with open(str(CFG.twitch_blacklist_path), "w") as f:
                json.dump(CFG.twitch_blacklist, f)
            added = True

        await ctx.send(
            f"['{name}' has {'already' if not added else ''} been blacklisted from interacting with FumoCam.]"
        )
        await async_sleep(1)
        await ctx.send("[It is recommended you also report them to Twitch, if needed.]")
        await async_sleep(1)
        await ctx.send(
            f"[@{name} if you feel this is in error, please type '!dev unjust ban' in chat."
            " The dev has already been notified]"
        )

        mod_url = f"<https://www.twitch.tv/popout/becomefumocam/viewercard/{ctx.message.author.name.lower()}>"
        target_url = (
            f"<https://www.twitch.tv/popout/becomefumocam/viewercard/{name.lower()}>"
        )

        notify_admin(
            f"{ctx.message.author.name} has blacklisted {name}\n{mod_url}\n{target_url}"
        )

    @commands.command()
    async def move(self, ctx: commands.Context):
        move_time: float = 1
        max_move_time: float = 10
        valid_movement_keys = ["w", "a", "s", "d"]
        args = await self.get_args(ctx)
        if not args or args[0].lower() not in valid_movement_keys:
            await ctx.send('[Please specify a valid direction! (i.e. "!move w")]')
            return
        move_key = args[0].lower()

        if len(args) > 1:
            try:
                move_time = float(args[1])
                if not (max_move_time >= move_time > 0):
                    await ctx.send(
                        f"[{args[1]} is too high/low! Please use a unit between 0 and {max_move_time}.]"
                    )
                    return
            except Exception:
                await ctx.send("[Error! Invalid number specified.]")
                return

        action = ActionQueueItem("move", {"move_key": move_key, "move_time": move_time})
        await CFG.add_action_queue(action)

    @commands.command()
    async def nav(self, ctx: commands.Context):
        args = await self.get_args(ctx)
        if not args or args[0].lower() not in CFG.nav_locations:
            await ctx.send("[Please specify a valid location!]")
            await ctx.send(f'[{", ".join(list(CFG.nav_locations.keys()))}]')
            return
        location = args[0].lower()
        await ctx.send("[Requested AutoNav! If we fail, re-run the command!]")
        await ctx.send(
            "[If we did not respawn, please run !respawnforce (we're stuck!) and re-run the !nav command.]"
        )
        action = ActionQueueItem("autonav", {"location": location})
        await CFG.add_action_queue(action)

    @commands.command()
    async def rejoin(self, ctx: commands.Context):
        if await self.is_dev(ctx.author):
            await ctx.send(f"[@{ctx.author.name} Added restart to queue]")
            CFG.crashed = True
            await CFG.add_action_queue(ActionQueueItem("rejoin"))
            CFG.crashed = False
        else:
            await ctx.send("[You do not have permission!]")

    async def zoom_handler(self, zoom_key, ctx: commands.Context):
        zoom_amount: float = 15
        max_zoom_amount: float = 100
        args = await self.get_args(ctx)
        if args:
            try:
                zoom_amount = float(args[0])
                if not (max_zoom_amount >= zoom_amount > 0):
                    await ctx.send(
                        f"[{args[0]} is too high/low! Please use a percentage between 0 and {max_zoom_amount}.]"
                    )
                    return
            except Exception:
                await ctx.send("[Error! Invalid number specified.]")
                return
        action = ActionQueueItem(
            "camera_zoom",
            {"zoom_key": zoom_key, "zoom_amount": zoom_amount},
        )
        await CFG.add_action_queue(action)

    @commands.command()
    async def zoomin(self, ctx: commands.Context):
        zoom_key = "i"
        await self.zoom_handler(zoom_key, ctx)

    @commands.command()
    async def zoomout(self, ctx: commands.Context):
        zoom_key = "o"
        await self.zoom_handler(zoom_key, ctx)


@routines.routine(minutes=10, wait_first=True)
async def routine_anti_afk():
    print("[Subroutine] AntiAFK")
    try:
        await CFG.add_action_queue(ActionQueueItem("anti_afk"))
        CFG.anti_afk_runs += 1
        if CFG.anti_afk_runs % 3 == 0:
            await CFG.add_action_queue(ActionQueueItem("chat", {"msgs": ["/clear"]}))
            await CFG.add_action_queue(ActionQueueItem("advert"))
            print("[Subroutine] Queued Advert")
            CFG.anti_afk_runs = 0
    except Exception:
        error_log(traceback.format_exc())


@routines.routine(minutes=1)
async def routine_check_better_server():
    print("[Subroutine] Better Server Check")
    try:
        while CFG.crashed:
            print("[Better Server Check] Currently crashed, waiting...")
            await async_sleep(60)
        await CFG.add_action_queue(ActionQueueItem("check_for_better_server"))
    except Exception:
        error_log(traceback.format_exc())


@routines.routine(seconds=1, wait_first=True)
async def routine_clock():
    current_time = strftime("%I:%M:%S%p EST")
    CFG.days_since_creation = floor((time() - CFG.epoch_time) / (60 * 60 * 24))
    output_log("clock", f"Day {CFG.days_since_creation}\n{current_time}")


@routines.routine(seconds=3, wait_first=True)
async def routine_ocr():
    if (
        CFG.action_running
        or CFG.crashed
        or (not CFG.chat_cleared_after_response)
        or (not CFG.chat_ocr_ready)
    ):
        return

    if not CFG.chat_ocr_active:
        if not CFG.chat_ocr_activation_queued and await can_activate_ocr():
            await CFG.add_action_queue(ActionQueueItem("activate_ocr"))
    else:
        try:
            # HACK: psuedo-blocking, make non-async
            CFG.chat_ocr_ready = False
            await do_chat_ocr()
        except Exception:
            CFG.chat_ocr_ready = True
            CFG.chat_cleared_after_response = True
            error_log(traceback.format_exc())


@routines.routine(time=datetime(year=1970, month=1, day=1, hour=3, minute=58))
async def routine_reboot():
    action_queue_item = ActionQueueItem(
        "chat", {"msgs": ["[System restart in 2 minutes]"]}
    )
    await CFG.add_action_queue(action_queue_item)
    await async_sleep(60)

    action_queue_item = ActionQueueItem(
        "chat", {"msgs": ["[System restart in 1 minute]"]}
    )
    await CFG.add_action_queue(action_queue_item)
    await async_sleep(60)

    log_process("System Shutdown")
    log("Initiating shutdown sequence")
    action_queue_item = ActionQueueItem("chat", {"msgs": ["[System restarting]"]})
    await CFG.add_action_queue(action_queue_item)
    await async_sleep(10)
    system("shutdown /f /r /t 0")  # nosec


@routines.routine(seconds=5, wait_first=True)
async def routine_crash_check():
    if CFG.crashed:
        return
    try:
        crashed = await do_crash_check()
        if crashed:
            print("[Routine] Crash detected")
            await CFG.add_action_queue(ActionQueueItem("handle_crash"))
            await async_sleep(60)
    except Exception:
        error_log(traceback.format_exc())


def twitch_main():
    token = getenv("TWITCH_BOT_TOKEN")
    channel = Twitch.channel_name
    bot = TwitchBot(token, channel)
    bot.run()


if __name__ == "__main__":  # Not supposed to run directly, but can be
    twitch_main()
