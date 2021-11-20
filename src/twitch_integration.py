from twitchio.ext import commands, routines
from asyncio import create_task
from commands import *
from datetime import datetime
import traceback
from math import floor


class TwitchBot(commands.Bot):
    def __init__(self, token, channel_name):
        super().__init__(token=token, prefix='!', initial_channels=[channel_name])

    
    async def event_ready(self):
        print(f"[Twitch] Logged in as \"{self.nick}\"")
        await CFG.async_main()
        await self.run_subroutines()
    
    
    async def event_message(self, message):
        if message.echo:
            return
        msg_str = f"[Twitch] {message.author.display_name}: {message.content}"
        
        print(msg_str.encode("ascii","ignore").decode("ascii","ignore"))
        
        log_task = create_task(self.do_discord_log(message))
        commands_task = create_task(self.handle_commands(message))
        try:
            await log_task
        except:
            print(format_exc())
            notify_admin(f"```{format_exc()}```")
        try:
            await commands_task
        except:
            print(format_exc())
            notify_admin(f"```{format_exc()}```")
    
    
    async def event_command_error(self, ctx, error):
        if type(error) == commands.errors.CommandNotFound:
            await ctx.send("[Not a valid command!]")
            return
        print(f'"{type(error)}"')
        print(f'"{commands.errors.CommandNotFound}"')
        traceback.print_exception(type(error), error, error.__traceback__)
        error_log(f"({type(error)})\n{error}\n{error.__traceback__}")
    
    
    async def do_discord_log(self, message):
        author = message.author.display_name
        author_url = f"https://www.twitch.tv/popout/becomefumocam/viewercard/{author.lower()}"
        author_avatar = "https://brand.twitch.tv/assets/images/black.png"
        message = message.content
        await discord_log(message, author, author_avatar, author_url)
    
    
    async def get_args(self, ctx):
        msg = ctx.message.content
        prefix = ctx.prefix
        command_name = ctx.command.name
        return msg.replace(f"{prefix}{command_name}","",1).strip().split()
    
    
    async def is_dev(self, author):
        return author.name.lower() in Twitch.admins
    
    
    async def run_subroutines(self):
        print("[Twitch] Initializing Subroutines")
        subroutines = [routine_anti_afk, routine_check_better_server, routine_clock, routine_crash_check, routine_help, routine_reboot]
        for subroutine in subroutines:
            print(f"[Routine] Starting subroutine: {subroutine._coro.__name__.replace('routine_','')}")
            subroutine.start()
    
    # Basic Commands
    @commands.command()
    async def click(self, ctx):
        await CFG.add_action_queue(ctx.command.name)
    
    
    @commands.command()
    async def grief(self, ctx):
        await CFG.add_action_queue(ctx.command.name)
    
    
    @commands.command()
    async def jump(self, ctx):
        await CFG.add_action_queue(ctx.command.name)
    
    
    @commands.command()
    async def respawnforce(self, ctx):
        await CFG.add_action_queue(ctx.command.name)
    
    
    @commands.command()
    async def respawn(self, ctx):
        await CFG.add_action_queue(ctx.command.name)
    
    
    @commands.command()
    async def sit(self, ctx):
        await CFG.add_action_queue(ctx.command.name)
    
    
    @commands.command()
    async def use(self, ctx):
        await CFG.add_action_queue(ctx.command.name)
    
    
    # Complex commands/Commands with args
    async def camera_pitch_handler(self, pitch_camera_direction, ctx):
        pitch = 45
        max_pitch = 180
        args = await self.get_args(ctx)
        print(args)
        if args:
            try:
                pitch = float(args[0])
                if max_pitch >= pitch > 0:
                    turn_time = pitch
                else:
                    await ctx.send(f"[{args[0]} is too high/low! Please use an angle between 0 and {max_pitch}.]")
                    return
            except Exception:
                await ctx.send(f"[Error! Invalid number specified.]")
                return
        await CFG.add_action_queue({"pitch_camera_direction": pitch_camera_direction, "pitch_camera_degrees": pitch})
    
        
    # Complex commands/Commands with args
    async def camera_turn_handler(self, turn_camera_direction, ctx):
        turn_time = 45
        max_turn_time = 360
        args = await self.get_args(ctx)
        if args:
            try:
                number = float(args[0])
                if max_turn_time >= number > 0:
                    turn_time = number
                else:
                    await ctx.send(f"[{args[0]} is too high/low! Please use an angle between 0 and 360.]")
                    return
            except Exception:
                await ctx.send(f"[Error! Invalid number specified.]")
                return
        await CFG.add_action_queue({"turn_camera_direction": turn_camera_direction, "turn_camera_time": turn_time})
    
    
    @commands.command()
    async def left(self, ctx):
        turn_camera_direction = "left"
        await self.camera_turn_handler(turn_camera_direction, ctx)
    
    
    @commands.command()
    async def right(self, ctx):
        turn_camera_direction = "right"
        await self.camera_turn_handler(turn_camera_direction, ctx)
        
        
    @commands.command()
    async def up(self, ctx):
        pitch_camera_direction = "up"
        await self.camera_pitch_handler(pitch_camera_direction, ctx)
    
    
    @commands.command()
    async def down(self, ctx):
        pitch_camera_direction = "down"
        await self.camera_pitch_handler(pitch_camera_direction, ctx)
    
    
    @commands.command()
    async def dev(self, ctx):
        args = await self.get_args(ctx)
        if not args:
            await ctx.send(f"[Specify a message, this command is for emergencies! (Please do not misuse it)]")
            return
        msg = " ".join(args)
        notify_admin(f"{ctx.message.author.display_name}: {msg}")
        await ctx.send(f"[Notified dev! As a reminder, this command is only for emergencies. If you were unaware of this and used the command by mistake, please write a message explaining that or you may be timed-out/banned.]")


    @commands.command()
    async def leap(self, ctx):
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
                    await ctx.send(f"[{args[0]} is too high/low! Please use a time between 0 and {max_forward_time}.]")
                    return
            except Exception:
                await ctx.send(f"[Error! Invalid number specified.]")
                return
        if len(args) > 1:
            try:
                number = float(args[1])
                if max_jump_time >= number > 0:
                    jump_time = number
                else:
                    await ctx.send(f"[{args[1]} is too high/low! Please use a time between 0 and {max_jump_time}.]")
                    return
            except Exception:
                await ctx.send(f"[Error! Invalid number specified.]")
                return
        await CFG.add_action_queue({"leap": "leap", "forward_time": forward_time, "jump_time": jump_time, "override": await self.is_dev(ctx.message.author)})

    
    @commands.command()  # Send message in-game
    async def m(self, ctx):
        args = await self.get_args(ctx)
        if not args:
            await ctx.send(f"[Please specify a message! (i.e. \"!m Hello World!\"]")
            return
            
        msg = " ".join(args)
        if len(msg) > 100:
            await ctx.send(f"[In-game character limit is 100! Please shorten your message.]")
            return
        is_dev = await self.is_dev(ctx.message.author)
        action_queue_item = {}
        if msg.startswith("[") or msg.startswith("/w"):  # Whisper functionality
            await ctx.send(f"[You do not have permission to whisper.]")
            return
        elif (msg.startswith("/mute") or msg.startswith("/unmute")):  # Make muting dev-only
            if is_dev:
                action_queue_item = {"chat": [msg]}
            else:
                await ctx.send(f"[You do not have permission to mute/unmute.]")
                return
        elif msg.startswith("/"):
            if msg.startswith("/e"):
                CFG.current_emote = msg
            action_queue_item = {"chat": [msg]}
        elif is_dev:  # Chat with CamDev Tag
            action_queue_item = {"chat_with_name": ["[CamDev]:", msg]}
        else:
            action_queue_item = {"chat_with_name": [f"{ctx.message.author.display_name}:", msg]}
        await CFG.add_action_queue(action_queue_item)
    
    
    @commands.command()
    async def move(self, ctx):
        move_time = 1
        max_move_time = 10
        valid_movement_keys = ["w","a","s","d"]
        args = await self.get_args(ctx)
        if not args or args[0].lower() not in valid_movement_keys:
            await ctx.send(f"[Please specify a valid direction! (i.e. \"!move w\")]")
            return
        move_key = args[0].lower()
        if len(args) > 1:
            try:
                number = float(args[1])
                if max_move_time >= number > 0:
                    move_time = number
                else:
                    await ctx.send(f"[{args[1]} is too high/low! Please use a unit between 0 and {max_move_time}.]")
                    return
            except Exception:
                await ctx.send(f"[Error! Invalid number specified.]")
                return
        await CFG.add_action_queue({"movement": "move", "move_key": move_key, "move_time": move_time, "override": await self.is_dev(ctx.message.author)})

    
    
    @commands.command()
    async def nav(self, ctx):
        args = await self.get_args(ctx)
        valid_locations = ["shrimp"]
        if not args or args[0].lower() not in valid_locations:
            await ctx.send(f"[Please specify a valid location! (i.e. \"!nav shrimp\")]")
            return
        location = args[0].lower()
        await ctx.send(f"[Requested AutoNav! This is experimental, so if it does not work the first time, please re-run the command.]")
        await ctx.send(f"[If we did not respawn at any point, please run !respawnforce (we're stuck!).]")
        await CFG.add_action_queue({"autonav": location})
        
    
    
    @commands.command()
    async def rejoin(self, ctx):
        if await self.is_dev(ctx.author):
            await ctx.send(f"[@{ctx.author.name} Added restart to queue]")
            await CFG.add_action_queue("handle_crash")
        else:
            await ctx.send("[You do not have permission!]")
    
    
    async def zoom_handler(self, zoom_direction, ctx):
        zoom_time = 15
        max_zoom_time = 100
        args = await self.get_args(ctx)
        if args:
            try:
                number = float(args[0])
                if max_zoom_time >= number > 0:
                    zoom_time = number
                else:
                    await ctx.send(f"[{args[0]} is too high/low! Please use a percentage between 0 and {max_zoom_time}.]")
                    return
            except Exception:
                await ctx.send(f"[Error! Invalid number specified.]")
                return
        await CFG.add_action_queue({"zoom_camera_direction": zoom_direction, "zoom_camera_time": zoom_time})
    
    
    @commands.command()
    async def zoomin(self, ctx):
        zoom_direction = "i"
        await self.zoom_handler(zoom_direction, ctx)


    @commands.command()
    async def zoomout(self, ctx):
        zoom_direction = "o"
        await self.zoom_handler(zoom_direction, ctx)
    
    
