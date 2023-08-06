#!/usr/bin/env python
# encoding: utf-8

import csv
from django.http import HttpResponse
from django.template import loader, Context
from decimal import Decimal
import datetime

# FOR EXCEL GENERATING
import xlwt
ezxf = xlwt.easyxf

from sws_tags.sws_utils.common_utils import *

def get_field_types(fields):
	# fields = self.fields
	field_types = []
	prev_len = 0
	found = False
	# print 'fields =',fields
	for lf in fields:
		found = False

		if type(lf) == unicode:
			field_types.append('text')
			found = True
		elif type(lf) == long:
			field_types.append('int')
			found = True
		elif type(lf) == int:
			field_types.append('int')
			found = True
		elif type(lf) == bool:
			field_types.append('boolean')
			found = True
		elif type(lf) == float: 
			field_types.append('price')
			found = True
		elif type(lf) == Decimal: 
			field_types.append('price')
			found = True                    
		elif type(lf) == datetime.date: 
			field_types.append('date')
			found = True                
		elif type(lf) == datetime.datetime: 
			field_types.append('date')
			found = True              
		if found is not True: 
			field_types.append('text')

	return field_types


def get_csv(request, data, fields_name, filename):
	try:
		# csv_file = open(filename,"w")
		csv_file = HttpResponse()

		# csv_writer = csv.writer(csv_file, dialect='excel', quoting=csv.QUOTE_MINIMAL, delimiter='|')
		csv_writer = csv.writer(csv_file, dialect='excel', quoting=csv.QUOTE_MINIMAL)
		csv_writer.writerow(fields_name)

		for row in data:
			# print row
			csv_writer.writerow(row)							
								
		# csv_file.close()
		return csv_file

	except Exception, e:
		# print 'e ---->',e
		return False


def get_csv_query(request, queryset, filename, col_order = None):
	try:
		# csv_file = open(filename,"w")
		csv_file = HttpResponse()

		csv_writer = csv.writer(csv_file, dialect='excel', quoting=csv.QUOTE_MINIMAL, delimiter='|')

		if type(queryset)!=list:
			q = queryset[0]

			fields_name = []
			for f in queryset._fields:
				fields_name.append(unicode(getFieldVerboseName(queryset,f)))
			for f in queryset.aggregate_names:
				fields_name.append(f)
			data = []
			# Fill the list of lists with data
			for i, q in enumerate(queryset):
				aux = []
				for f in queryset._fields:
					aux.append(q[f])
				for f in queryset.aggregate_names:
					aux.append(q[f])
				data.append(aux)
		else:
			fields_name = []
			if col_order:
				fields_name=col_order
			else:
				for k,v in queryset[0].items():
					fields_name.append(unicode(k))

			data = []

			for q in queryset:
				v_data=[]
				for k in fields_name:
					v_data.append(q[k])
				data.append(v_data)

		csv_writer.writerow(fields_name)

		for row in data:
			csv_writer.writerow(row)							
								
		# csv_file.close()
		return csv_file

	except Exception, e:
		# print 'e ---->',e
		return False


def get_excel(request, data, name, fields, fields_name):

	response = HttpResponse()
	heading_xf = ezxf('font: bold on; pattern: pattern solid, fore-colour grey25; align: wrap on, vert centre, horiz center')
	kind_to_xf_map = {
		'date': ezxf(num_format_str='yyyy-mm-dd HH:MM'),
		'int': ezxf(num_format_str='#,##0'),
		'money': ezxf('font: italic on; pattern: pattern solid, fore-colour grey25',
			num_format_str='€#,##0.00'),
		'price': ezxf(num_format_str='#0.000000'),
		'text': ezxf(),
		'boolean': ezxf(),
	}

	data_xfs = [kind_to_xf_map[k] for k in get_field_types(fields)]

	# self.get_xls(response, self.get_caption().replace('/','_').replace(' ','_')[0:31], real_field_names, data, heading_xf, data_xfs)

	get_xls(response, name, fields_name, data, heading_xf, data_xfs)
	return response

