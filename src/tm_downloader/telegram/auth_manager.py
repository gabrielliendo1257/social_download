import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

load_dotenv()

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
tg_session_name = os.getenv("TG_SESSION")
session_dir = os.getenv("TG_SESSION_DIR")

if (
    api_id is None
    and api_hash is None
    and tg_session_name is None
    and session_dir is None
):
    raise Exception("Not fount variables")

tg_session_dir = Path.home() / Path(str(session_dir))
tg_session_dir.mkdir(parents=True, exist_ok=True)


class AuthManager:

    def __init__(self) -> None:
        self.__client = None

    async def authentorize(self):
        if not isinstance(self.__client, TelegramClient):
            raise Exception("Client is None")
        is_authorized = await self.__client.is_user_authorized()
        logging.info(f"Is authorized: {str(is_authorized)}")
        return is_authorized

    async def connecting(self) -> TelegramClient | None:
        try:
            self.__client = TelegramClient(
                session=tg_session_dir / Path(str(tg_session_name)),
                api_id=int(api_id),
                api_hash=str(api_hash),
            )
            await self.__client.connect()
            is_authenticated = await self.authentorize()

            if not is_authenticated:
                phone = input("Enter phone number: ")
                await self.__client.send_code_request(phone)
                code = input("Enter code: ")

                try:
                    await self.__client.sign_in(phone=phone, code=code)
                except SessionPasswordNeededError as ex:
                    password = input("Enter 2fa code: ")
                    await self.__client.sign_in(password=password)

            return self.__client
        except Exception as ex:
            if not isinstance(self.__client, TelegramClient):
                raise Exception("Client is None")
            self.__client.disconnect()
            logging.exception(ex)
            logging.error(ex)

            return None
