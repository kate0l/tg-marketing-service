from random import choices
from sys import maxunicode
from rstr import xeger
from re import sub
import json
from typing import Any
import django.core.validators
from django.core.exceptions import ValidationError
import logging
import os
from datetime import datetime
from config.users.models import ROLE_MAXLENGTH, BIO_MAXLENGTH  # for ModelFixtureGenerator

logger = logging.getLogger(__name__)

# generated data is stored as json files in FIXTURES_DIR directory
FIXTURES_DIR_PATH = 'tests/fixtures'
DEFAULT_TEXT_LEN = 50
DEFAULT_INT_LEN = 10
NUM_OF_FIXTURES = 10
INVALID_DATA_LEN = 20

class DataValidator:
    @staticmethod
    def validate_json_object(json_obj: Any) -> bool:
        try:
            if isinstance(json_obj, (str, bytes, bytearray)):
                json.loads(json_obj)
            else:
                json.dumps(json_obj)
        except (TypeError, ValueError) as e:
            raise ValidationError(e)
        else:
            return True

    @staticmethod
    def validate_url(url: str) -> bool:
        django.core.validators.URLValidator()(url)
        return True
    @staticmethod
    def validate_email(email: str) -> bool:
        django.core.validators.EmailValidator()(email)
        return True
    @staticmethod
    def validate_datetime(value: Any) -> bool:
        # accept datetime objects
        if isinstance(value, datetime):
            return True
        # if not str, then what is it
        if not isinstance(value, str):
            raise ValidationError('Invalid datetime type')
        # all possible formats
        formats = (
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y-%m-%dT%H:%M',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%f',
        )
        for format in formats:
            try:
                datetime.strptime(value, format)
                return True
            except ValueError:
                continue
        # if here, then not datetime format - raise validation error
        raise ValidationError('Invalid datetime format')


