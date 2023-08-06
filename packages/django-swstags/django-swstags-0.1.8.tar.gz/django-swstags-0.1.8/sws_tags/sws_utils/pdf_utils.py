from os import fdopen, remove
from subprocess import Popen, PIPE, CalledProcessError
from tempfile import mkstemp

from django.conf import settings
from django.http import HttpResponse
from django.template import loader
from django.utils.encoding import smart_str

WKHTMLTOPDF_CMD = getattr(settings, 'WKHTMLTOPDF_CMD', 'wkhtmltopdf')

class CalledProcessDetailedError(CalledProcessError):
	def __init__(self, returncode, cmd, process_output):
		CalledProcessError.__init__(self, returncode, cmd)
		self.process_output = process_output.lstrip()
	def __str__(self):
		return CalledProcessError.__str__(self) + "\n%s" % self.process_output


def wkhtmltopdf(pages, output=None, **kwargs):
	"""
	Converts html to PDF using http://code.google.com/p/wkhtmltopdf/.

	pages: List of file paths or URLs of the html to be converted.
	output: Optionsal output file path.
	**kwargs: Passed to wkhtmltopdf via _extra_args() (See
			  https://github.com/antialize/wkhtmltopdf/blob/master/README_WKHTMLTOPDF
			  for acceptable args.)
			  Kwargs is passed through as arguments. e.g.:
				  {'footer_html': 'http://example.com/foot.html'}
			  becomes
				  '--footer-html http://example.com/foot.html'
			  Where there is no value passed, use a blank string. e.g.:
				  {'disable_javascript': ''}
			  becomes:
				  '--disable-javascript '

	example usage:
		wkhtmltopdf(html_path="~/example.html",
					dpi=300,
					orientation="Landscape",
					disable_javascript="")
	"""

	def _extra_args(**kwargs):
		"""Converts kwargs into a string of flags to be passed to wkhtmltopdf."""
		flags = ''
		for k, v in kwargs.items():
			flags += ' --%s %s' % (k.replace('_', '-'), v)
		return flags

	if not isinstance(pages, list):
		pages = [pages]

	kwargs['quiet'] = ''
	kwargs['javascript-delay'] = 3000
	args = '%s %s %s %s' % (WKHTMLTOPDF_CMD, _extra_args(**kwargs), ' '.join(pages), output or '-')
	# print args
	process = Popen(args, stdout=PIPE, stderr=PIPE, shell=True)
	stdoutdata, stderrdata = process.communicate()

	if process.returncode != 0:
		# combined_program_output = "stdout: %s\nstderr: %s" % (stdoutdata, stderrdata)
		# raise CalledProcessDetailedError(process.returncode, args, combined_program_output)

		output = stdoutdata
		return output
		
	
	if output is None:
		output = stdoutdata

	return output

def render_to_pdf(template_name, dictionary=None, context_instance=None, header_template=None, footer_template=None, **kwargs):
	"""Renders a html template as a PDF response."""

	filename = kwargs.pop('filename', None)

	page_path = template_to_temp_file(template_name, dictionary, context_instance)

	tmp_files = []
	if header_template is not None:
		kwargs['header_html'] = template_to_temp_file(header_template, dictionary, context_instance)
		tmp_files.append(kwargs['header_html'])
	if footer_template is not None:
		kwargs['footer_html'] = template_to_temp_file(footer_template, dictionary, context_instance)
		tmp_files.append(kwargs['footer_html'])

	content = wkhtmltopdf([page_path], **kwargs)

	for path in tmp_files:
		remove(path)

	response = HttpResponse(content, mimetype='application/pdf')
	if filename is not None:
		response['Content-Disposition'] = 'attachment;' + ' filename=%s' %filename
	return response


def template_to_temp_file(*args, **kwargs):
	"""Renders a template to a temp file, and returns the path of the file."""
	fd, tmppath = mkstemp(suffix='.html')
	f = fdopen(fd, 'wt')
	f.write(smart_str(loader.render_to_string(*args, **kwargs)))
	f.close()
	return tmppath

#wkhtmltopdf()

# #########################################################################################################
# #########################################################################################################
# ############################################### PHANTOMJS ###############################################
# #########################################################################################################
# #########################################################################################################
import subprocess
from django.shortcuts import get_object_or_404, render_to_response

# JS_PATH  = settings.JS_PATH
JS_PATH  = '/home/patilla/projects/ooint/static/js/htmlToPdf.js'

# New function to render HTML as PDF
def phantomjs_pdf(template,context_instance):

	page_path = template_to_temp_file(template, context_instance)

	command = 'phantomjs {0} {1} /tmp/payment_{2}.pdf'.format(JS_PATH, page_path, context_instance['payment'])
	# print 'command =',command

	try:
		subprocess.check_call(command,shell=True)
	except:
		raise

	filename = None
	filename = 'payment_{0}.pdf'.format(context_instance['payment'])

	response = HttpResponse(filename, mimetype='application/pdf')

	if filename is not None:
		response['Content-Disposition'] = 'attachment;' + ' filename=%s' %filename
	return response