# In this version data, fileds, and fields_name come all together in form of a queryset
# queryset must be such as: Clients.objects.filter().values('id', 'client')
def get_excel_query(request, queryset, name, col_order = None):
	response = HttpResponse()
	heading_xf = ezxf('font: bold on; pattern: pattern solid, fore-colour grey25; align: wrap on, vert centre, horiz center')
	kind_to_xf_map = {
		'date': ezxf(num_format_str='yyyy-mm-dd HH:MM'),
		'int': ezxf(num_format_str='#,##0'),
		'money': ezxf('font: italic on; pattern: pattern solid, fore-colour grey25',
			num_format_str='€#,##0.00'),
		'price': ezxf(num_format_str='#0.000'),
		'text': ezxf(),
		'boolean': ezxf(),
	}


	# Get the first row of the queryset in order to get the field types

	if type(queryset)!=list:
		q = queryset[0]

		fields = []
		for f in queryset._fields:
			fields.append(q[f])

		for f in queryset.aggregate_names:
			fields.append(q[f])

		# Get the unicode translation of the columns for the header
		fields_name = []

		for f in queryset._fields:
			fields_name.append(unicode(getFieldVerboseName(queryset,f)))

		# Add field annotate
		for i in queryset.aggregate_names:
			fields_name.append(i)

		# Map data types
		data_xfs = [kind_to_xf_map[k] for k in get_field_types(fields)]

		data = []

		# Fill the list of lists with data
		for i, q in enumerate(queryset):
			aux = []
			for f in queryset._fields:
				aux.append(q[f])
			for f in queryset.aggregate_names:
				aux.append(q[f])
			data.append(aux)
	else:
		data_xfs = [kind_to_xf_map[k] for k in get_field_types(queryset[0])]

		fields_name = []
		if col_order:
			fields_name=col_order
		else:
			for k,v in queryset[0].items():
				fields_name.append(unicode(k))

		data = []

		for q in queryset:
			v_data=[]
			for k in fields_name:
				v_data.append(q[k])
			data.append(v_data)

	get_xls(response, name, fields_name, data, heading_xf, data_xfs)
	return response

def get_xls(file_name, sheet_name, headings, data, heading_xf, data_xfs):
	book = xlwt.Workbook()
	sheet = book.add_sheet(sheet_name)
	rowx = 0

	# Create heading for table
	for colx, value in enumerate(headings):
		sheet.write(rowx, colx, value, heading_xf)

	sheet.set_panes_frozen(True) # frozen headings instead of split panes
	sheet.set_horz_split_pos(rowx+1) # in general, freeze after last heading row
	sheet.set_remove_splits(True) # if user does unfreeze, don't leave a split there
	
	# Fill table with values
	# Instead of a dict we will use a list of lists (ordered)
	for row in data:
		rowx += 1
		# for v in row:
		for colx, value in enumerate(row):
			sheet.write(rowx, colx, value, data_xfs[colx])

	# book.save('/tmp/patilla.xls')
	book.save(file_name)

def get_excel(self, request):
	items = self.get_items_csv(request)

	data = items.values_list(*self.get_field_names())
	# FIX: doesn't work with related fields
	real_field_names =  [unicode(_(field)) for field in self.get_field_caption()]
	response = HttpResponse()
	heading_xf = ezxf('font: bold on; pattern: pattern solid, fore-colour grey25; align: wrap on, vert centre, horiz center')
	kind_to_xf_map = {
		'date': ezxf(num_format_str='yyyy-mm-dd HH:MM'),
		'int': ezxf(num_format_str='#,##0'),
		'money': ezxf('font: italic on; pattern: pattern solid, fore-colour grey25',
			num_format_str='€#,##0.00'),
		'price': ezxf(num_format_str='#0.000000'),
		'text': ezxf(),
		'boolean': ezxf(),
	}
	data_xfs = [kind_to_xf_map[k] for k in self.get_field_types()]



	self.get_xls(response, self.get_caption().replace('/','_').replace(' ','_')[0:31], real_field_names, data, heading_xf, data_xfs)
	return response

	
def get_csv(self, request):
	items = self.get_items_csv(request)
	data = items.values_list(*self.get_field_names())
	real_field_names =  [unicode(_(field)) for field in self.get_field_caption()]
	response = HttpResponse()
	csv_writter = csv.writer(response, dialect='excel', quoting=csv.QUOTE_MINIMAL)
	csv_writter.writerow(self.get_field_names())
	n_row = []

	for row in data:
		for cell in row:
			if type(cell) is unicode: cell = cell.encode('utf-8')
			n_row.append(cell)
		csv_writter.writerow(n_row)
		n_row = []
	return response

