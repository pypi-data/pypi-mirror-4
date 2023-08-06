
from django.conf import settings

CURRENCIES = getattr(settings, 'ZIPFELCHAPPE_CURRENCIES',
    ('CHF', 'EUR', 'USD'))

BACKER_MODEL = getattr(settings, 'ZIPFELCHAPPE_BACKER_MODEL',
    'zipfelchappe.Backer')

DISQUS_SHORTNAME = getattr(settings, 'ZIPFELCHAPPE_DISQUS_SHORTNAME', None)

ALLOW_ANONYMOUS_PLEDGES = getattr(settings, 'ZIPFECHAPPE_ALLOW_ANONYMOUS_PLEDGES', True)
