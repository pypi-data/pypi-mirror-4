# coding: utf8

from django.contrib import admin

from .models import Account, Transaction


class AccountAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'comment',
        'balance',
        'is_primary_destination',
        'is_primary_source',
        'created',
        'modified',
    )

admin.site.register(Account, AccountAdmin)


class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'source_account',
        'destination_account',
        'amount',
        'is_settled',
        'comment',
        'created',
        'modified',
    )

admin.site.register(Transaction, TransactionAdmin)