@routines.routine(minutes=10, wait_first=True)
async def routine_anti_afk():
    print("[Subroutine] AntiAFK")
    try:
        await CFG.add_action_queue("anti-afk")
        CFG.anti_afk_runs += 1 
        if CFG.anti_afk_runs % 3 == 0:
            await CFG.add_action_queue("advert")
            print("[Subroutine] Queued Advert")
            CFG.anti_afk_runs = 0
    except:
        error_log(traceback.format_exc())

@routines.routine(minutes=5)
async def routine_check_better_server():
    print("[Subroutine] Better Server Check")
    try:
        while CFG.crashed:
            print("[Better Server Check] Currently crashed, waiting...")    
            await async_sleep(60)
        await CFG.add_action_queue("check_for_better_server")
    except:
        error_log(traceback.format_exc())


@routines.routine(seconds=1, wait_first=True)
async def routine_clock():
    current_time = strftime("%I:%M:%S%p EST")
    days_since_creation = floor((time()-CFG.epoch_time)/(60*60*24))
    output_log("clock", f"Day {days_since_creation}\n{current_time}")


@routines.routine(time=datetime(year=1970,month=1,day=1,hour=3,minute=58))
async def routine_reboot():
    action_queue_item = {"chat": ["[System restart in 2 minutes]"]}
    await CFG.add_action_queue(action_queue_item)
    await async_sleep(60)
    
    action_queue_item = {"chat": ["[System restart in 1 minute]"]}
    await CFG.add_action_queue(action_queue_item)
    await async_sleep(60)
    
    log_process("System Shutdown")
    log("Initiating shutdown sequence")
    action_queue_item = {"chat": ["[System restarting]"]}
    await CFG.add_action_queue(action_queue_item)
    await async_sleep(10)
    os.system("shutdown /f /r /t 0")
 

