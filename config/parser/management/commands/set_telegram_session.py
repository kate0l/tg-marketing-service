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

from typing import Optional, Callable, TypeVar, Any
from pathlib import Path
from operator import itemgetter
from os import getenv
from dotenv import load_dotenv, find_dotenv, set_key
from django.core.management.base import BaseCommand, CommandError, CommandParser
from telethon import TelegramClient
from telethon.sessions import StringSession

ENV_STRING_SESSION_KEY = 'TELEGRAM_SESSION'
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

        super().__init__(*args, **kwargs)
        # I didnt know about this so added it
        self.string_session: Optional[str] = None
        self.api_id: Optional[int] = None
        self.api_hash: Optional[str] = None
        self.phone: Optional[str] = None
        self.env_path: Optional[str] = None

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
            type=int,  # ensure int at parse time
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
    def handle(self, *args, **options: dict[str, str]) -> None:
        """Entrypoint: resolve input, authenticate in Telegram, save it

        Structure:
        - Resolve .env path
        - If --string-session is provided, set it in TELEGRAM_STRING_SESSION
        - If --string-session is not provided, generate it on provided and
        existing in .env data
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

        # Fix env path resolution
        if env_path:
            p = Path(env_path)
            env_file = p if p.suffix == '.env' else (p / '.env')
            if not env_file.is_file():
                raise CommandError(f'.env was not found at: {env_file}')
            self.env_path = str(env_file)
        else:
            try:
                # fix: usecwd (not usecws)
                self.env_path = find_dotenv(raise_error_if_not_found=True, usecwd=True)
            except Exception as e:
                raise CommandError(f'.env was not found: {e}') from e

        load_dotenv(self.env_path)

        # check if provided data present in .env and ask if want to replace data in .env
        # there are no ' ' spaces in any data, so safely remove it to fix typos
        self.replace_env_data('string_session', ENV_STRING_SESSION_KEY, string_session, str, force)
        self.replace_env_data('api_id', ENV_API_ID_KEY, api_id, int, force)
        self.replace_env_data('api_hash', ENV_API_HASH_KEY, api_hash, str, force)
        self.replace_env_data('phone', ENV_PHONE_KEY, phone, str, force)

        # If --string-session provided, just save it and exit
        if string_session:
            self.string_session = string_session  # ensure it is used by set_string_session
            self.set_string_session(ENV_STRING_SESSION_KEY)
            return

        # If session already exists and no --force, do nothing
        if getenv(ENV_STRING_SESSION_KEY) and not force:
            self.stdout.write('TELEGRAM_SESSION already present. Use --force to regenerate.')
            return

        # Generate a new StringSession (requires api_id, api_hash, phone)
        missing = [name for name, val in [('api_id', self.api_id), ('api_hash', self.api_hash), ('phone', self.phone)] if not val]
        if missing:
            raise CommandError(f'Missing required data: {", ".join(missing)}')

        import asyncio
        asyncio.run(self.get_string_session())
        self.set_string_session(ENV_STRING_SESSION_KEY)

    def replace_env_data(self, att_name: str, env_key: str, value: Any, to_type: Callable[[Any], Any] = str, force: bool=False, remove_whitespace: bool=True) -> None:
        # Normalize incoming value (CLI value)
        if isinstance(value, str) and remove_whitespace:
            value = value.replace(' ', '')

        # If no CLI value, use env and stop
        if value is None or (isinstance(value, str) and value == ''):
            setattr(self, att_name, getenv(env_key))
            return

        # Convert provided value
        try:
            converted = value if isinstance(value, to_type) else to_type(value)
        except Exception as e:
            raise CommandError(f'Error while converting {value} of {type(value)} to {to_type}: {e}') from e

        # If env already has a value, confirm replacement unless --force
        if getenv(env_key) and not force:
            answer = input(f'{env_key} is present. Do you want to replace it? [y/N] ').strip().lower()
            if answer != 'y':
                setattr(self, att_name, getenv(env_key))
                return

        # Use provided/converted value
        setattr(self, att_name, converted)


    async def get_string_session(self) -> None:
        '''Authentucate in TelegramClient and save StringSession in self.string_session

        Raises:
            OSError: if disconnect error occurs
            CommandError: other errors
        '''
        try:
            client = TelegramClient(StringSession(), self.api_id, self.api_hash)
        except ValueError as e:
            raise CommandError(f'api_id, api_hash and phone are required to generate StringSession: {e}') from e
        try:
            await client.start(phone=self.phone, password=getenv(ENV_PASSWORD_KEY))
            self.string_session = client.session.save()
        except Exception as e:
            raise CommandError(f'Failed to generate StringSession: {e}') from e
        finally:
            try:
                await client.disconnect()
            except Exception as e:
                raise OSError(f'Error while disconnecting TelegramClient: {e}') from e

    def set_string_session(self, string_session_key: str) -> None:
        '''Set thee generated StringSession in .env

        Args:
            string_session_key: 
        '''
        try:
            set_key(self.env_path, string_session_key, self.string_session)
        except ValueError as e:
            raise CommandError(f' Not enough data provided for generating StringSession: {e}') from e
        except PermissionError as e:
            raise
        except OSError as e:
            raise