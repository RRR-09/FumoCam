import irc.bot
from commands import *


class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, username, client_id, token, channel):
        self.client_id = client_id
        self.token = token
        self.channel = '#' + channel

        # Get the channel id, we will need this for v5 API calls
        url = f"https://api.twitch.tv/kraken/users?login={channel}"
        headers = {"Client-ID": client_id, "Accept": "application/vnd.twitchtv.v5+json",
                   "Authorization": f"oauth:{token}"}
        r = requests.get(url, headers=headers).json()
        self.channel_id = r["users"][0]["_id"]

        # Create IRC bot connection
        server = "irc.chat.twitch.tv"
        port = 6667
        print(f"Connecting to {server} on port {port}...")
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, f"oauth:{token}")], username, username)

    def on_welcome(self, c, _):
        print('Joining ' + self.channel)
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)
        print('Joined ' + self.channel)

    def on_pubmsg(self, _, e):
        author = "Twitch"
        for tag in e.tags:
            if tag["key"] == "display-name":
                author = tag["value"]
        author = author[:13]
        author_url = f"https://www.twitch.tv/{author.lower()}"
        author_avatar = "https://brand.twitch.tv/assets/images/black.png"
        message = e.arguments[0]
        discord_log(message, author, author_avatar, author_url)
        # If a chat message starts with an exclamation point, try to run it as a command
        if message[:1] == '!':
            original_cmd = message.split(" ")
            cmd = original_cmd[0].replace("!", "")
            args = original_cmd[1:]
            print(f"Received command: {cmd}")
            self.do_command(e, cmd, args, author)
        return

    @staticmethod
    def do_command(_, cmd, args, author):
        is_dev = author.lower() in Twitch.admins
        is_owner = author.lower() == "scary08rblx"
        if cmd == "rejoin" and is_dev:
            CFG.action_queue.append("handle_crash")
        elif (cmd == "handle_join_new_server" or cmd == "handle_crash") and is_dev:
            CFG.action_queue.append(cmd)
        elif cmd == "zoomin" or cmd == "zoomout":
            zoom_direction = "i" if cmd == "zoomin" else "o"
            zoom_time = 0.05
            try:
                number = float(args[0])
                if number <= 1:
                    zoom_time = number
            except Exception:
                pass
            CFG.action_queue.append({"zoom_camera_direction": zoom_direction, "zoom_camera_time": zoom_time})
        elif cmd == "left" or cmd == "right":
            turn_time = 0.1
            try:
                number = float(args[0])
                if number <= 2:
                    turn_time = number
            except Exception:
                pass
            CFG.action_queue.append({"turn_camera_direction": cmd, "turn_camera_time": turn_time})
        elif cmd == "move":
            move_time = 1
            try:
                number = float(args[1])
                if 5 >= number > 0:
                    move_time = number
            except Exception:
                pass
            try:
                CFG.action_queue.append({"movement": cmd, "move_key": args[0], "move_time": move_time, "override": is_dev})
            except Exception:
                log_process("Manual Movement")
                log("Command invalid! Check you're typing it right.")
                sleep(3)
        elif cmd == "leap":
            forward_time = 0.4
            jump_time = 0.3
            try:
                number = float(args[0])
                if 1 >= number > 0:
                    forward_time = number
            except Exception:
                pass
            try:
                number = float(args[1])
                if 1 >= number > 0:
                    jump_time = number
            except Exception:
                pass
            try:
                CFG.action_queue.append({"leap": cmd, "forward_time": forward_time, "jump_time": jump_time, "override": is_dev})
            except Exception:
                log_process("Leap")
                log("Command invalid! Check you're typing it right.")
        elif cmd == "dev":
            log("Sending warning to dev...")
            msg = " ".join(args)
            notify_admin(f"{author}: {msg}")
            sleep(5)
            log("")
        elif cmd == "click":
            CFG.action_queue.append("click")
        elif cmd == "sit":
            CFG.action_queue.append("sit")
        elif cmd == "use":
            CFG.action_queue.append("use")
        elif cmd == "grief":
            CFG.action_queue.append("grief")
        elif cmd == "respawn":
            CFG.action_queue.append("respawn")
        elif cmd == "jump":
            CFG.action_queue.append("jump")
        elif cmd == "m":
            msg = " ".join(args)
            if msg.startswith("[") or msg.startswith("/w"):  # Whisper functionality
                return
            elif (msg.startswith("/mute") or msg.startswith("/unmute")) and is_dev:  # Make muting dev-only
                CFG.action_queue.append({"chat": [msg]})
            elif msg.startswith("/"):
                if msg.startswith("/e"):
                    CFG.current_emote = msg
                CFG.action_queue.append({"chat": [msg]})
            elif is_dev:  # Chat with CamDev Tag
                print({"chat_with_name": ["[CamDev]:", msg]})
                CFG.action_queue.append({"chat_with_name": ["[CamDev]:", msg]})
            elif is_owner:  # Chat with BecomeFumo Owner Tag
                CFG.action_queue.append({"chat_with_name": ["[BecomeFumoDev Scary08]:", msg]})
            else:
                CFG.action_queue.append({"chat_with_name": [f"{author}:", msg]})


def twitch_main():
    username = Twitch.username
    client_id = os.getenv("TWITCH_CLIENT_ID")
    token = os.getenv("TWITCH_MAIN_OAUTH")
    channel = Twitch.channel_name
    bot = TwitchBot(username, client_id, token, channel)
    bot.start()

if __name__ == "__main__":
    twitch_main()