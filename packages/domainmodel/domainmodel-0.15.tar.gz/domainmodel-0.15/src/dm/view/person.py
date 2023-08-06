from django.conf.urls.defaults import patterns
import dm.regexps

urlpatterns = patterns('',

    #
    ##  Person

    (r'^people/create/(?P<returnPath>(.*))$',
        'person.create'),

    (r'^people/pending/$',
        'person.pending'),

    (r'^people/$',
        'person.list'),

    (r'^people/find/(?P<startsWith>[\w\d]+)/$',
        'person.search'),

    (r'^people/find/$',
        'person.search'),

    (r'^people/search/$',
        'person.search'),

    (r'^people/home/$',
        'person.read'),

    (r'^people/(?P<personName>%s)/$' % dm.regexps.personName,
        'dm.view.person.read'),

    (r'^people/(?P<personName>%s)/home/$' % dm.regexps.personName,
        'person.read'),

    (r'^people/(?P<personName>%s)/update/$' % dm.regexps.personName,
        'person.update'),

    (r'^people/(?P<personName>%s)/delete/$' % dm.regexps.personName,
        'person.delete'),

    (r'^people/(?P<personName>%s)/approve/$' % dm.regexps.personName,
        'person.approve'),

)

