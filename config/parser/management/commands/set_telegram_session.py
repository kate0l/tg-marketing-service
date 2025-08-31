"""
Custom action for "parser" application.
This action creates and stores in .env a TelegramClient StringSession.
StringSession is a serialized TelegramClient session, essentially a session.

Prerequisites:
- Telegram account with registered app
- Connection to the internet

How to:
    uv run python manage.py set_telegram_session

Variables:
    ENV_SESSION_KEY = TelegramClient Session key name in .env
    ENV_API_ID_KEY = Telegram app api_id key name in .env
    ENV_API_HASH_KEY = Telegram app api_hash key name in .env
    ENV_PHONE_KEY = Telegram account phone key name in .env
    ENV_PASSWORD_KEY = Telegram account password key name in .env

P.S.:
    This class can be used at any time and does not require starting up anything
"""

from pathlib import Path
from operator import itemgetter
from dotenv import load_dotenv, find_dotenv, set_key
from django.core.management.base import BaseCommand, CommandError, CommandParser
from telethon import TelegramClient
from telethon.sessions import StringSession

ENV_SESSION_KEY = 'TELEGRAM_SESSION'
ENV_API_ID_KEY = 'TELEGRAM_API_ID'
ENV_API_HASH_KEY = 'TELEGRAM_API_HASH'
ENV_PHONE_KEY = 'TELEGRAM_PHONE'
ENV_PASSWORD_KEY = 'TELEGRAM_PASSWORD'
ENV_PATH = '/'


class Command(BaseCommand):
    """Django management (manage.py) command to generate and 
    save to .env a TelegramClient StringSession

    Prerequisites:
    - .env and provided data that in total is enough for starting TelegramClient
    - User (or workaround) who will paste code, 
    which will be sent to a Telegram account, which waas registered with the  passed phone

    Features:
    - Provided data can be automatically be loaded from .env,
    if not passed via cli (cli is prioritised)
    - Raises CommandError
    - Safely disconnects from the client after successfull set of TelegramClient StringSession

    How to and when:
    1. uv run python manage.py set_telegram_session
    when: when everything is present in .env or user will provide data via cli in same terminal
    2. uv run python manage.py set_telegram_session --force
    when: StringSession is in .env, but want to regenerate it with data in .env
    3. uv run python manage.py set_telegram_session --string-session <value>
    when: set new StringSession
    4. uv run python manage.py set_telegram_session --api-id 123 --api-hash 123abc
    when: use passed data and what data is not passed should be loaded from .env
    4. uv run python manage.py set_telegram_session --api-id 123 --api-hash 123abc --phone +71235456789
    when: use passed data and what data is not passed should be loaded from .env
    5. uv run python manage.py set_telegram_session chilling
    when: u r tired and want to receive argparse.ArgumentError
    """

    def __init__(self, *args, **kwargs):
        """Initialize command state:
        1. init super (required for backward compatibility with BaseCommand)
        2. create fields
        """

        super().__init__(*args, **kwargs):
        self.string_session = None
        self.api_id = None
        self.api_hash = None
        self.phone = None
        self.env_path = None
    
    # argparse arguments
    def add_arguments(self, parser: CommandParser) -> None:
        """Define CLI options

        Options:
        - --force: to regenerate StringSession even if it is already in .env
        - --string-session: provide StringSession and set it in .env for future use (override)
        - --api-id: override TELEGRAM_API_ID in .env
        - --api-hash: override TELEGRAM_API_HAS in .env
        - --phone: override PHONE in .env
        - --env-path: override path to .env
        """
        parser.add_argument(
            '--force',
            action='store_true',
            help='Regenerate Telegram StringSession'
        )
        parser.add_argument(
            '--string-session',
            dest='string_session',
            type=str,
            help='Set this string as a Telegram StringSession'
        )
        parser.add_argument(
            '--api-id',
            dest='api_id',
            type=str,
            help=f'Override {ENV_API_ID_KEY}'
        )
        parser.add_argument(
            '--api-hash',
            dest='api_hash',
            type=str,
            help=f'Override {ENV_API_HASH_KEY}'
        )
        parser.add_argument(
            '--phone',
            dest='phone',
            type=str,
            help=f'Override {ENV_PHONE_KEY}'
        )
        parser.add_argument(
            '--env-path',
            dest='env_path',
            type=str,
            help='Set this string as a path to .env'
        )
        # is it needed?
        # return super().add_arguments(parser)

        # **options instead of **kwargs because of legacy
    def handle(self, *args, **options) -> None:
        """Entrypoint: resolve input, authenticate in Telegram, save it

        Structure:
        - Resolve .env path
        - If --string-session is provided, set it in TELEGRAM_STRING_SESSION
        - If --string-session is not provided, generate it on provided and
        existing in .env data (provided is prioritised)
        - If type of provided data already exists in .env,
        then ask for overwrite permission (default is yes)
        - Run Telethon authentication in cli and generate StringSession
        - Set StringSession in .env

        Check of arguments:
        - if argument was provided in command
        - then validate it
        -- if validation is passed, set it in .env
        - else use what is present in .env

        Raises:
            PermissionError: permission denied to .env file error
            OSError: error while writing to .env
            CommandError: other errors
        """
        # get all key (option) arguments. cool, huh?
        force, string_session, api_id, api_hash, phone, env_path = \
            itemgetter('force', 'string_session', 'api_id', \
                        'api_hash', 'phone', 'env_path')(options)

            
        if env_path:
            env_file = Path(ENV_PATH) / '.env'
            if env_file.is_file():
                self.env_path = env_path
        else:
            try:
                self.env_path = find_dotenv(raise_error_if_not_found=True, usecws=True)
            except FileNotFoundError as e:
                raise CommandError(f'.env was not found: {e}') from e


        if force :
