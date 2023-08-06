#!/usr/bin/env python
# encoding: utf-8
"""
Created by Miguel A. Sanchez on 2012-10-05.
Copyright (c) 2010 StoneWorkSolutions. All rights reserved.
"""
import django.db.models
from django.contrib.sites.models import Site
from django import template
from django.utils.translation import ugettext_lazy as _
from sws_tags.sws_utils.highcharts import *
import time
import logging
from decimal import Decimal
from sws_tags.sws_utils.common_utils import *


logger = logging.getLogger('django')

register = template.Library()

ROWS_TO_EVALUATE = 25


@register.inclusion_tag('tags/tag_filters.html')
def tag_filters(view_name,filters,shortcuts='false',vertical='false',shortcuts_select='today'):
	return {'view_name':view_name,'filters': filters, 'shortcuts':shortcuts,'vertical':vertical,'shortcuts_select':shortcuts_select}

@register.inclusion_tag('tags/tag_filters_select2.html')
def tag_filters_select2(view_name,dimension_filters,URL_FILTERS_CUVE,shortcuts='false',vertical='false',day_from=1,name='',shortcuts_default='today'):
	return {'view_name':view_name,'dimension_filters': dimension_filters,'URL_FILTERS_CUVE':URL_FILTERS_CUVE ,'shortcuts':shortcuts,'vertical':vertical,'day_from':day_from,'name':name,'shortcuts_default':shortcuts_default}


@register.inclusion_tag('tags/tag_shortcuts.html')
def tag_shortcuts(view_name,shortcuts=None,shortcuts_select='today'):

	# Shortcut translations
	shortcuts_trans = {
					'10m':			_('10 minutes'),
					'30m':			_('30 minutes'),
					'1h':			_('1 hour'),
					'2h':			_('2 hours'),
					'3h':			_('3 hours'),
					'6h':			_('6 hours'),
					'12h':			_('12 hours'),
					'24h':			_('24 hours'),
					'today': 		_('Today'),
					'yesterday':	_('Yesterday'),
					'week':			_('Curr. week'),
					'month':		_('Curr. month'),
					'pweek':		_('Prev. week'),
					'pmonth':		_('Prev. month'),
					'lastseven':	_('Last 7 days'),
					'lastthirty':	_('Last 30 days'),
					'all':			_('All'),

	}

	shortcuts_list = []

	# Define the order of the shortcuts
	shortcuts_order = ['10m','30m','1h','2h','3h','6h','12h','24h', 'today','yesterday','week','lastseven','pweek','month','lastthirty','pmonth','all']

	if shortcuts != None:
		# Assign the translation to the received shortcuts list
		for s in shortcuts_order:
			if s in shortcuts:
				shortcuts_list.append((s,shortcuts_trans[s]))
	return {'view_name':view_name,'shortcuts':shortcuts_list,'shortcuts_select':shortcuts_select}



@register.inclusion_tag('tags/tag_refresh_time.html')
def tag_refresh_time(view_name,refresh_time):
	return {'view_name':view_name,'refresh_time':refresh_time}


