# This file is part of python-markups test suite
# License: BSD
# Copyright: (C) Dmitry Shachnev, 2012

from markups import MarkdownMarkup
import os
import unittest

tables_source = \
'''th1 | th2
--- | ---
t11 | t21
t12 | t22'''

tables_output = \
'''<table>
<thead>
<tr>
<th>th1</th>
<th>th2</th>
</tr>
</thead>
<tbody>
<tr>
<td>t11</td>
<td>t21</td>
</tr>
<tr>
<td>t12</td>
<td>t22</td>
</tr>
</tbody>
</table>
'''

deflists_source = \
'''Apple
:   Pomaceous fruit of plants of the genus Malus in 
    the family Rosaceae.

Orange
:   The fruit of an evergreen tree of the genus Citrus.'''

deflists_output = \
'''<dl>
<dt>Apple</dt>
<dd>Pomaceous fruit of plants of the genus Malus in 
the family Rosaceae.</dd>
<dt>Orange</dt>
<dd>The fruit of an evergreen tree of the genus Citrus.</dd>
</dl>
'''

mathjax_source = \
r'''$i_1$ some text \$escaped\$ $i_2$

\(i_3\) some text \(i_4\)

\\(escaped\)

$$m_1$$

\[m_2\]

\$$escaped\$$ \\[escaped\]
'''

mathjax_output = \
r'''<p><span class="math">$i_1$</span> some text \$escaped\$ <span class="math">$i_2$</span></p>
<p><span class="math">\(i_3\)</span> some text <span class="math">\(i_4\)</span></p>
<p>\(escaped)</p>
<p>
<div class="math">$$m_1$$</div>
</p>
<p>
<div class="math">\[m_2\]</div>
</p>
<p>\$$escaped\$$ \[escaped]</p>
'''

def create_extensions_txt(extensions_list):
	extensions_txt = open('markdown-extensions.txt', 'w')
	for extension in extensions_list:
		extensions_txt.write(extension+'\n')
	extensions_txt.close()

class MarkdownTest(unittest.TestCase):
	def test_extensions_loading(self):
		markup = MarkdownMarkup()
		self.assertFalse(markup._check_extension_exists('nonexistent'))
		self.assertTrue(markup._check_extension_exists('meta'))
	
	def test_extra(self):
		markup = MarkdownMarkup()
		html = markup.get_document_body(tables_source)
		self.assertEqual(tables_output, html)
		html = markup.get_document_body(deflists_source)
		self.assertEqual(deflists_output, html)
	
	def test_remove_extra(self):
		create_extensions_txt(['remove_extra'])
		markup = MarkdownMarkup()
		html = markup.get_document_body(tables_source)
		os.remove('markdown-extensions.txt')
		self.assertNotEqual(html, tables_output)
	
	def test_meta(self):
		create_extensions_txt(['meta'])
		markup = MarkdownMarkup()
		os.remove('markdown-extensions.txt')
		title = markup.get_document_title('Title: Hello, world!\n\nSome text here.')
		self.assertEqual('Hello, world!', title)
	
	def test_mathjax(self):
		create_extensions_txt(['mathjax'])
		markup = MarkdownMarkup()
		os.remove('markdown-extensions.txt')
		# Escaping should work
		self.assertEqual('', markup.get_javascript('Hello, \\$2+2$!'))
		js = markup.get_javascript(mathjax_source)
		self.assertTrue('<script' in js)
		body = markup.get_document_body(mathjax_source)
		self.assertEqual(mathjax_output, body)
	
	def tearDown(self):
		if os.path.exists('markdown-extensions.txt'):
			os.remove('markdown-extensions.txt')

if __name__ == '__main__':
	unittest.main()
