# -*- coding: utf-8 -*-
import copy
import re

from django.conf import settings
from django.utils.translation import to_locale
from django.utils.translation.trans_real import get_language, to_locale

from rosetta import storage
from rosetta.polib import pofile
from rosetta.poutil import find_pos


# Holds a catalog of locale's in memory without fallback messages
_catalogs = {}


def get_locale_catalog(locale):
    """
    Fetch the complete message catalog for a certain locale.  Messages or spread across different po files.
    To check if a message is translated or not you'll need this catalog, iterating over the po files is way to slow.
    This method consolidates all the messages a places them in a dictionary.

    @param locale: locale of the translation, e.g.: nl_NL, nl_BE, fr_BE,
    @type locale: str
    @return: POFile with an additional dictionary to quickly lookup a message
    """
    if not locale:
        raise ValueError('Invalid locale: %s' % locale)

    #print "Locale =", locale, ", Catalogs=", str(len(_catalogs))
    catalog = _catalogs.get(locale, None)
    if catalog is not None:
        return catalog

    files = find_pos(locale, third_party_apps=True)
    if len(files) == 0:
        raise ValueError('Could not find any po files for locale: %s' % locale)

    # This catalog is needed to check whether a message is translated or not, we don't wont the interfere
    # with rosetta's logic ...
    #catalog = copy.deepcopy(pofile(files[0]))
    catalog = pofile(files[0])

    # Join the other po files to the original
    for i in range(1, len(files)):
        #deep = copy.deepcopy(pofile(files[i]))
        deep = pofile(files[i])
        for entry in deep:
            entry.pfile = files[i]
            catalog.append(entry)

    catalog.dict = dict((e.msgid, e) for e in catalog)
    _catalogs[locale] = catalog

    #print "Catalog: ", repr(catalog)
    #print "Dict: ", repr(catalog.dict)
    return catalog


def get_cached_catalogs():
    """

    @return:
    """
    return  _catalogs.keys()


def encode(message):
    """
    TODO: check encoding source

    @param message:
    @type message: str
    @return:
    """
    try:
        return message.decode().encode('utf-8')
    except UnicodeEncodeError:
        return message.encode('utf-8')


def get_message(msgid, locale=None):
    """
    Fetch a message for a locale from the catalog

    @param msgid:
    @param locale:
    @return:
    """
    if not locale:
        locale = to_locale(get_language())
    catalog = get_locale_catalog(locale)
    return catalog.dict.get(msgid, None)


def save_message(msgid, msgtxt, locale, request):
    """
    Saves a translated message (msgtxt) to all the po files that have the msgid

    @param msgid: msgid as it appears in the po files
    @param msgtxt: message text
    @param locale: locale of the translation, e.g.: nl_NL, nl_BE, fr_BE,
    @param request: http request
    @return: list with all the changed po files
    """
    # Validate the translated message, it must have the same amount of variable definitions
    if not validate_variables(msgid, msgtxt):
        raise ValueError('Invalid translation, unmatched variables')

    # file_ = find_pos(langid, project_apps=project_apps, django_apps=django_apps,
    # third_party_apps=third_party_apps)[int(idx)]
    #stor = storage.get_storage(request)
    files = []
    catalog = get_locale_catalog(locale)
    pofiles = find_pos(locale, third_party_apps=True)

    #print "Post 1 = ", str(source), ", ", str(target_locale), ", ", str(target_msg)
    #print "Post 1.1 = ", str(settings.SOURCE_LANGUAGE_CODE), ", ", str(request.LANGUAGE_CODE)
    #print "Post = ", repr(stor), ", ", repr(pos)

    translated = catalog.dict.get(msgid, None)

    # Update the message in the catalog
    if translated:
        translated.msgstr = msgtxt

    # Save the translation in all the po files that have msgid
    for path in pofiles:
        pfile = pofile(path)
        po_entry = pfile.find(msgid)

        if po_entry:
            po_entry.msgstr = msgtxt
            po_entry.obsolete = False
            pfile.save()
            files.append(path)
            #po_filepath, ext = os.path.splitext(p)
            #save_as_mo_filepath = po_filepath + '.mo'
            #file.save_as_mofile(save_as_mo_filepath)
            #print "Msg = ", repr(po_entry), ", ", str(po_entry)

    return files


# Regex to find 'variable' definitions in a translatable string
PATTERN = re.compile(r'%(?:\([^\s\)]*\))?[sdf]')


def validate_variables(original, target):
    """
    Check if the translated string contains equal variable definitions.

    @param original:
    @param target:
    @return:
    """
    # original = 'This website uses cookies. Why? Click <a href="/%(country_code)s/%(language)s/conditions/cookies/" ' \
    #            'title="Cookie policy">here</a> for more information.'
    # target = 'Deze website gebruikt cookies. Waarom? Klik ' \
    #          '<a href="/%(country_code)s/%(language)s/conditions/cookies/" ' \
    #          'title="Cookie policy">hier</a> voor meer informatie.'

    if original and target:
        result1 = PATTERN.findall(original)
        result2 = PATTERN.findall(target)
        return len(result1) == len(result2)
    elif not original or not target:
        return False


def get_supported_locales():
    """

    @return: list with tuples of the supported locales
    """
    array = list(settings.LANGUAGES)
    new_array = []

    for entry in array:
        if 'en' not in entry[0]:
            # new_array.append((entry[0], entry[1]))
            new_array.append((to_locale(entry[0]), entry[1]))

    return new_array
