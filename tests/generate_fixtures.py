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
# tests will fail if this len is not enough for a field in some form
# ! why did i add this?
INVALID_DATA_LEN = 20

class DataValidators:
    @staticmethod
    def validate_json_object( json_obj: Any) -> bool:
        try:
            # json.dump write to a file,
            # so i use dumpts, which create an obj
            json.dumps(json_obj)
        except (TypeError, ValueError) as e:
            return False
        # this cathces all other exceptions
        # this should not happen, so raising Exception
        except Exception as e:
            raise Exception(f'Exception while creating json_str: {e}')
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

    def __init__(self, rules: dict=None) -> None:
        # how many fixtures to make
        self.data_size = 10
        try:
            with open(RULES_FILE_PATH, 'r') as f:
                self.rules = json.load(f)
        except FileNotFoundError as e:
            raise Exception(f'Rules file is not found: {e}')
        
        # considering of adding a rule key and change validator to the func that should check validity accordingto the rule
        self.fixtures_generators = [
            {
                'name': 'urls',
                'generator': self.generate_urls,
                'validator': self.rules['limited']['url'],
            },
            {
                'name': 'emails',
                'generator': self.generate_emails,
                'validator': self.rules['limited']['email'],
            },
            {
                'name': 'text',
                'generator': self.generate_text,
                # since rule does not validate data of preknown len
                # for clarity such rules are stored in different key "unlimited"
                # meaning they do not have limit and it should be set
                'validator': self.rules['unlimited']['text']
            },
            {
                'name': 'int',
                'generator': self.generate_int,
                # since rule does not validate data of preknown len
                # for clarity such rules are stored in different key "unlimited"
                # meaning they do not have limit and it should be set
                'validator': self.rules['unlimited']['int']
            },
            {
                'name': 'datetime',
                'generator': self.generate_datetime,
                'validator': self.rules['limited']['datetime']
            },
            {
                'name': 'json',
                'generator': self.generate_json_object,
                # since rule does not validate data of preknown len
                # for clarity such rules are stored in different key "unlimited"
                # meaning they do not have limit and it should be set
                'validator': DataValidators.validate_json_object
            },
        ]


    # max len is for fixtures which len is controlled by changeable code in forms etc.
    # for exmaple email regex has len
    def _generate_data_from_regex(self, rgx: str, max_len: int=0) -> tuple:
        data = []
        if max_len:
            rgx = f'(?:{rgx}){{1,{max_len}}}'
        for _ in range(self.data_size):
            elem = xeger(rgx)
            elem = sub(r'\s+', '', elem)
            data.append(elem)
        return tuple(data)

    def generate_urls(self, rgx: str) -> tuple:
        return self._generate_data_from_regex(rgx)

    def generate_emails(self, rgx: str) -> tuple:
        return self._generate_data_from_regex(rgx)
    
    # max_length can be set on a charfield field (for example in a form)
    # and we cannot limit length of the string,
    # so add unexpected but necessary parameter max_len
    def generate_text(self, rgx: str, max_len: int=DEFAULT_TEXT_LEN) -> tuple:
        return self._generate_data_from_regex(rgx, max_len)

    def generate_datetime(self, rgx: str) -> tuple:
        return self._generate_data_from_regex(rgx)

    def generate_int(self, rgx: str, max_len: int=DEFAULT_INT_LEN) -> tuple:
        return self._generate_data_from_regex(rgx, max_len)

    # a list of dicts
    # this is for JSONField in parser model, but actually JSONField only accapets lists
    # so tuple will be converted to list when passed. i leave as it is bcs it doesnt rly matter
    def generate_json_object(self, max_len: int=DEFAULT_FILE_DEPTH) -> tuple:
        json_str = tuple({self.generate_text(): self.generate_text()} for _ in range(max_len))
        return json_str if DataValidators.validate_json_object(json_str) else ()

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
        load rules from json file
        if rules not used, then generator has built-in validators

        Important: it will be better if rules are imported to class DataGenerator
        so that other developers can skip looking at signature of the class's methods

        save_fixture(FIXTURE_DIR_PATH/fixturename, generate_data, generate_invalid_data)
        -> json file with 2 keys ('valid', 'invalid') each with data_size num of elems
        '''
        # need rules for urls -> rules['urls']
        # if its not in rules,
        # then data validator function is used explicitly imported to here

        for fixture in self.fixtures_generators:
            self.save_fixture(fixture['name'],
                        fixture['generator'](fixture['validator']),
                        self.generate_invalid_data())

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

def generate_fixtures() -> None:
    dg = DataGenerator()
    dg.generate_fixtures()