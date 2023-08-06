from . import gets
import sys
PYTHON_VERSION = sys.version_info[0]

if PYTHON_VERSION == 3:
	from urllib.request import Request, urlopen
	from urllib.parse import urlencode

else:
	from urllib import urlencode
	import urllib2










def get_url_status_py2(url, timeout=3, headers=None, data=None):
	req = urllib2.Request(url=url)
	if headers:
		for k, v in headers:
			req.add_header(k, v)

	data = urlencode(data).encode() if data else None

	f = urllib2.urlopen(req, timeout=timeout, data=data)
	status = f.getcode()
	f.close()
	return status




def get_url_status_py3(url, timeout=3, headers=None, data=None):
	req = Request(url=url)
	if headers:
		for k, v in headers:
			req.add_header(k, v)

	data = urlencode(data).encode() if data else None

	f = urlopen(req, timeout=timeout, data=data)
	status = f.getcode()
	f.close()
	return status



get_url_status = get_url_status_py3 if PYTHON_VERSION == 3 else get_url_status_py2













def get_url_py2(url, timeout=3, headers=None, autodecode=1, data=None):
	req = urllib2.Request(url=url)
	if headers:
		for k, v in headers:
			req.add_header(k, v)

	data = urlencode(data).encode() if data else None

	f = urllib2.urlopen(req, timeout=timeout, data=data)
	if autodecode:
		charset = gets(f.headers.get('content-type', '').lower(), 'charset=') or 'utf-8'
		return f.read().decode(charset)

	else:
		return f.read()




def get_url_py3(url, timeout=3, headers=None, autodecode=1, data=None):
	req = Request(url=url)
	if headers:
		for k, v in headers:
			req.add_header(k, v)

	data = urlencode(data).encode() if data else None

	f = urlopen(req, timeout=timeout, data=data)
	if autodecode:
		charset = gets(f.headers.get('content-type', '').lower(), 'charset=') or 'utf-8'
		return f.read().decode(charset)

	else:
		return f.read()



get_url = get_url_py3 if PYTHON_VERSION == 3 else get_url_py2