# def tag_grid(view_name,queryset,jsonReader_id,sortname,URL_GRID,multiselect=None):
@register.inclusion_tag('tags/tag_grid.html')
def tag_grid(view_name,queryset,jsonReader_id,sortname,URL_GRID,multiselect = 'false',footerrow = 'false',adjustment_factor=1,col_order='false',middle_col='false',row_num=200,checkboxColumn='false',subGrid='false'):

	col_name=[]
	col_model=[]
	col_name,col_model = getGridConfig(queryset,adjustment_factor,col_order,middle_col)

	if checkboxColumn != 'false':
		col_name.append('Select multiple')
		col_model.append({'width':1,'align':'center','name':'check_column', 'editable':'true', 'edittype':'checkbox', 'editoptions': { 'value':"True:False"}, 'formatter': "checkbox", 'formatoptions': {'disabled' : 'false'}})

	# col_name =  ['Client', 'Destino', 'Llamadas', 'Calls not tarified', 'Moneda', 'Total Reseller', 'Total Admin', 'Total Client', 'Total Superreseller', 'Minutos']
	# col_model = [{'width': 1, 'align': 'center', 'name': 'client__client'}, {'width': 1, 'align': 'center', 'name': 'destination__destination'},{'width': 1, 'align': 'center', 'name': 'calls'}, {'width': 1, 'align': 'center', 'name': 'non_calls'}, {'width': 1, 'align': 'center', 'name': 'admin_income_currency'}, {'width': 1, 'align': 'center', 'name': 'total_reseller_income'}, {'width': 1, 'align': 'center', 'name': 'total_admin_income'}, {'width': 1, 'align': 'center', 'name': 'total_client_income'}, {'width': 1, 'align': 'center', 'name': 'total_superreseller_income'}, {'width': 1, 'align': 'center', 'name': 'minutes'}]



	return {'view_name':view_name,'URL_GRID':URL_GRID,'col_name':col_name,'col_model':col_model,'jsonReader_id':jsonReader_id,'sortname':sortname,'multiselect':multiselect,'footerrow':footerrow,'row_num':row_num,'subGrid':subGrid}


@register.inclusion_tag('tags/tag_group_by.html')
def tag_group_by(view_name,grid_name,queryset,group_by, col1=None,index1=0,col2=None,index2=1 ,input_select = 'button',URL_GRID=None,):
	return {'queryset':queryset,'view_name': view_name,'grid_name':grid_name,'group_by':group_by, 'col1':col1,'index1':index1,'index2':index2,'col2':col2,'URL_GRID':URL_GRID,'input_select':input_select}


@register.inclusion_tag('tags/tag_excel_csv.html')
def tag_excel_csv(view_name,URL_EXCEL):
	return {'view_name': view_name,'URL_EXCEL':URL_EXCEL}


@register.inclusion_tag('tags/tag_highcharts.html')
def tag_highcharts(view_name,data_highcharts):
	
	# print 'TAG HIGCHARTS'

	title = data_highcharts['title']

	position = data_highcharts['position']

	xAxis=data_highcharts['xAxis']

	v_name_y = data_highcharts['v_name_y']
	v_dataname= data_highcharts['v_dataname']
	yAxis = get_yAxis(v_name_y,v_dataname)

	v_name = data_highcharts['v_name']
	v_type= data_highcharts['v_type']
	v_yAxis= data_highcharts['v_yAxis']
	v_data= data_highcharts['v_data']

	series = get_series(v_name,v_type,v_yAxis,v_data)

	# series = get_series(v_name,v_type,v_yAxis,v_data)
	return {'view_name': view_name,'title':title,'position':position,'xAxis':xAxis,'yAxis':yAxis,'series':series}

@register.inclusion_tag('tags/tag_highstock.html')
def tag_highstock(view_name,URL_HIGHSTOCK,data_highcharts):
	return {'view_name': view_name,'URL_HIGHSTOCK':URL_HIGHSTOCK}

@register.inclusion_tag('tags/tag_highstock2.html')
def tag_highstock2(view_name,URL_HIGHSTOCK,data_highcharts):
	v_name_y = data_highcharts['v_name_y']
	v_dataname= data_highcharts['v_dataname']
	yAxis = get_yAxis(v_name_y,v_dataname)
	return {'view_name': view_name,'URL_HIGHSTOCK':URL_HIGHSTOCK,'yAxis':yAxis}

@register.inclusion_tag('tags/tag_csvupload.html')
def tag_csvupload(view_name,UPLOAD_FORM,VALIDATE_FORM,URL_CSVUPLOAD):
	return {'view_name': view_name,'UPLOAD_FORM':UPLOAD_FORM,'VALIDATE_FORM':VALIDATE_FORM,'URL_CSVUPLOAD':URL_CSVUPLOAD}


