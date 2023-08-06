# Django Accountant

## Quick start

1. Add `"accountant"` to your INSTALLED_APPS setting like this


        INSTALLED_APPS = (
            …
            'accountant',
            …
        )
2. Add the required settings to your settings.py:


        MASTER_ACCOUNT_PK  = 1
3. Run `python manage.py syncdb` to create the model tables.
