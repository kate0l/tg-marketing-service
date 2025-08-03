from django.test import TestCase
from config.users.models import User
from django.db import models
from config.users.models import ROLE_MAXLENGTH, BIO_MAXLENGTH
from tests.fixtures import urls
from random import choices
from string import ascii_letters, digits
from sys import maxunicode

def make_str(l: int) -> str:
    return ''.join(choices(range(maxunicode), l))

class UserModelTest(TestCase):
    def setUp(self):
        # also need to check for superuser (idk what it is tho)
        self.user = User.objects.create_user(
            # check if it is a valid url in form test, not here
            avatar_image=urls['valid'][0],
            role=make_str(ROLE_MAXLENGTH),
            bio=make_str(BIO_MAXLENGTH)
        )