@routines.routine(seconds=5, wait_first=True)
async def routine_crash_check():
    if CFG.crashed:
        return
    print("[Subroutine] Crash Check")
    try:
        crashed = await do_crash_check()
        if crashed:
            print("[Routine] Crash detected") 
            await CFG.add_action_queue("handle_crash")
            await async_sleep(60)
    except:
        error_log(traceback.format_exc())


@routines.routine(seconds=5)
async def routine_help():
    for command in CFG.commands_list:
        output_log("commands_help_label", "")
        output_log("commands_help_title", "")
        output_log("commands_help_desc", "")

        await async_sleep(0.25)
        current_command_in_list = f"{(CFG.commands_list.index(command) + 1)}/{len(CFG.commands_list)}"
        output_log("commands_help_label", f"TWITCH CHAT COMMANDS [{current_command_in_list}]")
        output_log("commands_help_title", command["command"])
        await async_sleep(0.1)
        output_log("commands_help_desc", command["help"])
        if "time" in command:
            await async_sleep(int(command["time"]))
            continue
        await async_sleep(5)


def twitch_main():
    token = os.getenv("TWITCH_BOT_TOKEN")
    channel = Twitch.channel_name
    bot = TwitchBot(token, channel)
    bot.run()


if __name__ == "__main__":  # Not supposed to run directly, but can be
    twitch_main()