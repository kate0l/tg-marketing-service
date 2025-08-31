'''
management.py command to create and store a Telegram StringSession:
1) initializes a Telethon client using credentials in .env
2) obtains a Telegram session string.

How to:
    uv run python3 manage.py set_telegram_session

.env Variables:
    TELEGRAM_SESSION_STRING (str): Telegram client serialized session string.
    TELEGRAM_API_ID (str): Telegram API ID.
    TELEGRAM_API_HASH (str): Telegram API hash.
    PHONE (str): Phone number used for sign-in (with country code, like +7).

Location note:
    Django discovers management commands from each app's
    management/commands/ directory.
'''

import os
import sys
import asyncio
import logging
from typing import Optional
from operator import itemgetter

from dotenv import load_dotenv, find_dotenv, set_key
from django.core.management.base import BaseCommand, CommandError, CommandParser
from telethon import TelegramClient
from telethon.sessions import StringSession

logger = logging.getLogger(__name__)

# names of keys in .env
ENV_SESSION_KEY = 'TELEGRAM_SESSION_STRING'
ENV_API_ID_KEY = 'TELEGRAM_API_ID'
ENV_API_HASH_KEY = 'TELEGRAM_API_HASH'
ENV_PHONE_KEY = 'PHONE'
ENV_PASSWORD_KEY = 'TELEGRAM_PASSWORD'


