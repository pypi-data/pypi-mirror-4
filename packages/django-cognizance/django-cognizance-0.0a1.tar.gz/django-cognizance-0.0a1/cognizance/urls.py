from django.conf.urls import patterns, include, url
import signals

urlpatterns = patterns('',
    url(r'^$',                                          'cognizance.views.index',   name='cognizance_home'),
    url(r'^(?P<category>[-\w]+)/$',                     'cognizance.views.category',name='cognizance_category_home'),
    """
    url(r'^topic/new/(?P<forum>[-\w]+)/$',              'djero.views.create_topic', name='forum_create_topic'),
    url(r'^topic/reply/(?P<topic>[-\w]+)/$',            'djero.views.reply',        name='forum_reply'),
    url(r'^(?P<category>[-\w]+)/(?P<forum>[-\w]+)/$',   'djero.views.forum',        name='forum_board_home'),
    url(r'^topic/(?P<topic>[-\w]+)/edit/delete$',       'djero.views.delete_topic', name='forum_delete_topic'),
    url(r'^topic/(?P<topic>[-\w]+)/edit/$',             'djero.views.edit_topic',   name='forum_edit_topic'),
    url(r'^(?P<category>[-\w]+)/(?P<forum>[-\w]+)/(?P<topic>[-\w]+)/$',   
                                                        'djero.views.topic',        name='forum_topic_home'),
    """
)
