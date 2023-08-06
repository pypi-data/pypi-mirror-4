import logging
import simplejson

from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.utils.translation import trans_real
from rosetta_inpage.conf import COOKIE_PARAM
from urlparse import urlparse
import subprocess

logger = logging.getLogger(__name__)


def json_response(view):
    """
    Decorator view to generate a json response

    @param view:
    @return:
    """
    def _json_response(*args, **kwargs):
        result = view(*args, **kwargs)

        if isinstance(result, HttpResponse):
            return result
        else:
            return HttpResponse(simplejson.dumps(result), content_type='application/json; charset=utf-8')
    return _json_response


class MessageView(View):
    @json_response
    def get(self, request):
        source = request.GET.get('source', '')
        target_locale = request.GET.get('lang', '')
        result = trans_real.ugettext(source)

        return {
            'foo': 'bar',
            'test': '42',
        }

    @csrf_exempt
    @json_response
    def post(self, request):
        from django.utils.translation.trans_real import to_locale, get_language
        from rosetta_inpage.utils import save_message

        source = request.POST.get('source', '')
        target_lang = request.POST.get('lang', '')
        target_msg = request.POST.get('msg', '')

        if target_lang:
            locale = to_locale(target_lang)
        else:
            locale = to_locale(get_language())

        files = save_message(source, target_msg, locale, request)
        return {
            'files': files,
            'msg': target_msg,
        }


class GitHubView(View):
    @json_response
    def get(self, request):
        return {
            'status': 'ok',
            'git': 'hub'
        }

    @csrf_exempt
    @json_response
    def post(self, request):
        result = {}
        try:
            answer = self.commit(request)
            #answer = (200, 'branch/foobar', 'Foobar success')
            result['status'] = answer[0]
            result['branch'] = answer[1]
            result['message'] = answer[2]
        except:
            import traceback
            print traceback.format_exc()
            logger.exception('Could not execute translation commit')
            result['status'] = 500
            result['message'] = 'Oh no, George! An unexpected exception crossed our paths, contact a techie'
        return result

    def commit(self, request):
        """
        http status codes are used to indicate whether the commit succeeded or not
        a tuple is returned with a status code and a message

        200: ok, stuff has been committed
        304: nothing has changed

        @param request:
        @return:
        """
        username = request.user.username

        # 1. Commit the changes to the po files
        proc = subprocess.Popen(['git', 'commit', '-am', '"Translations by %s"' % username], stdout=subprocess.PIPE)
        commit = proc.communicate()[0]
        #print "Commit=", commit

        # 2. Grep the current branch name
        #echo $(git branch | grep "*" | sed "s/* //")
        proc = subprocess.Popen('git branch | grep "*" | sed "s/* //"', stdout=subprocess.PIPE, shell=True)
        branch = proc.communicate()[0].rstrip('\n')
        #print "Branch=", branch

        if 'nothing to commit' in commit:
            return 304, branch, 'nothing to commit'

        # 3. Push commit to Github
        #proc = subprocess.Popen('git push origin %s' % branch, stdout=subprocess.PIPE, shell=True)
        #push = proc.communicate()[0]
        #print "Push= ", push

        #if 'Everything up-to-date' in push:
        #    return 304, branch, 'everything up-to-date'

        return 200, branch, 'We got it! Commit successful'


class ChangeLocaleView(View):
    @json_response
    def get(self, request):
        page = request.GET.get('page', None)
        locale = request.GET.get('locale', None)

        parsed = urlparse(page)
        url = [parsed.path]
        if parsed.query:
            url.append('?')
            url.append(parsed.query)

        response = HttpResponseRedirect(''.join(url))
        if locale:
            expires = 365 * 24 * 60 * 60  # one year
            response.set_cookie(COOKIE_PARAM, locale, expires)
        else:
            response.delete_cookie(COOKIE_PARAM)
        return response

