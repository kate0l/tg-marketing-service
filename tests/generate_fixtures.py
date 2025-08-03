from random import choices
from sys import maxunicode
from rstr import xeger
from re import sub
import json


# generated data is stored as json files in FIXTURES_DIR directory
FIXTURES_DIR_PATH = 'tests/fixtures'
RULES_FILE_PATH = 'tests/rules.json'
# tests will fail if this len is not enough for a field in some form
INVALID_DATA_LEN = 20

class DataGenerator:
    '''
    class to generate random data (only valid except generate_invalid_data)
    dummy json is cool tho requires internet, faker is too complex

    def f(regex or func to validate):
        regex: check if randomly generated data matches regex
        func: check that randomly generated data is validateable

    output: lists with data_size num of elements
    '''

    def __init__(self):
        self.data_size = 10

    def _generate_data_from_regex(self, rgx: str) -> tuple:
        data = []
        for _ in range(self.data_size):
            item = xeger(rgx)
            item = sub(r'\s+', '', item)
            data.append(item)
        return tuple(data)

    def generate_urls(self, rgx: str) -> tuple:
        return self._generate_data_from_regex(rgx)

    def generate_emails(self, rgx: str) -> tuple:
        return self._generate_data_from_regex(rgx)

    def generate_invalid_data(self):
        # random data with choices (random)
        # only restriction is data_size
        invalid_data = []
        for _ in range(self.data_size):
            list_of_chars = [chr(c) for c in choices(range(maxunicode+1), k=INVALID_DATA_LEN)]
            invalid_data.append(''.join(list_of_chars))

        return tuple(invalid_data)

# data saved as json file
def save_fixture(fixture_name: str, valid_data, invalid_data) -> None:
    data = {
        "valid": valid_data,
        "invalid": invalid_data,
    }

    fixture_path = f"{FIXTURES_DIR_PATH}/{fixture_name}.json"
    with open(fixture_path, 'w') as f:
        json.dump(data, f)
        # indent=4
    
    return None

def generate_fixtures() -> None:
    '''
    load rules from json file
    if rules not used, then generator has built-in validators

    Important: it will be better if rules are imported to class DataGenerator
    so that other developers can skip looking at signature of the class's methods

    save_fixture(FIXTURE_DIR_PATH/fixturename, generate_data, generate_invalid_data)
    -> json file with 2 keys ('valid', 'invalid') each with data_size num of elems
    '''
    dg = DataGenerator()
    # need rules for urls -> rules['urls']
    # if its not in rules, then data validator function is used explicitly imported to here
    with open(RULES_FILE_PATH, 'r') as f:
        rules = json.load(f)

    fixtures_generators = [
        {
            'name': 'urls',
            'generator': dg.generate_urls,
            'validator': rules['url'],
        },
        {
            'name': 'emails',
            'generator': dg.generate_emails,
            'validator': rules['email'],
        },
    ]
    for fixture in fixtures_generators:
        save_fixture(fixture['name'],
                     fixture['generator'](fixture['validator']),
                     dg.generate_invalid_data())

if __name__ == '__main__':
    generate_fixtures()