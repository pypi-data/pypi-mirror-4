from cgi import escape as _escape
import re




def rm_tags(s):
	"""
		Usuwamy tagi HTML.
	"""
	if s is None: return ''
	s = s.replace('<sup>','(').replace('</sup>',')').replace('<sub>','(').replace('</sub>',')')
	return re.sub('<[^<>]*>', '', s)



def escape(s, new_line=1):
	s = _escape(s, True)
	s = s.replace('{', '&#123;').replace('}', '&#125;')
	if new_line:
		s = s.replace('\n','<br />')

	return s



def unescape(data):
	""" odwrotnosc escapowania HTML """
	return re.sub(r'&(#?[A-Za-z0-9]+?);', replace_entities, data)


def mk_links(data):
	""" dostawia tagi <a> w podanym tekscie tak by linki byly klikalne """
	return re.sub("(http://www\.|www\.|http://)([-A-Za-z0-9_]+(\.[-A-Za-z0-9_]+)+(:[0-9]*)?)((/[^\s]+[^._])?)","<a href=\"http://www.\\2\\5\">www.\\2\\5</a>", data)




def select(name, selected_values, options, id=None, **attrs):
	"""Create a dropdown selection box.

	* ``name`` -- the name of this control.

	* ``selected_values`` -- a string or list of strings or integers giving
	  the value(s) that should be preselected.

	* ``options`` -- an ``Options`` object or iterable of ``(value, label)``
	  pairs.  The label will be shown on the form; the option will be returned
	  to the application if that option is chosen.  If you pass a string or int
	  instead of a 2-tuple, it will be used for both the value and the label.
	  If the `value` is a tuple or a list, it will be added as an optgroup,
	  with `label` as label.

	``id`` is the HTML ID attribute, and should be passed as a keyword
	argument.  By default the ID is the same as the name.  filtered through
	``_make_safe_id_component()``.  Pass None to suppress the
	ID attribute entirely.


	  CAUTION: the old rails helper ``options_for_select`` had the label first.
	  The order was reversed because most real-life collections have the value
	  first, including dicts of the form ``{value: label}``.  For those dicts
	  you can simply pass ``D.items()`` as this argument.

	  HINT: You can sort options alphabetically by label via:
	  ``sorted(my_options, key=lambda x: x[1])``

	The following options may only be keyword arguments:

	* ``multiple`` -- if true, this control will allow multiple
	   selections.

	* ``prompt`` -- if specified, an extra option will be prepended to the
	  list: ("", ``prompt``).  This is intended for those "Please choose ..."
	  pseudo-options.  Its value is "", equivalent to not making a selection.

	Any other keyword args will become HTML attributes for the <select>.
	"""

	if not isinstance(selected_values, (list, tuple)): selected_values = [selected_values]
	selected_values = list(map(str,selected_values))

	assert isinstance(options, list), '`options` musi być listą'

	res = '<select name="%s"' % name
	if id: res += ' id="%s"' % id
	for k,v in attrs.items():
		if k == '_class': k = 'class'
		res += ' %s="%s"' % (k,v)

	res += '>'

	if not isinstance(options[0], (list, tuple)):
		options = [(x,x) for x in options]

	for v,l in options:
		if str(v) in selected_values:
			res += '<option value="%s" selected="selected">%s</option>' % (v,l)
		else:
			res += '<option value="%s">%s</option>' % (v,l)

	res += '</select>'
	return res










def tag(name, inner=None, s=None, c=None, id=None, args=''):
	if s: args += ' style="%s"' % s
	if c: args += ' class="%s"' % c
	if id: args += ' id="%s"' % id

	if inner is not None:
		if hasattr(inner, '__iter__'): inner = ''.join(inner)
		return '<%s%s>%s</%s>' % (name, args, inner, name)

	else:
		return '<%s%s />' % (name, args)


def div(inner, **kw):
	return tag('div', inner, **kw)


def span(inner, **kw):
	return tag('span', inner, **kw)


def span_color(inner, color_map, idx, **kw):
	return span(inner, s="color:%s"%color_map[idx])


def a(inner, **kw):
	args = ''
	if 'href' in kw:
		args += ' href="%s"' % kw['href']
		del kw['href']

	return tag('a', inner, args=args, **kw)


