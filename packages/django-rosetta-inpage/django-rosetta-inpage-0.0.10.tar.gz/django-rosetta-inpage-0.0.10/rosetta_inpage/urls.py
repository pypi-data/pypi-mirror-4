from django.conf.urls.defaults import patterns, url
from django.contrib.admin.views.decorators import staff_member_required
from rosetta_inpage.views import MessageView, GitHubView, ChangeLocaleView

urlpatterns = patterns('',
                       #url(r'ajax/message', 'rosetta_inpage.views.save_message' ),
                       url(r'ajax/message', staff_member_required(MessageView.as_view()),
                           name='rosetta-inpage-message'),
                       url(r'ajax/github', staff_member_required(GitHubView.as_view()),
                           name='rosetta-inpage-github'),
                       url(r'change-locale', staff_member_required(ChangeLocaleView.as_view()),
                           name='rosetta-inpage-change'),
                       )

