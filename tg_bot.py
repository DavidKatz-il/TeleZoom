import json
import requests


class TelegramBot:
    """
    Telegram bot class
    """

    def __init__(self, token: str):
        """
        Initialize the class.
        :param token: telegram bot token, given by BotFather.
        """
        self.base_url = "https://api.telegram.org/bot"
        self.token = token
        self.updates = None
        self.last_id = None

    def get_updates(self):
        """
        stores new incoming updates.
        """
        url = self.base_url + self.token + "/getUpdates"
        if self.last_id:
            url = f"{url}?offset={self.last_id}"
        self.updates = requests.get(url).json()["result"]
        self.set_last_id()

    def set_last_id(self):
        """
        set the current last update_id.
        """
        if len(self.updates) > 0:
            self.last_id = self.updates[-1]["update_id"] + 1

    def send_message(self, chat_id: int, text: str):
        """
        Sends a message to a telegram user.
        :param chat_id: Unique identifier user_id / user_name / chat_id
        :param text: Text of the message to be sent
        """
        url = self.base_url + self.token + "/sendMessage"
        params = {"chat_id": int(chat_id), "text": text}
        requests.get(url, params=params)

    def send_video(self, chat_id: int, video):
        """
        Sends a video to a telegram user.
        :param chat_id: Unique identifier user_id / user_name / chat_id
        :param video: video file to be sent
        """
        url = self.base_url + self.token + "/sendVideo"
        data = {"chat_id": int(chat_id)}
        files = {"video": video}
        requests.post(url, data=data, files=files)

    def request_contact(self, chat_id: int, text: str = "Your Contact:"):
        """
        Asking the user to give back is phone number.
        :param chat_id: Unique identifier user_id / user_name / chat_id
        :param text: Text of the message to be sent
        """
        reply_markup = {
            "keyboard": [[{"text": "Press Me", "request_contact": True}]],
            "one_time_keyboard": True,
            "resize_keyboard": True,
        }

        url = self.base_url + self.token + "/sendMessage"
        params = {
            "chat_id": chat_id,
            "text": text,
            "reply_markup": json.dumps(reply_markup),
        }
        requests.get(url, params=params)
