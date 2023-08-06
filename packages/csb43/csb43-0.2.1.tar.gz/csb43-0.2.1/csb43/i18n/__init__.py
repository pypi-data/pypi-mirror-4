# -*- coding: utf-8 -*-

import os
import locale
import gettext

import pkg_resources

# Change this variable to your app name!
#  The translation files will be under
#  @LOCALE_DIR@/@LANGUAGE@/LC_MESSAGES/@DOMAIN_NAME@.mo
DOMAIN_NAME = "messages"

LOCALE_DIR = pkg_resources.resource_filename(__name__, '')

DEFAULT_LANGUAGES = os.environ.get('LANG', '').split(':')
DEFAULT_LANGUAGES += ['en']

lc, encoding = locale.getdefaultlocale()
if lc:
    languages = [lc]

languages += DEFAULT_LANGUAGES
mo_location = LOCALE_DIR

gettext.install(True, localedir=None, unicode=1)

gettext.textdomain(DOMAIN_NAME)

gettext.bind_textdomain_codeset(DOMAIN_NAME, "UTF-8")

language = gettext.translation(DOMAIN_NAME, mo_location, languages = languages, fallback = True)

tr = language.ugettext