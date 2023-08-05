# -*- coding:utf-8 -*-

from django.conf import settings

# Here you can override any settings from coop default settings files
# See :
# - coop/default_project_settings.py
# - coop/db_settings.py

SITE_AUTHOR = 'Organisme'
SITE_TITLE = 'Demo Django-coop'
DEFAULT_URI_DOMAIN = '{{ domain }}'

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Administrateur', 'web@quinode.fr'),
)

MANAGERS = ADMINS
SEND_BROKEN_LINK_EMAILS = True
INTERNAL_IPS = ('127.0.0.1', '92.243.30.98')

SUBHUB_MAINTENANCE_AUTO = False    # set this value to True to automatically syncronize with agregator
PES_HOST = 'pes.domain.com'
THESAURUS_HOST = 'thess.domain.com'

INSTALLED_APPS = settings.INSTALLED_APPS + [
    # select your coop components
    'coop.tag',
    'coop.agenda',
    'coop.article',
    'coop.mailing',
    'coop.exchange',
    #'coop.webid',
    'coop_local',

    # coop optional modules
    'coop_geo',  # est obligatoirement placé APRES coop_local
]