@register.inclusion_tag('tags/tag_slider.html')
def tag_slider(view_name,name_slider,text_slider,position,rang,min_val,max_val,default_min,default_max,unit):
	return {'view_name': view_name,'name_slider':name_slider,'text_slider':text_slider,'position':position,'rang':rang,'min_val':min_val,'max_val':max_val,'default_min':default_min,'default_max':default_max,'unit':unit}

@register.inclusion_tag('tags/tag_button.html')
def tag_button(view_name,button_name,button,default='false',input_select='button',text_button='Select'):
	return {'view_name': view_name,'button':button,'default':default,'input_select':input_select,'text_button':text_button,'button_name':button_name}

@register.inclusion_tag('tags/tag_table.html')
def tag_table(view_name,table_dict):
	return {'view_name': view_name,'table_dict':table_dict}


@register.inclusion_tag('tags/tag_mail.html')
def tag_mail(view_name,mail,period,URL_MAIL):
	return {'view_name':view_name,'mail':mail,'period':period,'URL_MAIL':URL_MAIL}


@register.inclusion_tag('tags/grid.html')
def show_grid(grid):
	return {'code': grid}



@register.inclusion_tag('tags/grid.html')
def show_grid_p(grid, column=None):
	if column == '': return show_grid(grid)
	else: return {'code': grid, 'column': column}

def get_field_type(field):
	# fields = self.field
	# print 'fields =',fields
	try:
		if type(field) == unicode:
		 	return ''
		elif type(field) == long:
		 	return 'integer'
		elif type(field) == int:
		 	return 'integer'
		elif type(field) == float: 
			return 'number'
		elif type(field) == Decimal: 
			return 'currency'
		return ''
	except:
		return ''

	return field_types

def getLenMiddle(queryset,col_model):
	dic_len_middle={}
	number_element = queryset.count()
	if number_element > ROWS_TO_EVALUATE:
		number_element = ROWS_TO_EVALUATE

	if number_element == 0:
		dic_len_middle[0]=0
		# raise
	else:
		total_len=0
		for tupla in queryset:
			for q in col_model:
				if q not in dic_len_middle:
					dic_len_middle[q]=0
				value = tupla[q]
				if type(tupla[q]) in [float,Decimal]:
					value=round(value,2)
				dic_len_middle[q] += len(str(value))
		for k,v in dic_len_middle.iteritems():
			dic_len_middle[k]=dic_len_middle[k]/number_element
	return dic_len_middle

