#! /usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2013 Thomas Chiroux
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.
# If not, see <http://www.gnu.org/licenses/lgpl-3.0.html>
#

__authors__ = [
    # alphabetical order by last name
    'Thomas Chiroux', ]

from pygments import highlight
from pygments.lexers import XmlLexer
from pygments.formatters import HtmlFormatter
from bottle import route, run, request, template
import lxml.etree as etree
import difflib

PAGE_TPL = """<html>
<head>
<title>xml highlighter</title>
<style type="text/css">
    body { font-style: monotype; }
    body h1 { font-size: small; }
    .left {  }
    .right {  }
    .diff { font-size: x-small; }
    table.diff {font-family:Courier; border:medium;}
    .diff_header {background-color:#e0e0e0}
    td.diff_header {text-align:right}
    .diff_next {background-color:#c0c0c0}
    .diff_add {background-color:#aaffaa}
    .diff_chg {background-color:#ffff77}
    .diff_sub {background-color:#ffaaaa}
</style>
<style type="text/css">
    {{!highlight_style}}
</style>
</head>
<body>
%if highlight_left:
<h1>xml left</h1>
<div class="left">
{{!highlight_left}}
</div>
%end
%if highlight_right:
<h1>xml right</h1>
<div class="right">
{{!highlight_right}}
</div>
%end
%if diff:
<h1>diff</h1>
<div class="diff">
{{!diff}}
</div>
%end

<h1>input</h1>
<div class="form">
<form action="/upload" method="post">
  <textarea rows="10" cols="80" name="content_left">{{!text_left}}</textarea>
  <textarea rows="10" cols="80" name="content_right">{{!text_right}}</textarea>
  <p><input type="submit"/></p>
</form>
</div>

</body>
</html>"""


@route('/')
@route('/index.html')
def index():
    return template(PAGE_TPL,
                    highlight_style='',
                    highlight_left='',
                    highlight_right='',
                    diff='',
                    text_left='',
                    text_right='')


@route('/upload', method='POST')
def pretty_print():
    code_left = request.forms.content_left
    if code_left is not None and code_left != "":
        tree_left = etree.fromstring(code_left)
        pprint_left = etree.tostring(tree_left, pretty_print=True)
        highlight_left = highlight(pprint_left,
                               XmlLexer(),
                               HtmlFormatter())
    else:
        code_left = ""
        pprint_left = ""
        highlight_left = ""

    code_right = request.forms.content_right
    if code_right is not None and code_right != "":
        tree_right = etree.fromstring(code_right)
        pprint_right = etree.tostring(tree_right, pretty_print=True)
        highlight_right = highlight(pprint_right,
                                    XmlLexer(),
                                    HtmlFormatter())
    else:
        code_right = ""
        pprint_right = ""
        highlight_right = ""

    if pprint_left and pprint_right:
        diff = difflib.HtmlDiff(wrapcolumn=100)
        diff_html = diff.make_table(pprint_left.split('\n'),
                                    pprint_right.split('\n'))
    else:
        diff_html = ""

    return template(PAGE_TPL,
                    highlight_style=HtmlFormatter().get_style_defs('.highlight'),
                    highlight_left=highlight_left,
                    highlight_right=highlight_right,
                    diff=diff_html,
                    text_left=code_left,
                    text_right=code_right)


def main():
    from optparse import OptionParser
    cmd_parser = OptionParser(usage="usage: %prog package.module:app")
    cmd_options, cmd_args = cmd_parser.parse_args()
    if len(cmd_args) >= 2:
        host, port = (cmd_args[0] or 'localhost'), (cmd_args[1] or 8080)
    elif len(cmd_args) == 1:
        host, port = (cmd_args[0] or 'localhost'), (8080)
    else:
        host, port = ('localhost'), (8080)
    if ':' in host:
        host, port = host.rsplit(':', 1)
    run(host=host, port=port)

if __name__ == '__main__':
    main()