class DataGenerator:
    '''
    class to generate random data (only valid except generate_invalid_data)
    dummy json is cool tho requires internet, faker is too complex

    def f(regex or func to validate):
        regex: check if randomly generated data matches regex
        func: check that randomly generated data is validateable

    output: lists with data_size num of elements
    '''

    def __init__(self, num_of_fixtures = NUM_OF_FIXTURES) -> None:
        # how many fixtures to make
        self.data_size = num_of_fixtures
        self.rules = {
            'limited': {
                # for eaxmple https://example.com/image.jpg
                'url': r'(https?:\/\/)(?:www\.)?[A-Za-z0-9-]{2,63}\.[A-Za-z]{2,6}\/[A-Za-z0-9._~-]{3,50}\.(?:apng|avif|gif|jpg|jpeg|jfif|pjp|pjpeg|png|svg|webp|bmp|ico|tiff)',
                'email': r"([-!#$%&'*+/=?^_`{}|~0-9A-Za-z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Za-z]+)*)@([A-Za-z0-9]([A-Za-z0-9\-]{0,61}[0-9A-Za-z])?\.)*[A-Za-z]{2,}",
                'datetime': r'^(19\d\d|20\d\d)-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])[ T]([0-1][0-9]|2[0-3]):[0-5][0-9]((:[0-5][0-9])?(\.\d{1,6})?)?$',
            },
            'unlimited': {
                'text': r'.',
                'int': r'\d',
            },
        }
        '''
        rule - how the fixture is generated
        (for example regex)
        validator - how the fixture is validated
        (for example func that receives fixture)
        '''
        self.fixtures_generators = [
            {
                'name': 'urls',
                'generator': self.generate_urls,
                'rule': self.rules['limited']['url'],
                'data_type': str,
                'validator': DataValidator.validate_url,
            },
            {
                'name': 'emails',
                'generator': self.generate_emails,
                'rule': self.rules['limited']['email'],
                'data_type': str,
                'validator': DataValidator.validate_email,
            },
            {
                'name': 'text',
                'generator': self.generate_text,
                'rule': self.rules['unlimited']['text'],
                'data_type': str,
                'validator': None,
            },
            {
                'name': 'int',
                'generator': self.generate_int,
                'rule': self.rules['unlimited']['int'],
                'data_type': int,
                'validator': None,
            },
            {
                'name': 'datetime',
                'generator': self.generate_datetime,
                'rule': self.rules['limited']['datetime'],
                'data_type': str,
                'validator': DataValidator.validate_datetime,
            },
            {
                'name': 'json',
                'generator': self.generate_json_object,
                'rule': None,
                'data_type': object,
                'validator': DataValidator.validate_json_object
            },
        ]


    # max len is for fixtures which len is controlled by changeable code in forms etc.
    # for exmaple email regex has len
    def _generate_data(
        self,
        rule: str,
        max_len: int = 0,
        data_type=str,
        validator: object = None,
        remove_whitespace: bool = True,
        ensure_unique: bool = False, # for fields on models that are unique
        max_attempts_multiplier: int = 20,
    ) -> tuple:
        data = []
        if not isinstance(rule, str):
            return tuple(data)
        rgx = rule
        if max_len:
            rgx = f'(?:{rgx}){{1,{max_len}}}'

        attempts = 0
        # avoid under-generation when validation is strict
        max_attempts = self.data_size * max_attempts_multiplier
        seen = set() if ensure_unique else None

        while len(data) < self.data_size and attempts < max_attempts:
            attempts += 1
            elem = xeger(rgx)
            if remove_whitespace:
                # only remve edges
                elem = elem.strip()
            try:
                elem = data_type(elem)
            except Exception as e:
                logger.warning(f'Casting to {data_type} failed: {e}')
                continue

            if ensure_unique:
                if elem in seen:
                    continue
                seen.add(elem)

            try:
                if validator:
                    validator(elem)
            except ValidationError as e:
                logger.warning(f'Validation by {validator} failed: {e}')
                continue
            else:
                data.append(elem)
        return tuple(data)

    # kwargs because there is too many args
    def generate_urls(self, rule: str, data_type=str, validator=None, **kwargs) -> tuple:
        return self._generate_data(rule, data_type=data_type, validator=validator, **kwargs)

    def generate_emails(self, rule: str, data_type=str, validator=None, **kwargs) -> tuple:
        # ensure uniqueness for models like users.User.email (unique=True)
        kwargs.setdefault('ensure_unique', True)
        return self._generate_data(rule, data_type=data_type, validator=validator, **kwargs)

    def generate_text(self, rule: str, data_type=str, validator=None, max_len=DEFAULT_TEXT_LEN, **kwargs) -> tuple:
        # keep whitespace in text
        kwargs.setdefault('remove_whitespace', False)
        return self._generate_data(rule, max_len=max_len, data_type=data_type, validator=validator, **kwargs)

    def generate_datetime(self, rule: str, data_type=str, validator=None, **kwargs) -> tuple:
        # by default keep whitespace as-is for datetime strings
        kwargs.setdefault('remove_whitespace', False)
        return self._generate_data(rule, data_type=data_type, validator=validator, **kwargs)

    def generate_int(self, rule: str, data_type=int, validator=None, max_len=DEFAULT_INT_LEN, **kwargs) -> tuple:
        return self._generate_data(rule, max_len=max_len, data_type=data_type, validator=validator, **kwargs)

    def generate_json_object(self, rule=None, data_type=object, validator=None) -> tuple:
        # a list of dicts
        def rand_str(max_line_len: int = DEFAULT_TEXT_LEN) -> str:
            s = xeger(f'(?:{self.rules['unlimited']['text']}){{1,{max_line_len}}}')
            s = sub(r'\s+', '', s) # can be only whistespace
            return s
        json_obj = tuple([[{rand_str(): rand_str()}]] for _ in range(self.data_size))
        if validator:
            try:
                validator(json_obj)
            except ValidationError as e:
                logger.warning(f'JSON validation failed: {e}')
                return tuple()
        return json_obj

    def generate_invalid_data(self):
        # random data with choices (random)
        # only restriction is data_size
        invalid_data = []
        for _ in range(self.data_size):
            list_of_chars = [chr(c) for c in choices(range(maxunicode+1), k=INVALID_DATA_LEN)]
            invalid_data.append(''.join(list_of_chars))

        return tuple(invalid_data)

    def generate_fixtures(self) -> None:
        '''
        save_fixture(FIXTURE_DIR_PATH/fixturename, generate_data, generate_invalid_data)
        -> json file with 2 keys ('valid', 'invalid') each with data_size num of elems
        '''
        for fixture in self.fixtures_generators:
            valid = fixture['generator'](
                fixture['rule'],
                fixture['data_type'],
                fixture['validator']
            )
            self.save_fixture(
                fixture['name'],
                valid,
                self.generate_invalid_data()
            )

    # fixture saved as json file
    def save_fixture(self, fixture_name: str, valid_data, invalid_data) -> None:
        data = {
            'valid': valid_data,
            'invalid': invalid_data,
        }
        os.makedirs(FIXTURES_DIR_PATH, exist_ok=True)
        fixture_path = f'{FIXTURES_DIR_PATH}/{fixture_name}.json'
        with open(fixture_path, 'w', encoding='utf-8') as f:
            # default=str handles datetime objects
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        return None


