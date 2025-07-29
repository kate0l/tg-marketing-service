from django.test import TestCase
from config.users.models import User
from tests.fixtures import URL

class UserModelTest(TestCase):
    def setUp(self):
        # also need to check for superuser (idk what it is tho)
        self.user = User.objects.create_user(
            # check if it is a valid url in form test, not here
            avatar_image=
        )