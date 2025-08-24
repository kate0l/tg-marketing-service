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
from dotenv import load_dotenv, find_dotenv, set_key
from django.core.management.base import BaseCommand
from telethon import TelegramClient
from telethon.sessions import StringSession

class Command(BaseCommand):
    '''Command for generating a Telethon session string.

    Attributes:
        sessions_string: Placeholder for the generated serialized
            Telethon StringSession.
    '''

    # What appears under: python3 manage.py help set_telegram_session
    help = 'This command is run to set \
        TELEGRAM_SESSION_STRING in .env'

    def __init__(self):
        self.session_string = None

    def handle(self, session_name: str='session'):
        '''Entry point for the management command (all need handle method)

        Loads environment variables and prepares credentials used by
        Telethon for authentication.

        Args:
            session_name (str): Optional session name passed to the command.
                it should be loaded from .env TELEGRAM_SESSION_NAME.
                Defaults to 'session'.

        Side Effects:
            Reads variables from a .env file via python-dotenv.
        '''
        load_dotenv()

        self.session_name = os.getenv('TELEGRAM_SESSIONS_ENV') or session_name
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.phone = os.getenv('PHONE')
        self.get_session_string()
        self.set_session_string()

        # Why async:
        # Telethon client.start is awaitable operation.
    async def get_session_string(self):
        '''Authenticate with Telegram and get the StringSession.

        Starts a Telethon client session and saves its serialized
        session string on the command instance.

        Returns:
            None

        Raises:
            telethon.errors.rpcerrorlist.PhoneCodeInvalidError: If the
                login code is invalid.
            RuntimeError: If the client fails to start.

        Notes:
            Defined inside `handle` to keep scope-local helpers private
            to the command run.
        '''
        client = TelegramClient(self.session_name, self.api_id, self.api_hash)
        await client.start(phone=self.phone)
        self.session_string = StringSession.save(client.session)
        await client.disconnect()

    # After obtaining the Telegram session string, it is set to .env
    def set_session_string(self):
        dotenv_path = find_dotenv(raise_error_if_not_found=True, usecwd=True)
        set_key(dotenv_path, 'TELEGRAM_SESSION_STRING', self.session_string)