def getGridConfig(queryset,adjustment_factor,col_order='false',middle_col = 'false'):

	col_name=[]	
	col_model=[]
	col_len = []
	dic_col_model=[]
	col_types=[]

	col_translations={
		'minutes': _('Minutes'),
		'total_reseller_income':_('Total Reseller'),
	 	'total_admin_income':_('Total Admin'),	 
		'total_client_income':_('Total Client'),
	 	'total_superreseller_income':_('Total Superreseller'),
	 	'calls':_('Llamadas'),
	 	'std_income':_('Standard Income'),
	 	'destination':_('Destination'),
	 	'cli_income':_('Client Income'),
	 	'client':_('Client'),
	 	'routetable':_('Route Table'),
	}

	group_by_order = ['minutes','calls','total_reseller_income','total_admin_income','total_client_income','total_superreseller_income']

	if type(queryset) == django.db.models.query.ValuesQuerySet:
		for i in queryset.field_names:
			if i != 'id':
				col_name.append(str(unicode(getFieldVerboseName(queryset,i))))
				col_model.append(i)
		for i in queryset.aggregate_names:
			if i in group_by_order:
				col_name.append(str(unicode(col_translations[i])))
			else:
				col_name.append(i)
			
			col_model.append(i)
		for i in queryset.extra_names:
			if i in group_by_order:
				col_name.append(str(unicode(col_translations[i])))
			else:
				col_name.append(i)
			
			col_model.append(i)
	# Instead of a queryset we receive a list of tuples ('Name','field')
	elif type(queryset) == list:
		try:
			if type(queryset[0]) == tuple:
				for i in queryset:
					col_name.append(str(unicode(i[0])))
					col_model.append(i[1])
					col_len.append(i[2])



			elif type(queryset[0]) == dict:
				for i in queryset[0].keys():
					if i in col_translations:
						col_name.append(str(unicode(col_translations[i])))
					else:
						col_name.append(str(unicode(getFieldVerboseName(queryset,i))))					
					col_model.append(i)
		except:
			logger.error(' getGridConfig: error in len column')


	# Instead of a queryset we receive a dict {'Name':'field'}
	elif type(queryset) == dict:
		for i,j in queryset.items():
			col_name.append(i)
			col_model.append(j)
	





	if middle_col == 'false':

		if type(queryset) == django.db.models.query.ValuesQuerySet:
			try:
				for i in range(0,len(col_model)):
					dic_col_model.append({'name':col_model[i],
										'width':1,
										'align':'center',
										})
			except:
				logger.error('getGridConfig: error in asignation len a column of grid')
		elif type(queryset) == list or dict:
			if len(col_len)>0:
				try:
					for i in range(0,len(col_model)):
						dic_col_model.append({'name':col_model[i],
											'width':col_len[i],
											'align':'center',
											})
				except:
					logger.error('getGridConfig: error in asignation len a column of grid')
			else:
					for i in range(0,len(col_model)):
						dic_col_model.append({'name':col_model[i],
											'width':1,
											'align':'center',
											})

		else:
			for i in col_model:
				dic_col_model.append({'name':i,
									'width':1,
									'align':'center',
									'formatter': get_field_type(queryset[0][i])
									})

	else:		
		lenMidle=getLenMiddle(queryset,col_model)
		lenTotal = 0


		for i,k in lenMidle.items():
			if k=='0':
				lenMidle = 'false'
			else:
				lenTotal = lenTotal + k;

		lenTotal = lenTotal / len(lenMidle)

		try:	
			for i in col_model:
				if lenTotal> lenMidle[i]:
					dic_col_model.append({'name':i,
										'width':lenTotal*adjustment_factor,
										'align':'center',
										# 'formatter': get_field_type(queryset[0][i])
										}) 
				else:
					dic_col_model.append({'name':i,
										'width':lenMidle[i],
										'align':'center',
										# 'formatter': get_field_type(queryset[0][i])
										})
		except:
			for i in col_model:
				dic_col_model.append({'name':i,
								'width':1,
								'align':'center',
								# 'formatter': get_field_type(queryset[0][i])
								}) 
			logger.error(' getGridConfig: data passed: lenMidle = {0} lenTotal = {1}'.format(lenMidle,lenTotal))	
			# print 'getGridConfig: data passed: lenMidle = {0} lenTotal = {1}'.format(lenMidle,lenTotal)

	col_model = dic_col_model
	


	# print 'COL_NAME',col_name
	# print 'COL_MODEL',col_model
	try:
		if col_order != 'false':
			col_model = dic_col_model
			col_model_order=[]
			col_name_order=[]

			for i_order in col_order:
				for col in col_model:
					for i,k in col.items():
						if k == i_order:
							col_model_order.append(col)
							trad = ''
							j = i_order
							if i in col_translations:
								trad = unicode(col_translations[j])
							else:
								trad = str(unicode(getFieldVerboseName(queryset,j)))

							col_name_order.append(trad)

							if trad == '':
								trad = j
			col_name = col_name_order
			col_model = col_model_order
	except:
		logger.error('getGridConfig: order gridname and order gridmodel')
		# print 'getGridConfig: order gridname and order gridmodel'
	return col_name,col_model


@register.inclusion_tag('tags/tag_interruptor.html')
def tag_interruptor(view_name,
					interruptor_name,
					name_text,
					callback,
					default_position = 'OFF',
					default_name_OFF = 'OFF',
					default_name_ON='ON'):

	return {'view_name':view_name,
			'interruptor_name':interruptor_name,
			'name_text':name_text,
			'callback':callback,
			'default_position':default_position,
			'default_name_OFF':default_name_OFF,
			'default_name_ON':default_name_ON}