def html_and_body(inner, **kw):
	return '''<!DOCTYPE html>
<html lang="pl">
<head>
<title>%s</title>
<meta charset="utf-8">
<link href="/favicon.ico" rel="shortcut icon" type="image/x-icon" />
</head>%s</html>''' % (
	'title',
	tag('body', inner, *kw),
)


def table(inner, **kw):
	return tag('table', (
		tag('tr', (
			tag('td', td) for td in tr
		)) for tr in inner
	), **kw)


def button(value, submit=0, confirm='', onclick='', s=None):
	if onclick and submit: raise Exception('nie można używać jednocześnie submit i onclick')
	if submit and confirm:
		onclick = ' onclick="if(!confirm(\'%s\'))return false"' % confirm.replace('\n','\\n')

	elif onclick:
		if confirm:
			onclick = ' onclick="if(confirm(\'%s\')){%s}"' % (confirm.replace('\n','\\n'), onclick)

		else:
			onclick = ' onclick="%s"' % onclick

	style = ' style="%s"'%s if s else ''
	return '<input type="%s" value="%s" class="k-button"%s%s />' % ('submit' if submit else 'button', value, onclick, style)


def itext(name, value='', width='100%', maxlength=None, s=None, c=None, p=None):
	input_arg = ''
	if maxlength: input_arg += ' maxlength="%s"'%maxlength
	if p: input_arg += ' placeholder="%s"'%p
	value = '' if value is None else value

	s = 'width:%s;%s' % (width, s or '')
	c = 'k-widget k-autocomplete %s' % c or ''
	return '<div class="{}" style="{}"><input type="text" name="{}" value="{}" class="k-input" style="width:100%"{} data-bind="value: {}, valueUpdate: \'afterkeydown\'" /></div>'.format(c, s, name, value, input_arg, name)


def inum(name, value='', width='100%', min=None, max=None, s=None, c=None):
	input_arg = ''
	if min is not None: input_arg += ' min="%s"'%min
	if max is not None: input_arg += ' max="%s"'%max
	value = '' if value is None else value
	s = 'width:%s;%s' % (width, s or '')
	c = 'k-widget k-autocomplete %s' % c or ''
	return '<div class="{}" style="{}"><input type="number" name="{}" value="{}" class="k-input" style="width:100%"{} data-bind="value: {}, valueUpdate: \'afterkeydown\'" /></div>'.format(c, s, name, value, input_arg, name)


def ipassword(name, value='', width='100%', maxlength=None):
	input_arg = ''
	if maxlength: input_arg += ' maxlength="%s"'%maxlength
	value = '' if value is None else value
	return '<div class="k-widget k-autocomplete" style="width:{}"><input type="password" name="{}" value="{}" class="k-input" style="width:100%"{} /></div>'.format(width, name, value, input_arg)


def data_table(data_src, fields, **kw):
	if not data_src: return ''
	_table_class = ['k-widget','k-grid']
	if 'c' in kw: _table_class.append(kw['c'])
	if kw.get('tr_hover') and kw['tr_hover']: _table_class.append('tab-hover')
	res = '<table class="%s" style="width:100%%">' % ' '.join(_table_class)

	res += '<thead class="k-grid-header"><tr>'
	for label in (x[0] for x in fields):
		res += '<th data-field="%s" class="k-header">%s</th>' % (label, label)

	res += '</tr></thead><tbody>'

	row_tpl = '>%s</tr>' % ('<td>%s</td>'*len(fields))
	row_d = ', '.join(x[1] for x in fields)
	for i, r in enumerate(data_src):
		_tr_class = []
		if i%2!=0: _tr_class.append('k-alt')
		if kw.get('tr_select') and eval(kw['tr_select']): _tr_class.append('sel')
		res += '<tr class="%s"' % ' '.join(_tr_class)

		if kw.get('tr_click'):
			tmp = eval(kw['tr_click'])
			if tmp:
				res += ' style="cursor:pointer"'
				res += " onclick=\"parent.location='%s'\"" % tmp

		res += row_tpl % eval(row_d)

	res += '</tbody></table>'
	return res


