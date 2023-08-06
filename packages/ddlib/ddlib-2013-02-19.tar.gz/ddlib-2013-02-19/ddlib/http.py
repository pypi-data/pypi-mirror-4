from . import gets
import sys
PYTHON_VERSION = sys.version_info[0]

if PYTHON_VERSION == 3:
	from urllib.request import Request, urlopen

else:
	import urllib2








def get_url_py2(url, timeout=3, headers=None):
	req = urllib2.Request(url=url)
	if headers:
		for k, v in headers:
			req.add_header(k, v)

	f = urllib2.urlopen(req, timeout=timeout)
	charset = gets(f.headers.get('content-type', '').lower(), 'charset=') or 'utf-8'
	return f.read().decode(charset)




def get_url_py3(url, timeout=3, headers=None):
	req = Request(url=url)
	if headers:
		for k, v in headers:
			req.add_header(k, v)

	f = urlopen(req, timeout=timeout)
	charset = gets(f.headers.get('content-type', '').lower(), 'charset=') or 'utf-8'
	return f.read().decode(charset)



get_url = get_url_py3 if PYTHON_VERSION == 3 else get_url_py2
