# coding: utf8

import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.dispatch import receiver

from model_utils.models import TimeStampedModel

log = logging.getLogger('accountant.models')


class Account(TimeStampedModel):
    comment = models.CharField(max_length=200, blank=True)
    is_primary_destination = models.BooleanField(default=True)
    is_primary_source = models.BooleanField(default=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='accounts')

    class InsufficientBalance(Exception):
        def __init__(self, balance, amount):
            self.balance = balance
            self.amount = amount

        def __str__(self):
            return str('%0.2f < %0.2f' % (self.balance, self.amount))

        def __unicode__(self):
            return '%0.2f < %0.2f' % (self.balance, self.amount)

    def __unicode__(self):
        if self.comment:
            return unicode('%s (%s)' % (self.user, self.comment))
        return unicode(self.user)

    @classmethod
    def GetMasterAccount(cls):
        return cls.objects.get(pk=settings.MASTER_ACCOUNT_PK)

    @classmethod
    def GetStripeAccount(cls):
        return cls.objects.get(pk=settings.STRIPE_ACCOUNT_PK)

    @classmethod
    def GetPrimaryDestinationAccount(cls, user):
        try:
            return cls.objects.get(user=user, is_primary_destination=True)
        except cls.DoesNotExist:
            log.error(
                'Primary destination account for user: %s does not exist.'
                % user
            )

    @classmethod
    def GetPrimarySourceAccount(cls, user):
        try:
            return cls.objects.get(user=user, is_primary_source=True)
        except cls.DoesNotExist:
            log.error(
                'Primary source account for user: %s does not exist.'
                % user
            )

    def get_balance(self, only_settled=True):
        """
        Sums the source transactions less than zero and the destination
        transactions greater than zero.
        """
        balance = sum(map(
            lambda t: t.amount, self.source_transactions.filter(
                amount__lt=0, is_settled=only_settled
            )
        ))

        balance += sum(map(
            lambda t: t.amount, self.destination_transactions.filter(
                amount__gt=0, is_settled=only_settled
            )
        ))

        return float(balance)
    balance = property(get_balance)

    def transfer(self, amount, account, comment=''):
        """
        Transfers the amount from this account to the given account if the
        account has enough funds.
        """
        if self.balance < amount:
            log.error(
                'Account %d does not have enough funds to cover the transfer. '
                'Balance: %0.2f, Amount Requested: %0.2f, Comment: %s' % (
                    self.pk, self.balance, amount, comment
                )
            )

            raise self.__class__.InsufficientBalance(self.balance, amount)

        Transaction.objects.create(
            amount=amount * -1,
            is_settled=True,
            source_account=self,
            destination_account=account,
            comment=comment,
        )

        destination_transaction = Transaction.objects.create(
            amount=amount,
            is_settled=True,
            source_account=self,
            destination_account=account,
            comment=comment,
        )

        return destination_transaction


@receiver(models.signals.post_save,
          sender=get_user_model(),
          dispatch_uid='create_user_account')
def create_user_account(sender, instance, created, **kwargs):
    if getattr(settings, 'ACCOUNTANT_CREATE_USER_ACCOUNT', True) and created:
        Account.objects.create(
            user=instance,
            is_primary_destination=True,
            is_primary_source=True,
        )


class Transaction(TimeStampedModel):
    amount = models.DecimalField(decimal_places=4, max_digits=9)
    comment = models.CharField(max_length=200, blank=True, default='')
    is_settled = models.BooleanField(default=False)

    source_account = models.ForeignKey(
        'accountant.Account',
        related_name='source_transactions'
    )

    destination_account = models.ForeignKey(
        'accountant.Account',
        related_name='destination_transactions'
    )

    def __unicode__(self):
        return unicode('%f %s (%d) %s -> %s' % (
            self.amount,
            self.reference_type,
            self.reference_id,
            self.source_account,
            self.destination_account
        ))
