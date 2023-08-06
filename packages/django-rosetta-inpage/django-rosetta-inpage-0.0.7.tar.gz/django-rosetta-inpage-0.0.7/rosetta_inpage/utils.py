# -*- coding: utf-8 -*-
import re
import logging

from django.conf import settings
from django.utils.translation import to_locale
from django.utils.translation.trans_real import get_language

from rosetta.storage import get_storage
from rosetta.polib import pofile
from rosetta.poutil import find_pos

from rosetta_inpage.conf import (REQUEST, THIRD_PARTY_APPS)
from rosetta_inpage.patches import THREAD_LOCAL_STORAGE


# Key for the cache, all catalogs are stored in a dictionary with this key
CACHE_KEY = 'rosetta-inpage-catalog'

logger = logging.getLogger(__name__)


def get_cache_key(locale):
    return "%s-%s" % (CACHE_KEY, locale)


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

    request = getattr(THREAD_LOCAL_STORAGE, REQUEST, None)

    if not request:
        raise SystemError('Could not fetch the request object from THREAD_LOCALE_STORAGE')

    cache_key_locale = get_cache_key(locale)
    if hasattr(request, cache_key_locale):
        return getattr(request, cache_key_locale)

    storage = get_storage(request)

    if storage.has(cache_key_locale):
        catalog = storage.get(cache_key_locale)
        setattr(request, cache_key_locale, catalog)
        return catalog

    files = find_pos(locale, third_party_apps=THIRD_PARTY_APPS)
    if len(files) == 0:
        raise ValueError('Could not find any po files for locale: %s' % locale)

    # This catalog is needed to check whether a message is translated or not, we don't wont the interfere
    # with rosetta's logic ...
    #catalog = copy.deepcopy(pofile(files[0]))
    logger.info('Creating cached catalog for: %s' % locale)
    catalog = pofile(files[0])

    # Join the other po files to the original
    for i in range(1, len(files)):
        #deep = copy.deepcopy(pofile(files[i]))
        deep = pofile(files[i])
        for entry in deep:
            entry.pfile = files[i]
            catalog.append(entry)

    catalog.dict = dict((e.msgid, e) for e in catalog)

    # Store the catalog on the request
    setattr(request, cache_key_locale, catalog)
    # Store the catalog in the cache
    storage.set(cache_key_locale, catalog)

    #get_catalogs()[locale] = catalog
    #print "Catalog: ", repr(catalog)
    #print "Dict: ", repr(catalog.dict)
    return catalog


def encode(message):
    """
    TODO: check encoding source

    @param message:
    @type message: str
    @return:
    """
    try:
        return message.decode('ASCII').encode('utf-8')
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


def save_message(msgid, msgtxt, locale):
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
    #stor = storage.get_storage(request)
    files = []
    catalog = get_locale_catalog(locale)
    pofiles = find_pos(locale, third_party_apps=THIRD_PARTY_APPS)

    #print "Post 1 = ", str(source), ", ", str(target_locale), ", ", str(target_msg)
    #print "Post 1.1 = ", str(settings.SOURCE_LANGUAGE_CODE), ", ", str(request.LANGUAGE_CODE)
    #print "Post = ", repr(stor), ", ", repr(pos)

    translated = catalog.dict.get(msgid, None)

    # Update the message in the catalog
    if translated:
        translated.msgstr = msgtxt
        catalog.dict[msgid] = translated
        request = getattr(THREAD_LOCAL_STORAGE, REQUEST, None)
        cache_key_locale = get_cache_key(locale)
        storage = get_storage(request)
        # print "Store it in the tze cache %s" % cache_key_locale
        storage.set(cache_key_locale, catalog)

    # Save the translation in all the po files that have msgid
    logger.info('Saving msgid %s ' % msgid)
    saved = False
    for path in pofiles:
        pfile = pofile(path)
        po_entry = pfile.find(msgid)

        if po_entry:
            po_entry.msgstr = msgtxt
            po_entry.obsolete = False
            try:
                po_entry.flags.remove('fuzzy')
            except ValueError:
                pass
            pfile.save()
            files.append(path)
            saved = True
            logger.info('Saved to %s' % path)
            #po_filepath, ext = os.path.splitext(p)
            #save_as_mo_filepath = po_filepath + '.mo'
            #file.save_as_mofile(save_as_mo_filepath)
            #print "Msg = ", repr(po_entry), ", ", str(po_entry)

    if not saved:
        logger.error('Did not save to any file')

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


def is_translated(entry):
    """
    The translated() instance method of an poentry also takes 'fuzzy' into account.  That's not what we want here.

    @param entry:
    @return:
    """
    if entry and entry.msgstr is not u"" or None and not entry.obsolete:
        return True
    else:
        return False
