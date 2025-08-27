'''
management.py command to create and store a Telegram StringSession:
1) initializes a Telethon client using credentials in .env
2) obtains a Telegram session string.

How to:
    uv run python3 manage.py set_sessiong_string

.env Variables:
    TELEGRAM_SESSIONS_ENV: Optional session file/name (default: 'session').
    TELEGRAM_API_ID: Telegram API ID.
    TELEGRAM_API_HASH: Telegram API hash.
    PHONE: Phone number used for sign-in (with country code, like +7).

Location note:
    Django discovers management commands from each app's
    management/commands/ directory.
'''

import os
import asyncio
import logging
from dotenv import load_dotenv, find_dotenv, set_key
from django.core.management.base import BaseCommand, CommandError
from telethon import TelegramClient
from telethon.sessions import StringSession

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    '''Command for generating a Telethon session string.

    Attributes:
        session_string (str) : Placeholder for the generated serialized
            Telethon StringSession.
    '''

    # What appears for python3 manage.py help set_telegram_session
    help = 'This command is run to set \
        TELEGRAM_SESSION_STRING in .env'

    def __init__(self):
        super().__init__()  # init BaseCommand init commands
        self.session_string = None  # then do our stuff

    def handle(self, session_name_value: str='session', session_name: str='TELEGRAM_SESSION_ENV', api_id: str='TELEGRAM_API_ID', api_hash: str='TELEGRAM_API_HASH', phone: str='PHONE', *args, **kwargs) -> None:
        '''Entry point for the management command (all need handle method)

        Loads environment variables and prepares credentials used by
        Telethon for authentication.

        Args:
            session_name (str): Optional session name passed to the command.
                it should be loaded from .env TELEGRAM_SESSION_NAME.
                Defaults to 'session'.
            *args, **kwargs: Optional args, kept for compatibility.

        Side Effects:
            Reads variables from a .env file via python-dotenv.
        '''
        load_dotenv()

        # all .env values are str
        self.session_name = os.getenv(session_name) or session_name_value
        # api_id should be passed to Telegram as int
        self.api_id = int(os.getenv(api_id))
        self.api_hash = os.getenv(api_hash)
        self.phone = os.getenv(phone)
        # need to run in an event loop, to make it run coroutine
        asyncio.run(self.get_session_string())
        self._set_session_string()

        # Why async: Telethon client.start is awaitable operation.
    async def get_session_string(self) -> None:
        '''Authenticate with Telegram and get the StringSession.

        Starts a Telethon client session and saves its serialized
        session string on the command instance.

        Returns:
            None

        Raises:
            telethon.errors.rpcerrorlist.PhoneCodeInvalidError: If the
                login code is invalid.
            RuntimeError: If the client fails to start.
        '''
        # c.disconnect is handled via with
        async with TelegramClient(self.session_name, self.api_id, self.api_hash) as c:
            await c.start(phone=self.phone)
            self.session_string = StringSession.save(c.session)

    def _set_session_string(self) -> None:
        '''Load the Telegram StringSession into the .env file.

        Locates the nearest .env using python-dotenv (searching from the
        current working directory) and writes/updates the
        TELEGRAM_SESSION_STRING key with the value previously produced by
        get_session_string().
        '''
        try:
            dotenv_path = find_dotenv(raise_error_if_not_found=True, usecwd=True)
        except PermissionError as e:
            logger.exception("Permission denied writing TELEGRAM_SESSION_STRING to .env")
            raise CommandError("Permission denied writing to .env") from e
        except OSError as e:
            logger.exception("OS error while writing TELEGRAM_SESSION_STRING to .env")
            raise CommandError(f"OS error while writing .env: {e}") from e
        try:
            set_key(dotenv_path, 'TELEGRAM_SESSION_STRING', self.session_string)
            logger.info("Saved TELEGRAM_SESSION_STRING to %s", dotenv_path)
        except TypeError as e:
            logger.exception("Wrong type of TELEGRAM_SESSION_STRING to .env")
            raise CommandError(f"Wrong type of TELEGRAM_SESSION_STRING to .env: {e}")
        except PermissionError as e:
            logger.exception("Permission denied writing TELEGRAM_SESSION_STRING to .env")
            raise CommandError("Permission denied writing to .env") from e
        except OSError as e:
            logger.exception("OS error while writing TELEGRAM_SESSION_STRING to .env")
            raise CommandError(f"OS error while writing .env: {e}") from e
