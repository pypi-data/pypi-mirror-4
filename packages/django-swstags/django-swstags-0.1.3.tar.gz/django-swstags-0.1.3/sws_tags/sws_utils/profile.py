#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
filters.py

Filtering utility library

Created by SWS on 2013-01-03.
Copyright (c) 2012 StoneWorkSolutions. All rights reserved.
'''

from datetime import date,datetime, timedelta
from django.utils.translation import ugettext_lazy as _ # Internacionalization
from sws_tags.sws_utils import json_encode
from math import ceil
import time
import copy
import re
from decimal import *
import types
from sws_tags.sws_utils.date import *
from django.conf import settings
import django_mobile


def connectedDevice(request):

    DEFAULT_DEVICE=(
        ('iphone','mobile'),
        ('ipad','mobile'),
        ('android','mobile'),
        ('winphone7','mobile'),
        ('winmo','mobile'),
        ('other','full'),
        )


    device = {}

    ua = request.META.get('HTTP_USER_AGENT', '').lower()
    
    if ua.find("iphone") > 0:
        device['iphone'] = "iphone" + re.search("iphone os (\d)", ua).groups(0)[0]
        
    if ua.find("ipad") > 0:
        device['ipad'] = "ipad"
        
    if ua.find("android") > 0:
        device['android'] = "android" + re.search("android (\d\.\d)", ua).groups(0)[0].translate(None, '.')
        
    if ua.find("blackberry") > 0:
        device['blackberry'] = "blackberry"
        
    if ua.find("windows phone os 7") > 0:
        device['winphone7'] = "winphone7"
        
    if ua.find("iemobile") > 0:
        device['winmo'] = "winmo"
        
    if not device:          # either desktop, or something we don't care about.
        device['other'] = "other"
    
    # spits out device names for CSS targeting, to be applied to <html> or <body>.
    device['classes'] = " ".join(v for (k,v) in device.items())
    
    select_default = ('other','full','full')
    for d in DEFAULT_DEVICE:
        if device['classes'].find(d[0])>=0:
            select_default = (d[0],d[1],device['classes'])

    return select_default


def InterfaceType(request):
    # select value default for first load 
    connected_device = connectedDevice(request)
    if 'interface_type' not in request.session:
        if connected_device[1] =='mobile':
            django_mobile.set_flavour('mobile',permanent=True)
        else:
            django_mobile.set_flavour('full',permanent=True)

    flavour = django_mobile.get_flavour(request)

    if flavour == "full":
        request.session['interface_type'] = 'normal'
    else:
        request.session['interface_type'] = 'simple'
        # logger.debug("Setting interface type to simple, mobile device detected")
    # print 'CONNECTED DEVICE->',connected_device
    # print  'VALOR FLAVOUR2',flavour


def profileField(filters,user,interface_type):
    # if  not simple interface show all interface normal
    interface_simple = False
    list_filters=[]


    if len(filters[0])==3:
        for f in filters:
            view_type = f[2]
            if view_type[1] == 'S':
                interface_simple = True
        if interface_simple != True:
            interface_type = 'normal'

        for f in filters:
            user_view_type = f[2]
            type_user = user_view_type[0]
            type_view = user_view_type[1]

            if interface_type == 'normal':
                if user == 'admins':
                    list_filters.append(f[0:2]) 
                elif user == 'superresellers' and  type_user != 'A':
                    list_filters.append(f[0:2])
                elif user == 'resellers' and  (type_user == 'R' or type_user == 'C') :
                    list_filters.append(f[0:2])
                elif user == 'clients' and type_user == 'C':
                    list_filters.append(f[0:2])
            else:
                if type_view=='S':
                    if user == 'admins':
                        list_filters.append(f[0:2]) 
                    elif user == 'superresellers' and  type_user != 'A':
                        list_filters.append(f[0:2])
                    elif user == 'resellers' and  (type_user == 'R' or type_user == 'C') :
                        list_filters.append(f[0:2])
                    elif user == 'clients' and type_user == 'C':
                        list_filters.append(f[0:2])
        return list_filters

    else:

        for f in filters:
            view_type = f[1]
            if view_type[1] == 'S':
                interface_simple = True
        if interface_simple != True:
            interface_type = 'normal'

        for f in filters:
            user_view_type = f[1]
            type_user = user_view_type[0]
            type_view = user_view_type[1]

            if interface_type == 'normal':
                if user == 'admins':
                    list_filters.append(f[0]) 
                elif user == 'superresellers' and  type_user != 'A':
                    list_filters.append(f[0])
                elif user == 'resellers' and  (type_user == 'R' or type_user == 'C') :
                    list_filters.append(f[0])
                elif user == 'clients' and type_user == 'C':
                    list_filters.append(f[0])
            else:
                if type_view=='S':
                    if user == 'admins':
                        list_filters.append(f[0]) 
                    elif user == 'superresellers' and  type_user != 'A':
                        list_filters.append(f[0])
                    elif user == 'resellers' and  (type_user == 'R' or type_user == 'C') :
                        list_filters.append(f[0])
                    elif user == 'clients' and type_user == 'C':
                        list_filters.append(f[0])
        return list_filters


def profileFieldExclusive(filters,user,interface_type):
    # if  not simple interface show all interface normal
    interface_simple = False
    list_filters=[]


    if len(filters[0])==3:
        for f in filters:
            view_type = f[2]
            if view_type[1] == 'S':
                interface_simple = True
        if interface_simple != True:
            interface_type = 'normal'

        for f in filters:
            user_view_type = f[2]
            type_user = user_view_type[0]
            type_view = user_view_type[1]
            type_restriction = 'F'
            if len(user_view_type)==3:
                type_restriction = user_view_type[2]

            if interface_type == 'normal':
                if user == 'admins':
                    if type_user == 'A':
                        list_filters.append(f[0:2]) 
                    elif type_restriction !='E':
                        list_filters.append(f[0:2])  

                elif user == 'superresellers' and  type_user != 'A':
                    # print'dentro',f[0:2]
                    if type_user == 'S':
                        list_filters.append(f[0:2]) 
                        # print'dentro2'
                    elif type_restriction !='E':
                        list_filters.append(f[0:2]) 
                        # print'dentro3'

                elif user == 'resellers' and  (type_user == 'R' or type_user == 'C') :
                    if type_user == 'R':
                        list_filters.append(f[0:2]) 
                    elif type_restriction!='E':
                        list_filters.append(f[0:2]) 
                        
                elif user == 'clients' and type_user == 'C':
                    list_filters.append(f[0:2]) 
            else:
                if type_view=='S':
                    if user == 'admins':
                        if type_user == 'A':
                            list_filters.append(f[0:2]) 
                        elif type_restriction !='E':
                            list_filters.append(f[0:2])  

                    elif user == 'superresellers' and  type_user != 'A':
                        if type_user == 'S':
                            list_filters.append(f[0:2]) 
                        elif type_restriction !='E':
                            list_filters.append(f[0:2]) 

                    elif user == 'resellers' and  (type_user == 'R' or type_user == 'C') :
                        if type_user == 'R':
                            list_filters.append(f[0:2]) 
                        elif type_restriction!='E':
                            list_filters.append(f[0:2]) 
                            
                    elif user == 'clients' and type_user == 'C':
                        list_filters.append(f[0:2]) 
        return list_filters

    else:

        for f in filters:
            view_type = f[1]
            if view_type[1] == 'S':
                interface_simple = True
        if interface_simple != True:
            interface_type = 'normal'

        for f in filters:
            user_view_type = f[1]
            type_user = user_view_type[0]
            type_view = user_view_type[1]
            type_restriction = 'F'
            if len(user_view_type)==3:
                type_restriction = user_view_type[2]


            if interface_type == 'normal':
                if user == 'admins':
                    if type_user == 'A':
                        list_filters.append(f[0])
                    elif type_restriction !='E':
                        list_filters.append(f[0]) 

                elif user == 'superresellers' and  type_user != 'A':
                    if type_user == 'S':
                        list_filters.append(f[0])
                    elif type_restriction !='E':
                        list_filters.append(f[0])

                elif user == 'resellers' and  (type_user == 'R' or type_user == 'C') :
                    if type_user == 'R':
                        list_filters.append(f[0])
                    elif type_restriction!='E':
                        list_filters.append(f[0])

                elif user == 'clients' and type_user == 'C':
                    list_filters.append(f[0])
            else:
                if type_view=='S':
                    if user == 'admins':
                        if type_user == 'A':
                            list_filters.append(f[0]) 
                        elif type_restriction !='E':
                            list_filters.append(f[0]) 
                    elif user == 'superresellers' and  type_user != 'A':
                        if type_user == 'S':
                            list_filters.append(f[0])
                        elif type_restriction !='E':
                            list_filters.append(f[0])
                    elif user == 'resellers' and  (type_user == 'R' or type_user == 'C') :
                        if type_user == 'R':
                            list_filters.append(f[0])
                        elif type_restriction!='E':
                            list_filters.append(f[0])
                    elif user == 'clients' and type_user == 'C':
                        list_filters.append(f[0])
        return list_filters


def requestGet(name,request):
    if name in request.GET:
        return request.GET[name]
    else:
        return 'NULL'
#update the request_data dictionary with the values of request.GET
def reloadRequest(request_data,request):  
    request_data ['previous'] = -1  
    request_data ['user_tz'] = str(request.session['user_tz'])
    for k,v in request.GET.iteritems():
        if k in request_data:
            request_data[k] = request.GET[k]
        else:
            request_data[k] = request.GET[k]
        if request_data[k] == '':
            request_data[k] = 'NULL'
    if 'int_all_time' in request_data:
        if request_data['int_all_time']=='OFF':
            request_data['int_all_time'] = 0
        else:
            request_data['int_all_time'] =1


    updateDateTz(request_data)
    return request_data





# def profileField(dic_profile,user,interface_type):
#   list_query=[]

#   interface_simple = False
#   for key in dic_profile.keys():
#       view_type = dic_profile[key]
#       if view_type[1]=='S':
#           interface_simple = True
#   if interface_simple != True:
#       interface_type = 'normal'

#   for key in dic_profile.keys():
#       view_type = dic_profile[key]
#       field_interface = view_type[1]
#       field_user = view_type[0]

#       if interface_type == 'normal':
#           if user == 'admins':
#               list_query.append(key) 
#           elif user == 'superresellers' and  field_user != 'A':
#               list_query.append(key)
#           elif user == 'resellers' and  (field_user == 'R' or field_user == 'C') :
#               list_query.append(key)
#           elif user == 'clients' and field_user == 'C':
#               list_query.append(key)
#       else:
#           if field_interface == 'S':
#               if user == 'admins':
#                   list_query.append(key) 
#               elif user == 'superresellers' and  field_user != 'A':
#                   list_query.append(key)
#               elif user == 'resellers' and  (field_user == 'R' or field_user == 'C') :
#                   list_query.append(key)
#               elif user == 'clients' and field_user == 'C':
#                   list_query.append(key)
#   return list_query
