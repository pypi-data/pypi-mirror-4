#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
'''
messages.py

Processes messages utility library

Created by SWS on 2012-09-11.
Copyright (c) 2012 StoneWorkSolutions. All rights reserved.
'''
from django.conf import settings
import re
import logging
import redis
import sys,traceback
# import ooint.settings

logger = logging.getLogger('sws-tags')

def processErrorsForm(form):
	
	message = ''
	messages = []

	for field in form:

		if field.errors:
			message = re.sub('</(.*)>', '', unicode(str(field.errors), 'utf-8'))
			message = re.sub('<(.*)>', '', message)
			message = field.html_name + ': ' + message
			messages.append(message)

	return messages


from django_tools.middlewares import ThreadLocal
# ThreadLocal.get_current_user()
# si necesitaras toda la request..
# ThreadLocal.get_current_request()
	
def processMessages(message, typeMessage, timeOut=10000):

	msg = {}

	def getTraceBackInfo():
		info = inspect.stack()[2][3]
		return info 
		# print 'f_back',inspect.frame().f_back
		# mod = inspect.getmodule(frm[0])
		# print '[%s] %s' % (mod.__name__, msg)
	
	called_from_view = getTraceBackInfo()

	if typeMessage == 'error':
		try:
			logger.error(' view: '+called_from_view+', user: '+str(ThreadLocal.get_current_user())+', message: '+message)
		except:
			pass
		error = (message, timeOut)
		msg['error'] = error

	elif typeMessage == 'warning':
		try:
			logger.warning(' view: '+called_from_view+', user: '+str(ThreadLocal.get_current_user())+', message: '+message)
		except:
			pass
		warning = (message, timeOut)
		msg['warning'] = warning

	elif typeMessage == 'success':
		try:
			logger.info(' view: '+called_from_view+', user: '+str(ThreadLocal.get_current_user())+', message: '+message)
		except:
			pass
		success = (message, timeOut)
		msg['success'] = success

	elif typeMessage == 'info':
		try:
			logger.info(' view: '+called_from_view+', user: '+str(ThreadLocal.get_current_user())+', message: '+message)
		except:
			pass
		info = (message, timeOut)
		msg['info'] = info

	return msg

# Send message to the specific channel
# Parametres: 
# 	name channel (session_id or settings.CHANNEL_GLOBAL_MESSAGES)
# 	text message
# 	level (info, warning,error or debug)
# 	time visible
import inspect

def sendMessages(channel=settings.CHANNEL_GLOBAL_MESSAGES,message='No messages',level='info',time=5000):
	cr = redis.Redis(settings.REDIS_IP)
	message={"message":message,"level":level,"time":time}
	cr.publish(channel,message)

	if level == 'error':
		try:
			logger.error(' user: '+str(ThreadLocal.get_current_user())+', message: '+message)
		except:
			pass
	elif level == 'warning':
		try:
			logger.warning(' user: '+str(ThreadLocal.get_current_user())+', message: '+message)
		except:
			pass
	elif level == 'success':
		try:
			logger.info(' user: '+str(ThreadLocal.get_current_user())+', message: '+message)
		except:
			pass
	elif level == 'info':
		try:
			logger.info(' user: '+str(ThreadLocal.get_current_user())+', message: '+message)
		except:
			pass

	return True


def swslog(typeMessage,message,e):

	msg = {}

	def getTraceBackInfo():
		info = inspect.stack()[2][3]
		return info 
	
	called_from_view = getTraceBackInfo()

	if typeMessage == 'error':
		try:
			logger.error(' -- '+called_from_view+', USER: '+str(ThreadLocal.get_current_user())+', MESSAGE ERROR: '+message+ ' EXCEPTION: {0}'.format(traceback.format_exc()))		
			# logger.error('*FUNCTION: '+called_from_view+', USER: '+str(ThreadLocal.get_current_user())+', MESSAGE ERROR: '+message)
			# logger.error('-----EXCEPTION: {0}'.format(traceback.format_exc()))

		except:
			pass

	elif typeMessage == 'warning':
		try:
			logger.warning(' -- '+called_from_view+', USER: '+str(ThreadLocal.get_current_user())+', MESSAGE WARNING: '+message+ ' EXCEPTION: {0}'.format(traceback.format_exc()))
		except:
			pass

	elif typeMessage == 'success':
		try:
			logger.info(' -- '+called_from_view+', USER: '+str(ThreadLocal.get_current_user())+', MESSAGE SUCCES: '+message+ 'EXCEPTION: {0}'.format(traceback.format_exc()))
		except:
			pass

	elif typeMessage == 'info':
		try:
			logger.info(' -- '+called_from_view+', USER: '+str(ThreadLocal.get_current_user())+', MESSAGE INFO: '+message+ 'EXCEPTION: {0}'.format(traceback.format_exc()))
		except:
			pass

