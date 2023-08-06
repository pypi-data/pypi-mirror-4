# -*- coding: utf-8 -*-
from django.conf import settings
from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils.html import mark_safe

import rosetta_inpage
from rosetta_inpage.conf import (COOKIE_PARAM, EDIT_MODE, MESSAGES, REQUEST, REQUEST_LOCALE)
from rosetta_inpage.patches import THREAD_LOCAL_STORAGE
from rosetta_inpage import utils


class TranslateMiddleware(object):
    """
    Adds an extra html toolbar (and css & js) to translate strings if the user is a staff user.
    After the response content is rendered this middleware will insert the html
    """
    def is_edit_mode(self, request):
        from django.utils.translation.trans_real import get_language, to_locale
        locale = to_locale(get_language())
        if 'en' in locale:
            return False

        #return request.GET.get('translate', 'False').lower() == 'true' and request.user.is_staff
        return request.user.is_staff and getattr(settings, 'ROSETTA_INPAGE', False)

    def process_request(self, request):
        """

        :param request:
        :return:
        """
        if self.is_edit_mode(request):
            from django.utils.translation.trans_real import get_language, to_locale
            locale = to_locale(get_language())

            setattr(THREAD_LOCAL_STORAGE, EDIT_MODE, True)
            setattr(THREAD_LOCAL_STORAGE, MESSAGES, set())
            setattr(THREAD_LOCAL_STORAGE, REQUEST, request)
            setattr(THREAD_LOCAL_STORAGE, REQUEST_LOCALE, locale)
        else:
            setattr(THREAD_LOCAL_STORAGE, EDIT_MODE, False)
        return None

    def process_response(self, request, response):
        """
        Only add the translation html if the status code is 200

        :param request:
        :param response:
        :return:
        """
        if self.is_edit_mode(request) and response.status_code == 200 and not request.path.startswith('/rosetta'):
            return self.insert_html(request, response)

        return response

    def insert_html(self, request, response):
        content = response.content
        index = content.lower().find('</body>')

        if index == -1:
            return response

        messages = getattr(THREAD_LOCAL_STORAGE, MESSAGES, set())
        view_locale = request.COOKIES.get(COOKIE_PARAM, None)
        viewer = messages_viewer(messages, view_locale)
        percentage = 100 * float(viewer[1]) / float(len(messages))
        dictionary = {
            'rosetta_inpage': {
                'messages': viewer[0],
                'translate_from': str(settings.SOURCE_LANGUAGE_CODE.split('-')[0]),
                'translate_to': str(request.LANGUAGE_CODE),
                'locales': utils.get_supported_locales(),
                'locale_view': view_locale if view_locale else settings.LANGUAGE_CODE,
                'version': rosetta_inpage.__version__,
                'stats': {
                    'count': len(messages),
                    'translated': viewer[1],
                    'percentage': percentage,
                }
            }
        }

        html = render_to_string("rosetta_inpage/sidebar.html", dictionary, context_instance=RequestContext(request))
        response.content = content[:index] + html.encode("utf-8") + content[index:]
        #response.content =  unicode(s)
        return response


def messages_viewer(list_messages, view_locale=None):
    """
    Use the original translate function instead of the patched one
    """
    from django.utils.translation.trans_real import get_language, to_locale
    from rosetta_inpage.patches import original as _  # The original

    results = []
    locale = to_locale(get_language())
    catalog = utils.get_locale_catalog(locale)
    translated_count = 0

    def create(msgid):
        entry = catalog.dict.get(msgid, None)
        # is_valid_translation = True if entry and entry.msgstr is not u"" or None \
        #     and not entry.obsolete else False
        is_valid_translation = True if entry and entry.translated() else False

        # if translated:
        #    print "\n\n", str(is_valid_translation), ", "
        #    print "Test= ", msg, translated, "==", encode(translated.msgstr), \
        #        ", file=", str(translated.pfile), "obs=", str(translated.obsolete), "\n"

        if is_valid_translation:
            msg_target = entry.msgstr
        else:
            msg_target = _(msgid)

        return {
            'show': show_message(msgid, view_locale),
            'hash': rosetta_inpage.hash_text(msgid),
            'source': mark_safe(msg),       # the source message
            'msg': mark_safe(msg_target),   # the translated message
            'translated': is_valid_translation,
        }

    def show_message(msgid, view_locale=None):
        if view_locale:
            poentry = utils.get_message(msgid, view_locale)
            if poentry and poentry.msgstr:
                return utils.encode(poentry.msgstr)
        return utils.encode(msgid)

    for msg in list_messages:
        item = create(msg)
        results.append(item)
        if item.get('translated', False):
            translated_count += 1

    return results, translated_count
