from django.core.validators import EmailValidator
from random import choices
from sys import maxunicode
from rstr import xeger
from re import sub
from json import load, dump
from pathlib import Path


# generated data is stored as json files in FIXTURES_DIR directory
FIXTURES_DIR_PATH = 'tests/fixtures'
RULES_FILE_PATH = 'tests/rules.json'

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

    def generate_urls(self, rgx: str) -> tuple:
        urls = []
        for _ in range(self.data_size):
            url = xeger(rgx)
            url = sub(r'\s+', '', url)
            urls.append(url)

        return tuple(urls)


    def generate_emails(self, EmailValidator):
        ...

    def generate_invalid_data(self):
        # random data with choices (random)
        # only restriction is data_size
        ...

# data saved as json file
def save_fixture(fixture_name: str, valid_data, invalid_data) -> None:
    data = [
        {"valid": valid_data},
        {"invalid": invalid_data},
    ]

    fixture_path = Path(FIXTURES_DIR_PATH) / fixture_name

    with open(fixture_path, 'w') as f:
        dump(data, f)
        # indent=4
    
    return None

def test():
    '''
    load rules from json file
    import validators (functions)

    save_fixture(FIXTURE_DIR_PATH/fixturename, generate_data, generate_invalid_data)
    -> json file with 2 keys ('valid', 'invalid') each with data_size num of elems
    '''
    dg = DataGenerator()
    # need rules for urls -> rules['urls']
    # if its not in rules, then data validator function is used explicitly imported to here
    with open('tests/rules.json', 'r') as f:
        rules = load(f)

    fixtures_generators = {
        'urls': dg.generate_urls,
        'emails': dg.generate_emails,
    }
    # urls
    save_fixture('urls', fixtures_generators['urls'](rules["url"]), dg.generate_invalid_data(''))

if __name__ == '__main__':
    test()