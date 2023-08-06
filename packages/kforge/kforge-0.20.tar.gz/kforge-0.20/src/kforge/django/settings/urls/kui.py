from django.conf.urls.defaults import *
import re
import kforge.regexps

urlpatterns = patterns('kforge.django.apps.kui.views',

    #
    ##  Application Home Page

    (r'^$',
        'kui.welcome'),

    #
    ##  About 

    (r'^about/$',
        'kui.about'),

    #
    ##  Feed 

    (r'^feed/$',
        'kui.feed'),

    #
    ##  Account recovery

    (r'^recover/$',
        'accesscontrol.recover'),
    #
    ##  User Authentication

    (r'^login/(?P<returnPath>(.*))$',
        'accesscontrol.login'),
    (r'^logout/$',
        'accesscontrol.logout'),

    #
    ##  Administration
    
    (r'^admin/model/create/(?P<className>(\w*))/$',
        'admin.create'),

    (r'^admin/model/update/(?P<className>(\w*))/(?P<objectKey>([^/]*))/$',
        'admin.update'),

    (r'^admin/model/delete/(?P<className>(\w*))/(?P<objectKey>([^/]*))/$',
        'admin.delete'),

    (r'^admin/model/(?P<className>([^/]*))/(?P<objectKey>([^/]*))/(?P<hasMany>([^/]*))/$',
        'admin.listHasMany'),

    (r'^admin/model/create/(?P<className>([^/]*))/(?P<objectKey>([^/]*))/(?P<hasMany>([^/]*))/$',
        'admin.createHasMany'),

    (r'^admin/model/(?P<className>([^/]*))/(?P<objectKey>([^/]*))/(?P<hasMany>([^/]*))/(?P<attrKey>([^/]*))/$',
        'admin.readHasMany'),

    (r'^admin/model/update/(?P<className>([^/]*))/(?P<objectKey>([^/]*))/(?P<hasMany>([^/]*))/(?P<attrKey>([^/]*))/$',
        'admin.updateHasMany'),

    (r'^admin/model/delete/(?P<className>([^/]*))/(?P<objectKey>([^/]*))/(?P<hasMany>([^/]*))/(?P<attrKey>([^/]*))/$',
        'admin.deleteHasMany'),

    (r'^admin/model/(?P<className>([^/]*))/(?P<objectKey>([^/]*))/$',
        'admin.read'),

    (r'^admin/model/(?P<className>([^/]*))/$',
        'admin.list'),

    (r'^admin/model/$',
        'admin.model'),

    (r'^admin/$',
        'admin.index'),

    #
    ##  Access Control
    
    (r'^accessDenied/(?P<deniedPath>(.*))$',
        'kui.accessDenied'),

    #
    ##  Person

    (r'^people/create/(?P<returnPath>(.*))$',
        'person.create'),
        
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
        
    (r'^people/(?P<personName>%s)/$' % kforge.regexps.personName,
        'person.read'),
        
    (r'^people/(?P<personName>%s)/home/$' % kforge.regexps.personName,
        'person.read'),
        
    (r'^people/(?P<personName>%s)/edit/$' % kforge.regexps.personName,
        'person.update'),
        
    (r'^people/(?P<personName>%s)/delete/$' % kforge.regexps.personName,
        'person.delete'),

    (r'^people/(?P<personName>%s)/tickets/$' % kforge.regexps.personName,
        'person.tickets'),

    (r'^people/(?P<personName>%s)/tracsearch/$' % kforge.regexps.personName,
        'person.tracsearch'),

    #
    ## SSH Key 
    
    (r'^people/(?P<personName>%s)/sshKeys/$' % kforge.regexps.personName,
        'sshKey.list'),

    (r'^people/(?P<personName>%s)/sshKeys/create/$' % kforge.regexps.personName,
        'sshKey.create'),

    (r'^people/(?P<personName>%s)/sshKeys/(?P<sshKeyId>(\d*))/delete/$' % (
        kforge.regexps.personName),  
        'sshKey.delete'),

    (r'^people/(?P<personName>%s)/sshKeys/(?P<sshKeyId>(\d*))/$' % (
        kforge.regexps.personName),  
        'sshKey.read'),

    #
    ## API Key
    (r'^people/(?P<personName>%s)/apikey/$' % kforge.regexps.personName,
        'person.apikey'),
            

    #
    ##  Project

    (r'^projects/create/(?P<returnPath>(.*))$',
        'project.create'),
        
    (r'^projects/$',
        'project.list'),
        
    (r'^projects/find/(?P<startsWith>[\w\d]+)/$',
        'project.search'),
        
    (r'^projects/find/$',
        'project.search'),
        
    (r'^projects/search/$',
        'project.search'),
        
    (r'^projects/home/$',
        'project.read'),
        
    (r'^projects/(?P<projectName>%s)/$' % kforge.regexps.projectName,
        'project.read'),
        
    (r'^projects/(?P<projectName>%s)/home/$' % kforge.regexps.projectName,
        'project.read'),
        
    (r'^projects/(?P<projectName>%s)/edit/$' % kforge.regexps.projectName,
        'project.update'),
        
    (r'^projects/(?P<projectName>%s)/delete/$' % kforge.regexps.projectName,
        'project.delete'),

    (r'^projects/(?P<projectName>%s)/join/$' % kforge.regexps.projectName,
        'project.join'),
        

    #
    ##  Member

    (r'^projects/(?P<projectName>%s)/members/$' % kforge.regexps.projectName,
        'member.list'),
        
    (r'^projects/(?P<projectName>%s)/members/create/$' % kforge.regexps.projectName,
        'member.create'),
        
    (r'^projects/(?P<projectName>%s)/members/(?P<personName>%s)/edit/$' % (
        kforge.regexps.projectName, kforge.regexps.personName),  
        'member.update'),
        
    (r'^projects/(?P<projectName>%s)/members/(?P<personName>%s)/delete/$' % (
        kforge.regexps.projectName, kforge.regexps.personName),  
        'member.delete'),

    (r'^projects/(?P<projectName>%s)/members/(?P<personName>%s)/approve/$' % (
        kforge.regexps.projectName, kforge.regexps.personName),  
        'member.approve'),

    (r'^projects/(?P<projectName>%s)/members/(?P<personName>%s)/reject/$' % (
        kforge.regexps.projectName, kforge.regexps.personName),  
        'member.reject'),

    #
    ##  Service
    
    (r'^projects/(?P<projectName>%s)/services/$' % kforge.regexps.projectName,
        'service.list'),

    (r'^projects/(?P<projectName>%s)/services/create/$' % kforge.regexps.projectName,
        'service.create'),

    (r'^projects/(?P<projectName>%s)/services/(?P<serviceName>%s)/edit/$' % (
        kforge.regexps.projectName, kforge.regexps.serviceName),  
        'service.update'),

    (r'^projects/(?P<projectName>%s)/services/(?P<serviceName>%s)/delete/$' % (
        kforge.regexps.projectName, kforge.regexps.serviceName),  
        'service.delete'),

    (r'^projects/(?P<projectName>%s)/services/(?P<serviceName>%s)/$' % (
        kforge.regexps.projectName, kforge.regexps.serviceName),  
        'service.read'),

    #
    ##  API

    (r'^api.*$',
        'api.api'),


    #
    ##  Not Found

    (r'^.*/$',
        'kui.pageNotFound'),
)

