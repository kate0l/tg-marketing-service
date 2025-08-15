from random import choices
from sys import maxunicode
from rstr import xeger
from re import sub
import json
from typing import Any

# generated data is stored as json files in FIXTURES_DIR directory
FIXTURES_DIR_PATH = 'tests/fixtures'
RULES_FILE_PATH = 'tests/rules.json'
DEFAULT_TEXT_LEN = 50
DEFAULT_INT_LEN = 10
DEFAULT_FILE_DEPTH = 5
NUM_OF_FIXTURES = 10
# tests will fail if this len is not enough for a field in some form
# ! why did i add this?
INVALID_DATA_LEN = 20

class DataValidator:
    @staticmethod
    def validate_json_object( json_obj: Any) -> bool:
        try:
            '''
            json.loads insted of json.load
            because loads -> obj, load -> file-like obj
            loads is faster
            '''
            json.loads(json_obj)
        except (TypeError, ValueError) as e:
            return False
        # this cathces all other exceptions
        # this should not happen, so raising Exception
        except Exception as e:
            raise Exception(f'Exception while validating json_str: {e}')
        else:
            return True


class DataGenerator:
    '''
    class to generate random data (only valid except generate_invalid_data)
    dummy json is cool tho requires internet, faker is too complex

    def f(regex or func to validate):
        regex: check if randomly generated data matches regex
        func: check that randomly generated data is validateable

    output: lists with data_size num of elements
    '''

    def __init__(self, num_of_fixtures=NUM_OF_FIXTURES) -> None:
        # how many fixtures to make
        self.data_size = num_of_fixtures
        try:
            with open(RULES_FILE_PATH, 'r') as f:
                self.rules = json.load(f)
        except FileNotFoundError as e:
            raise Exception(f'Rules file is not found: {e}')
        
        # considering of adding a rule key and change validator to the func that should check validity according to the rule
        self.rules = {
            "limited": {
                "url": "((https|http):\\/\\/|)(www|).{5,100}\\.(apng|avif|gif|jpg|jpeg|jfif|pjp|pjpeg|png|svg|webp|bmp|ico|tiff)",
                "email": "([-!#$%&'*+/=?^_`{}|~0-9A-Za-z]+(\\.[-!#$%&'*+/=?^_`{}|~0-9A-Za-z]+)*)@([A-Za-z0-9]([A-Za-z0-9\\\\-]{0,61}[A-ZaZm0-9])?\\.)*[A-Za-z]{2,}",
                "datetime": "(19\\d\\d|20\\d\\d)-(0[1-9]|1[0-2])-(0[1-9]|[12]\\d|3[01])",
            },
            "unlimited": {
                "text": ".",
                "int": "\\d",
            },
        }
        self.fixtures_generators = [
            {
                'name': 'urls',
                'generator': self.generate_urls,
                'rule': self.rules['limited']['url'],
                'validator': None,
            },
            {
                'name': 'emails',
                'generator': self.generate_emails,
                'rule': self.rules['limited']['email'],
                'validator': None,
            },
            {
                'name': 'text',
                'generator': self.generate_text,
                'rule': self.rules['unlimited']['text'],
                'validator': None,
            },
            {
                'name': 'int',
                'generator': self.generate_int,
                'rule': self.rules['unlimited']['int'],
                'validator': None,
            },
            {
                'name': 'datetime',
                'generator': self.generate_datetime,
                'rule': self.rules['limited']['datetime'],
                'validator': None,
            },
            {
                'name': 'json',
                'generator': self.generate_json_object,
                'rule': None,
                'validator': DataValidator.validate_json_object
            },
        ]


    # max len is for fixtures which len is controlled by changeable code in forms etc.
    # for exmaple email regex has len
    def _generate_data_from_regex(self, rule: str, max_len: int = 0) -> tuple:
        if isinstance(rule, str):
            rgx = rule
            data = []
            if max_len:
                rgx = f'(?:{rgx}){{1,{max_len}}}'
            for _ in range(self.data_size):
                elem = xeger(rgx)
                elem = sub(r'\s+', '', elem)
                data.append(elem)
            return tuple(data)

    def generate_urls(self, rule: str) -> tuple:
        return self._generate_data_from_regex(rule)

    def generate_emails(self, rule: str) -> tuple:
        return self._generate_data_from_regex(rule)
    
    # max_length can be set on a charfield field (for example in a form)
    # and we cannot limit length of the string,
    # so add unexpected but necessary parameter max_len
    def generate_text(self, rule: str, max_len: int = DEFAULT_TEXT_LEN) -> tuple:
        return self._generate_data_from_regex(rule, max_len)

    def generate_datetime(self, rule: str) -> tuple:
        return self._generate_data_from_regex(rule)

    def generate_int(self, rule: str, max_len: int = DEFAULT_INT_LEN) -> tuple:
        return self._generate_data_from_regex(rule, max_len)

    # a list of dicts
    # this is for JSONField in parser model, but actually JSONField only accapets lists
    # so tuple will be converted to list when passed. i leave as it is bcs it doesnt rly matter
    def generate_json_object(self, max_len: int = DEFAULT_FILE_DEPTH) -> tuple:
        # generate single random strings for keys/values using the text rule
        def rand_str() -> str:
            s = xeger(f'(?:{self.rules["unlimited"]["text"]}){{1,{DEFAULT_TEXT_LEN}}}')
            return sub(r'\s+', '', s)
        json_obj = tuple({rand_str(): rand_str()} for _ in range(max_len))
        # validate by passing a JSON string to the validator
        return json_obj if DataValidator.validate_json_object(json.dumps(json_obj)) else ()

    def generate_invalid_data(self):
        # random data with choices (random)
        # only restriction is data_size
        invalid_data = []
        for _ in range(self.data_size):
            list_of_chars = [chr(c) for c in choices(range(maxunicode+1), k=INVALID_DATA_LEN)]
            invalid_data.append(''.join(list_of_chars))

        return tuple(invalid_data)
    
    @staticmethod
    def generate_fixtures(self) -> None:
        '''
        save_fixture(FIXTURE_DIR_PATH/fixturename, generate_data, generate_invalid_data)
        -> json file with 2 keys ('valid', 'invalid') each with data_size num of elems
        '''
        for fixture in self.fixtures_generators:
            rule = fixture.get('rule')
            valid = fixture['generator']() if rule is None else fixture['generator'](rule)
            self.save_fixture(
                fixture['name'],
                valid,
                self.generate_invalid_data()
            )

    # data saved as json file
    def save_fixture(self, fixture_name: str, valid_data, invalid_data) -> None:
        data = {
            "valid": valid_data,
            "invalid": invalid_data,
        }

        fixture_path = f"{FIXTURES_DIR_PATH}/{fixture_name}.json"
        with open(fixture_path, 'w') as f:
            json.dump(data, f)
            # indent=4 maybe needed
        
        return None