# coding: utf8

from django.contrib.auth import get_user_model
create_user = get_user_model().objects.create_user

from testutils import BaseTestCase

from .models import Account, Transaction


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
