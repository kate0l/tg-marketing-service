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
                'text': r'[\t\n\r -~]',
                'int': r'\d',
            },
            'invalid': r'[\t\n\r -~]'
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
        rgx: str,
        max_len: int = 0,
        data_type=str,
        validator: object = None,
        remove_whitespace: bool = True,
        ensure_unique: bool = False, # for fields on models that are unique
        max_attempts_multiplier: int = 20,
    ) -> tuple:
        data = []
        if not isinstance(rgx, str):
            return tuple(data)
        if max_len:
            rgx = f'(?:{rgx}){{1,{max_len}}}'

        attempts = 0
        # avoid under-generation when validation is strict - simply make more generations
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
            # random printable string without leading/trailing whitespace
            s = xeger(self.rules['unlimited']['text'] + '{1,' + str(max_line_len) + '}')
            return sub(r'^\s+|\s+$', '', s) or 'x'
        # produce a list (not nested) of small dicts per entry
        items = []
        for _ in range(self.data_size):
            list_len = 2
            items.append([{rand_str(): rand_str()} for __ in range(list_len)])
        json_obj = tuple(items)
        if validator:
            # keep only those that pass validator, fallback to a simple list if none
            filtered = [obj for obj in json_obj if validator(obj)]
            json_obj = tuple(filtered) if filtered else tuple([[{"x": "y"}]] * self.data_size)
        return json_obj

    def generate_invalid_data(self, rule=None, max_len=INVALID_DATA_LEN):
        # random data with choices (random)
        # only restriction is data_size
        rgx = f'(?:{rule}){{1,{max_len}}}'
        return tuple(xeger(rgx) for _ in range(self.data_size))

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
                self.generate_invalid_data(rule=self.rules['invalid'])
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
        self.generator = DataGenerator(num_of_fixtures)

    ...

if __name__ == '__main__':
    ModelFixtureGenerator(NUM_OF_FIXTURES).generate_fixtures()
