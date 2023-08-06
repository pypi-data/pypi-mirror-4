#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8

from django.utils.translation import ugettext_lazy as _ # Internacionalization
from django.db.models import *
from django.contrib.contenttypes.models import ContentType

# Gets the translation of a field or related field name
def getFieldVerboseName(qs,field):
	try:
		# Find qs non related model fields
		if '__' not in field:
			return _(qs.model._meta.get_field(field).verbose_name)
				

		# Find the related model field
		else:	
			related_model,field = field.split('__')[-2],field.split('__')[-1]
		try:
			return _(qs.model._meta.get_field(related_model).rel.to._meta.get_field(field).verbose_name)
		except:
			ct=ContentType.objects.get(model=related_model)
			return get_model(ct.app_label,ct.model)._meta.get_field(field).verbose_name
	except:
		return field.replace('_',' ').capitalize()