class Command(BaseCommand):
    '''Django management command to generate or store a Telethon StringSession.

    Features:
    - Loads API credentials from CLI options or .env.
    - Starts an interactive Telethon login flow and produces a serialized session.
    - Saves the resulting session string into the selected .env file.

    Usage examples:
        uv run python manage.py set_telegram_session
        uv run python manage.py set_telegram_session --force
        uv run python manage.py set_telegram_session --string-session <value>
        uv run python manage.py set_telegram_session --api-id 123 --api-hash abc --phone +70000000000
    '''

    def __init__(self, *args, **kwargs):
        '''Initialize command state and placeholders for runtime values.'''
        super().__init__(*args, **kwargs)
        # self.attr: Type = value
        self.string_session = None
        self.api_id = None
        self.api_hash = None
        self.phone = None
        self.env_path = None

    def add_arguments(self, parser: CommandParser) -> None:
        '''Define CLI options for the management command.

        Options:
        - --force: overwrite existing TELEGRAM_SESSION_STRING without prompt.
        - --string-session: provide a ready session string to store into .env.
        - --api-id: override TELEGRAM_API_ID for this run.
        - --api-hash: override TELEGRAM_API_HASH for this run.
        - --phone: override PHONE (login phone) for this run.
        - --env-path: explicit path to target .env file (defaults to nearest).
        '''
        parser.add_argument(
            '--force',
            action='store_true',
            help='Regenerate the session without prompt if oit already exists'
        )
        parser.add_argument(
            '--string-session',
            dest='string_session',
            type=str,
            help='Provide an already generated Telegram StringSession to store'
        )
        parser.add_argument(
            '--api-id',
            dest='api_id',
            type=str,
            help=f'Override {ENV_API_ID_KEY} value'
        )
        parser.add_argument(
            '--api-hash',
            dest='api_hash',
            type=str,
            help=f'Override {ENV_API_HASH_KEY} value'
        )
        parser.add_argument(
            '--phone',
            dest='phone',
            type=str,
            help=f'Override {ENV_PHONE_KEY} value'
        )
        parser.add_argument(
            '--env-path',
            dest='env_path',
            type=str,
            help='Path to .env file (defaults to the nearest .env in CWD tree)'
        )
        # return super().add_arguments(parser)

    def handle(self, *args, **options) -> None:
        '''Main entrypoint: resolve inputs, authenticate, and persist the session.

        Flow:
        1) Resolve .env path (explicit or nearest).
        2) If --string-session provided: validate and store it, possibly asking to overwrite.
        3) Otherwise, read/override API credentials and phone.
        4) Confirm overwrite if TELEGRAM_SESSION_STRING already exists (unless --force).
        5) Run interactive Telethon auth and generate a StringSession.
        6) Store TELEGRAM_SESSION_STRING in the chosen .env file.

        Raises:
            CommandError: for any validation or runtime error requiring user action.
        '''
        '''Get all option values possible
        If not present and not passed, than raise CommandError
        '''
        # get all key args from command
        env_path_opt, string_session_opt, api_id_opt, api_hash_opt, phone_opt, force = itemgetter(
            'env_path', 'string_session', 'api_id', 'api_hash', 'phone', 'force'
        )(options)

        # set .env path
        if env_path_opt:
            if not os.path.isfile(env_path_opt):
                raise CommandError(f'.env file not found at: {env_path_opt}')
            self.env_path = env_path_opt
        else:
            try:
                self.env_path = find_dotenv(raise_error_if_not_found=True, usecwd=True)
            except Exception as e:
                raise CommandError(f'Could not locate .env file from current directory: {e}') from e

        load_dotenv(self.env_path)
        
        

        
        !!!


        # if --string-session provided, just store it
        if string_session_opt:
            # to prevent typos with spaces, newlines etc
            self.string_session = string_session_opt.strip()
            if not self.string_session:
                raise CommandError('--string-session is empty')
            self._confirm_overwrite_if_exists(force)
            self._set_session_string(ENV_SESSION_KEY)
            self.stdout.write(self.style.SUCCESS('Saved provided Telegram StringSession to .env'))
            return

        # Gather credentials with precedence: CLI > .env
        api_id = api_id_opt or os.getenv(ENV_API_ID_KEY)
        if api_id is None:
            raise CommandError(f'{ENV_API_ID_KEY} is not set (env or --api-id).')
        try:
            self.api_id = int(api_id)
        except ValueError:
            # check {api_id!r}
            raise CommandError(f'{ENV_API_ID_KEY} must be an integer, got: {api_id}')

        self.api_hash = (api_hash_opt or os.getenv(ENV_API_HASH_KEY) or '').strip()
        if not self.api_hash:
            raise CommandError(f'{ENV_API_HASH_KEY} is not set (env or --api-hash).')

        self.phone = (phone_opt or os.getenv(ENV_PHONE_KEY) or '').strip()
        if not self.phone:
            raise CommandError(f'{ENV_PHONE_KEY} is not set (env or --phone).')

        # Confirm overwrite if session already exists
        self._confirm_overwrite_if_exists(force)

        # Generate session string
        asyncio.run(self.get_session_string())
        self._set_session_string(ENV_SESSION_KEY)
        # swag
        self.stdout.write(self.style.SUCCESS('Generated and saved Telegram StringSession to .env'))

    def _confirm_overwrite_if_exists(self, force: bool) -> None:
        '''Ask user confirmation before overwriting an existing session.

        In non-interactive environments, requires --force to proceed.

        Args:
            force: If true, skip interactive prompt and overwrite silently.

        Raises:
            CommandError: when session exists and user declines or --force is missing.
        '''
        existing = os.getenv(ENV_SESSION_KEY)
        if existing and not force:
            if sys.stdin.isatty():
                answer = input(f'{ENV_SESSION_KEY} already exists. Regenerate/overwrite? [y/N] ').strip().lower()
                if answer != 'y':
                    raise CommandError('Aborted by user; existing session not changed.')
            else:
                raise CommandError(f'{ENV_SESSION_KEY} already exists. Use --force to overwrite in non-interactive mode.')

    async def get_session_string(self) -> None:
        '''Authenticate with Telegram and produce a serialized StringSession.

        Uses Telethon interactive flow:
        - Constructs a TelegramClient with StringSession().
        - Starts authentication using provided phone (and optional 2FA password).
        - On success, saves the serialized session into self.string_session.

        Raises:
            CommandError: on client construction errors or authentication failures.
            OSError: if disconnect errors occur.
        '''
        try:
            client = TelegramClient(StringSession(), self.api_id, self.api_hash)
        except Exception as e:
            raise CommandError(f'Failed to construct Telegram client: {e}') from e

        try:
            await client.start(
                phone=self.phone,
                password=os.getenv(ENV_PASSWORD_KEY, '')  # optional 2FA password
            )
            # save the session string
            self.string_session = client.session.save()
        except ValueError as e:
            raise CommandError(f'Wrong values passed to client: {e}') from e
        # many thins can go wrong, so need to keep Exception
        except Exception as e:
            raise CommandError(f'Failed to authenticate with Telegram: {e}') from e
        finally:
            try:
                await client.disconnect()
                await client.disconnected
            except OSError as e:
                raise OSError(f'Error on disconnect: {e}') from e

    def _set_session_string(self, string_session_key: str) -> None:
        '''Persist the generated session string into .env.

        Args:
            string_session_key: Environment key to set (e.g., TELEGRAM_SESSION_STRING).

        Raises:
            CommandError: if session is missing or writing .env fails.
        '''
        if not self.string_session:
            raise CommandError('No session string generated; aborting write to .env')
        try:
            set_key(self.env_path, string_session_key, self.string_session)
            logger.info(f'Saved Telegram StringSession to {self.env_path} ({string_session_key})')
        except PermissionError as e:
            raise CommandError(f'Permission denied writing to .env: {e}') from e
        except OSError as e:
            raise CommandError(f'OS error while writing .env: {e}') from e
