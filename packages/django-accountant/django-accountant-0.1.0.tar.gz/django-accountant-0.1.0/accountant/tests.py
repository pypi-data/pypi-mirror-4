# coding: utf8

from django.core.urlresolvers import reverse

from .models import Account, Transaction

from django.contrib.auth import get_user_model
create_user = get_user_model().objects.create_user

from django import test


class BaseTestCase(test.TestCase):
    """
    The base test case, providing convenience methods for various testing
    related tasks.
    """

    def setUp(self):
        self.client = test.client.Client()

    def check_template(self, url_name, templated_path,
                       method='get', **kwargs):
        """
        Checks the given template was used for the given url.
        """

        response = getattr(self, method)(
            url_name=url_name, url_kwargs=kwargs
        )
        self.assertTemplateUsed(response, templated_path)

    def get_url(self, name, **kwargs):
        """ Returns the url for the given name, args and kwargs. """

        return reverse(name, kwargs=kwargs)

    def get(self, url_name=None, url=None, url_kwargs={}, data={}):
        """
        Returns the response for a POST request on the url with the given name,
        args and kwargs.
        """

        if not url:
            url = self.get_url(url_name, **url_kwargs)

        return self.client.get(url, data=data)

    def post(self, url_name=None, url=None, url_kwargs={}, data={}):
        """
        Returns the response for a POST request on the url with the given name,
        args and kwargs.
        """

        if not url:
            url = self.get_url(url_name, **url_kwargs)

        return self.client.post(url, data=data)


class TestAccount(BaseTestCase):
    email1 = 'test1@example.com'
    password1 = 'test'

    email2 = 'test2@example.com'
    password2 = 'test'

    def setUp(self):
        self.user1 = create_user(self.email1, self.password1)
        self.user1_source = Account.GetPrimarySourceAccount(self.user1)
        self.user1_destination = Account.GetPrimaryDestinationAccount(
            self.user1
        )

        self.user2 = create_user(self.email2, self.password2)
        self.user2_source = Account.GetPrimarySourceAccount(self.user2)
        self.user2_destination = Account.GetPrimaryDestinationAccount(
            self.user2
        )

    def test_new_user_destination_account_creation(self):
        user = create_user('bob@dundermifflin.com', 'test')

        try:
            self.assertNotEqual(
                Account.GetPrimaryDestinationAccount(user), None
            )
        except Account.DoesNotExist:
            self.fail('New user destination account creation failed.')

    def test_new_user_source_account_creation(self):
        user = create_user('samantha@dundermifflin.com', 'test')

        try:
            self.assertNotEqual(
                Account.GetPrimarySourceAccount(user), None
            )
        except Account.DoesNotExist:
            self.fail('New user source account creation failed.')

    def test_new_user_balance(self):
        user = create_user('hope@dundermifflin.com', 'test')

        self.assertEqual(
            Account.GetPrimaryDestinationAccount(user).balance, 0.0
        )

        self.assertEqual(Account.GetPrimarySourceAccount(user).balance, 0.0)

    def test_balance(self):
        Transaction.objects.create(
            amount=50.0,
            source_account=self.user1_source,
            destination_account=self.user1_destination,
            is_settled=True,
        )

        self.assertEqual(self.user1_source.balance, 50.0)

    def test_transfer(self):
        Transaction.objects.create(
            amount=50.0,
            source_account=self.user1_source,
            destination_account=self.user1_destination,
            is_settled=True,
        )

        self.user1_source.transfer(50.0, self.user2_destination)
        self.assertEqual(self.user2_destination.balance, 50.0)

    def test_transfer_insufficient_balance(self):
        self.assertEqual(self.user1_source.balance, 0.0)

        with self.assertRaises(Account.InsufficientBalance):
            self.user1_source.transfer(50.0, self.user2_destination)