def data_table_one(data_src, fields, **kw):
	if not data_src: return ''
	_table_class = ['k-widget','k-grid','tab-one']
	if kw.get('tr_hover') and kw['tr_hover']: _table_class.append('tab-hover')
	res = '<table class="%s" style="width:100%%"><tbody>' % ' '.join(_table_class)

	r = data_src
	for i, (label, tpl) in enumerate(fields):
		_tr_class = []
		if i%2!=0: _tr_class.append('k-alt')
		res += '<tr class="%s"' % ' '.join(_tr_class)
		res += '><th>%s:</th><td>%s</td></tr>' % (label, eval(tpl))

	res += '</tbody></table>'
	return res


def data_table_form(data_src, fields, **kw):
	if not data_src: return ''
	_table_class = ['k-widget','k-grid','tab-one']
	if kw.get('tr_hover') and kw['tr_hover']: _table_class.append('tab-hover')
	res = '<table class="%s" style="width:100%%"><tbody>' % ' '.join(_table_class)

	r = data_src
	for i, (label, name) in enumerate(fields):
		_tr_class = []
		if i%2!=0: _tr_class.append('k-alt')
		res += '<tr class="%s"' % ' '.join(_tr_class)
		res += '><th>%s:</th><td>%s</td></tr>' % (label, itext(name, getattr(r, name)))

	res += '</tbody></table>'
	return res



def box(inner):
	return '<div class="k-window" style="position:relative;width:100%;padding:0;background-color:#f6f6f6"><div style="padding:10px">' + inner + '</div></div>'



def pagination(ilosc_na_stronie, nr_aktualnej_strony, ilosc_na_aktualnej_stronie, aktualny_url, zmienna='p'):
	"""
		strony powinny być numerowane od '1', nie od '0'
	"""
	r = ''
	stron = nr_aktualnej_strony + 1 if ilosc_na_aktualnej_stronie == ilosc_na_stronie else nr_aktualnej_strony
	if stron == 1: return ''
	prev = 0
	for p in sorted(set([1]+[x for x in range(stron-4, stron+1) if x > 0])):
		if prev != p-1:
			r += '<span>...</span>'

		if p == nr_aktualnej_strony:
			r += '<span class="current-page">{p}</span>'.format(p=p)

		else:
			r += '<a href="?p={p}">{p}</a>'.format(p=p)

		prev = p

	if ilosc_na_aktualnej_stronie == ilosc_na_stronie:
		r += '<span>...</span><a href="?p={p}">następna strona</a>'.format(p=p)

	return '<div class="pagination">%s</div>'%r



class Paginator:

	def __init__(self, db_query, req, var='p', on_page=10):
		"""
			klasa ulatwiająca obsługę stronicowania zapytań
			użycie:
			p = Paginator(
				db.query(db.News),
				req = req,
			)
			items = p.page_items   # return list of items for current page
			p.buttons
		"""
		self.on_page = on_page								# ile na jednej stronie
		self.var = var
		self.url = req.request.path_str
		self.page = req.data(self.var, 'int', 1)
		if self.page < 1: self.page = 1

		self.page_items = db_query.limit(self.on_page).offset((self.page-1)*self.on_page).all()

		self.buttons = pagination(
			self.on_page,
			self.page,
			len(self.page_items),
			self.url,
			self.var,
		)















'''


print(html_and_body((
	div((
		a('biuro@nri.pl', href='mailto:biuro@nri.pl'),
		' &nbsp; &nbsp; ',
		span('tel.',  s="font-size:.8em"),
		a('pokaż stronę »', href='/', c='showsite'),
	), id='fl-head'),

	div((
		a(v, href='/fl-panel%s'%('?m=%s'%k if k else ''), c='hl' if k=='logo' else None) for k,v,img in MENU
	), id='fl-menu')
)))
'''


'''
<div id="fl-head"><a href="mailto:biuro@nri.pl">biuro@nri.pl</a> &nbsp; &nbsp; <span style="font-size:.8em">tel.</span> 797 782 978<a href="/" class="showsite">pokaż stronę »</a></div>
	<div id="fl-menu">
		{% for k,v,img in menu %}
			{% if k == '' %}
				<a href="/fl-panel"{% print ['',' class="hl"'][menu_hl==''] %}>{{v}}</a>
			{% else %}
				<a href="/fl-panel?m={{k}}"{% print ['',' class="hl"'][menu_hl==k] %}>{{v}}</a>
			{% endif %}
		{% endfor %}
	</div>
'''