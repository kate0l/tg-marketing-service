Overall, it works for the happy path. A few fixes will make it more robust and complete:

Fix typos/mismatches in docs: command name, env var names.
Validate TELEGRAM_API_ID parsing and required envs; raise CommandError with clear messages.
Handle missing session_string before writing.
Use CommandError (not TypeError) and fix the f-string in the exception.
Optional: add CLI arguments via add_arguments to pass session name/phone.
Suggested changes:

# ...existing code...
'''
management.py command to create and store a Telegram StringSession:
1) initializes a Telethon client using credentials in .env
2) obtains a Telegram session string.

How to:
    python3 manage.py set_telegram_session

.env Variables:
    TELEGRAM_SESSIONS_ENV: Optional session file/name (default: 'session').
    TELEGRAM_API_ID: Telegram API ID.
    TELEGRAM_API_HASH: Telegram API hash.
    PHONE: Phone number used for sign-in (with country code, like +7).
# ...existing code...
    def handle(self, session_name: str='session', *args, **kwargs) -> None:
        '''Entry point for the management command (all need handle method)

        Loads environment variables and prepares credentials used by
        Telethon for authentication.

        Args:
            session_name (str): Optional session name passed to the command.
                It may be overridden by .env TELEGRAM_SESSIONS_ENV.
                Defaults to 'session'.

        Side Effects:
            Reads variables from a .env file via python-dotenv.
        '''
        load_dotenv()

        # all these are str
        self.session_name = os.getenv('TELEGRAM_SESSIONS_ENV') or session_name

        api_id_raw = os.getenv('TELEGRAM_API_ID')
        if not api_id_raw:
            raise CommandError("TELEGRAM_API_ID is not set in environment.")
        try:
            # api_id should be passed to Telegram as int
            self.api_id = int(api_id_raw)
        except ValueError as e:
            raise CommandError("TELEGRAM_API_ID must be an integer.") from e

        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        if not self.api_hash:
            raise CommandError("TELEGRAM_API_HASH is not set in environment.")

        self.phone = os.getenv('PHONE')
        if not self.phone:
            logger.warning("PHONE is not set; Telethon will prompt interactively.")

        # need to run in an event loop, to make it run coroutine
        asyncio.run(self.get_session_string())
        self.set_session_string()
# ...existing code...
    def set_session_string(self) -> None:
        '''Load the Telegram StringSession into the .env file.

        Locates the nearest .env using python-dotenv (searching from the
        current working directory) and writes/updates the
        TELEGRAM_SESSION_STRING key with the value previously produced by
        get_session_string().

        Returns:
            None

        Raises:
            CommandError: When .env cannot be found/written or value is invalid.
        '''
        if not self.session_string:
            raise CommandError("No session string produced; authentication may have failed.")

        try:
            dotenv_path = find_dotenv(raise_error_if_not_found=True, usecwd=True)
        except PermissionError as e:
            logger.exception("Permission denied writing TELEGRAM_SESSION_STRING to .env")
            raise CommandError("Permission denied writing to .env") from e
        except OSError as e:
            logger.exception("OS error while locating .env for TELEGRAM_SESSION_STRING")
            raise CommandError(f"OS error while locating .env: {e}") from e

        try:
            set_key(dotenv_path, 'TELEGRAM_SESSION_STRING', self.session_string)
            logger.info("Saved TELEGRAM_SESSION_STRING to %s", dotenv_path)
        except TypeError as e:
            logger.exception("Invalid TELEGRAM_SESSION_STRING type when writing to .env")
            raise CommandError(f"Invalid TELEGRAM_SESSION_STRING: {e}") from e
        except PermissionError as e:
            logger.exception("Permission denied writing TELEGRAM_SESSION_STRING to .env")
            raise CommandError("Permission denied writing to .env") from e
        except OSError as e:
            logger.exception("OS error while writing TELEGRAM_SESSION_STRING to .env")
            raise CommandError(f"OS error while writing .env: {e}") from e
# ...existing code...

Optional: expose CLI arguments.

# ...existing code...
class Command(BaseCommand):
    # ...existing code...

    def add_arguments(self, parser):
        parser.add_argument('--session', dest='session_name', default='session',
                            help='Session file/name (overrides TELEGRAM_SESSIONS_ENV)')
        parser.add_argument('--phone', dest='phone', default=None,
                            help='Phone number with country code (overrides PHONE)')

    def handle(self, session_name: str='session', *args, **kwargs) -> None:
        # ...existing code...
        self.session_name = os.getenv('TELEGRAM_SESSIONS_ENV') or kwargs.get('session_name') or session_name
        self.phone = kwargs.get('phone') or os.getenv('PHONE')
        # ...existing code...

With these changes, the command is complete for typical use:

Run: python3 manage.py set_telegram_session
Or: python3 manage.py set_telegram_session --session mysession --phone +71234567890
If you want, I can also add friendly handling of common Telethon auth errors.