class ModelFixtureGenerator:
    '''
    fixtures based on models,
    made by DataGenerator class
    '''
    def __init__(self, num_of_fixtures=NUM_OF_FIXTURES) -> None:
        self.base = DataGenerator(num_of_fixtures)

    def _save(self, name: str, records: list[dict]) -> None:
        self.base.save_fixture(name, tuple(records), self.base.generate_invalid_data())

    # Users.User fixtures
    # Fields covered: avatar_image (url), role (text<=ROLE_MAXLENGTH), bio (text<=BIO_MAXLENGTH), email (unique)
    def _make_users(self) -> tuple:
        emails = self.base.generate_emails(self.base.rules['limited']['email'])
        avatars = self.base.generate_urls(self.base.rules['limited']['url'])
        roles = self.base.generate_text(self.base.rules['unlimited']['text'], max_len=ROLE_MAXLENGTH)
        bios = self.base.generate_text(self.base.rules['unlimited']['text'], max_len=BIO_MAXLENGTH)

        records = []
        for i in range(self.base.data_size):
            records.append({
                'email': emails[i],
                'avatar_image': avatars[i],
                'role': roles[i],
                'bio': bios[i],
            })

        self._save('model_users_User', records)
        # return a stable unique key list to use for FKs
        return emails

    # parser.TelegramChannel fixtures
    # Fields covered: channel_id (unique int), username (text), title (text), description (text),
    # participants_count (int), parsed_at (datetime), pinned_messages (json), creation_date (datetime),
    # last_messages (json), average_views (int)
    def _make_telegram_channels(self) -> tuple:
        channel_ids = self.base.generate_int(
            self.base.rules['unlimited']['int'],
            max_len=12,
            data_type=int,
            ensure_unique=True,
        )
        usernames = self.base.generate_text(self.base.rules['unlimited']['text'], max_len=32)
        titles = self.base.generate_text(self.base.rules['unlimited']['text'], max_len=64)
        descriptions = self.base.generate_text(self.base.rules['unlimited']['text'], max_len=256)
        participants = self.base.generate_int(self.base.rules['unlimited']['int'], max_len=7, data_type=int)
        dt_rule = self.base.rules['limited']['datetime']
        parsed_at = self.base.generate_datetime(dt_rule)
        pinned = self.base.generate_json_object()
        creation_date = self.base.generate_datetime(dt_rule)
        last_messages = self.base.generate_json_object()
        avg_views = self.base.generate_int(self.base.rules['unlimited']['int'], max_len=7, data_type=int)

        records = []
        for i in range(self.base.data_size):
            records.append({
                'channel_id': channel_ids[i],
                'username': usernames[i],
                'title': titles[i],
                'description': descriptions[i],
                'participants_count': participants[i],
                'parsed_at': parsed_at[i],
                'pinned_messages': pinned[i] if i < len(pinned) else [],
                'creation_date': creation_date[i],
                'last_messages': last_messages[i] if i < len(last_messages) else [],
                'average_views': avg_views[i],
            })

        self._save('model_parser_TelegramChannel', records)
        # return channel_ids as stable unique keys for FK usage
        return channel_ids

    # parser.ChannelStats fixtures
    # Fields covered: channel (FK -> TelegramChannel.channel_id), participants_count (int),
    # daily_growth (int), parsed_at (datetime)
    def _make_channel_stats(self, channel_ids: tuple) -> None:
        participants = self.base.generate_int(self.base.rules['unlimited']['int'], max_len=7, data_type=int)
        daily_growth = self.base.generate_int(self.base.rules['unlimited']['int'], max_len=5, data_type=int)
        parsed_at = self.base.generate_datetime(self.base.rules['limited']['datetime'])

        records = []
        n = len(channel_ids) or 1
        for i in range(self.base.data_size):
            records.append({
                # reference channel by its unique channel_id (assumption: FK stored as this unique field for synthetic fixtures)
                'channel': channel_ids[i % n],
                'participants_count': participants[i],
                'daily_growth': daily_growth[i],
                'parsed_at': parsed_at[i],
            })

        self._save('model_parser_ChannelStats', records)

    # group_channels.Group fixtures
    # Fields covered: name (unique), description (text), owner (FK -> users.User.email),
    # image_url (url), created_at (datetime)
    def _make_groups(self, user_emails: tuple) -> None:
        names = self.base.generate_text(self.base.rules['unlimited']['text'], max_len=50, ensure_unique=True)
        descriptions = self.base.generate_text(self.base.rules['unlimited']['text'], max_len=200)
        image_urls = self.base.generate_urls(self.base.rules['limited']['url'])
        created_at = self.base.generate_datetime(self.base.rules['limited']['datetime'])

        records = []
        n = len(user_emails) or 1
        for i in range(self.base.data_size):
            records.append({
                'name': names[i],
                'description': descriptions[i],
                # reference owner by a unique user email (assumption: FK represented by the unique field for synthetic fixtures)
                'owner': user_emails[i % n],
                'image_url': image_urls[i],
                'created_at': created_at[i],
            })

        self._save('model_group_channels_Group', records)

    def generate_fixtures(self) -> None:
        user_emails = self._make_users()
        channel_ids = self._make_telegram_channels()
        self._make_groups(user_emails)
        self._make_channel_stats(channel_ids)

if __name__ == '__main__':
    # Generate primitive fixtures (optional) and model-based fixtures
    # Data-only fixtures (urls, emails, etc.) can still be created via DataGenerator if desired.
    ModelFixtureGenerator(NUM_OF_FIXTURES).generate_fixtures()
