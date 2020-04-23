from tg_bot import TelegramBot
import requests
import re
import os


class TeleZoomBot(TelegramBot):
    """
    TeleZoom bot class
    """

    def __init__(self, token: str):
        """
        Initialize the class.
        :param token: telegram bot token, given by BotFather.
        """
        super().__init__(token)
        self.msg = "Please send me 'url password' (password is optimal)."
        self.start_msg = (
            "Welcome to TeleZoom.\n"
            "Downloading recording videos from zoom.us/rec/.\n" + self.msg
        )

    def handle_updates(self):
        """
        Handling new incoming massages.
        """
        for update in self.updates:
            print(f"update: {update}")
            try:
                info = update["message"]["from"]
                text = update["message"].get("text", "")

                if text == "/start":
                    self.send_message(info["id"], self.start_msg)
                    continue
                if "zoom.us/rec/" not in text:
                    self.send_message(
                        info["id"], "Downloading only from 'zoom.us/rec/'"
                    )
                    continue

                url_password = text.split(" ")
                if len(url_password) > 2:
                    self.send_message(info["id"], self.msg)
                    continue
                elif len(url_password) == 2:
                    url, password = url_password[0], url_password[1]
                else:
                    url, password = url_password[0], None

                self.handle_zoom_link(info["id"], url, password)
            except Exception as e:
                print(f"Exception: {e}")
                continue

    def handle_zoom_link(self, chat_id: int, url: str, password: str = None):
        """
        Handle an request to download video from 'zoom.us/rec'
        :param chat_id: Unique identifier to send massage / video
        :param url: The link to zoom recording video.
        :param password: The password of the zoom recording video (optional).
        """
        session = requests.session()
        page = session.get(url)
        if password:
            m = re.search(r'(\w*)(<input type="hidden" id="meetId")(.*)(/>)', page.text)
            meet_id = m.group(3).strip().split("=")[1].replace('"', "")

            session.post(
                "https://epfl.zoom.us/rec/validate_meet_passwd",
                data={"id": meet_id, "passwd": password, "action": "viewdetailpage"},
            )
            session.headers.update({"referer": "https://epfl.zoom.us/"})
            page = session.get(url)

        url_list = re.compile('https.*ssrweb.zoom.us[^"]*').search(page.text)
        if url_list:
            video_url = url_list[0]
            video_name, extension = video_url.split("?")[0].split("/")[-1].split(".")
            res = session.head(video_url,)
            if int(res.headers["content-length"]) >= (50 * 1024):
                self.send_message(
                    chat_id,
                    "The Video is more then 50 MB.\n"
                    "Bots can currently send video files of up to 50 MB in size.",
                )
                return

            self.send_message(chat_id, "Start Downloading...")
            vid = session.get(video_url, cookies=session.cookies, stream=True)
            if vid.status_code == 200:
                file = f"{video_name}.{extension}"
                with open(file, "wb") as f:
                    for chunk in vid:
                        self.send_message(chat_id, str(chunk))
                        f.write(chunk)
                self.send_video(chat_id, open(file, "rb"))
                os.remove(file)
            else:
                self.send_message(chat_id, "Try again later.")
        else:
            self.send_message(chat_id, self.msg)


def main():
    token = ""
    bot = TeleZoomBot(token)

    while True:
        bot.get_updates()
        bot.handle_updates()


if __name__ == "__main__":
    main()
