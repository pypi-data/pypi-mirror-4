# -*- coding: utf-8 -*-
"""
    sphinxcontrib.recentpages
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Build recent update pages list.

    :copyright: Copyright 2012 by Sho Shimauchi.
    :license: BSD, see LICENSE for details.
"""

from sphinx.util.compat import Directive
from docutils import nodes

import os
import datetime
import re


def visit_html_recentpages(self, node):
    env = self.builder.env
    file_list = get_file_list_ordered_by_mtime(env)

    num = node['num']
    n = len(file_list) if num < 0 else num

    self.body += _generate_html(file_list, n)
    raise nodes.SkipNode


def depart_recentpages(self, node):
    pass


def setup(app):
    app.add_node(recentpages,
                 html=(visit_html_recentpages, depart_recentpages))

    app.add_config_value('recentpages_sidebar', True, 'html')
    app.add_config_value('recentpages_sidebar_pages', 5, 'html')

    app.add_directive('recentpages', RecentpagesDirective)

    app.connect('env-updated', generate_template)
    app.connect('html-page-context', generate_recentpages_html)


class recentpages(nodes.General, nodes.Element):
    """Node for recentpages extention.
    """
    pass


class RecentpagesDirective(Directive):
    """
    Directive to display recent update pages list.
    """

    has_content = True
    option_spec = {
        'num': int
    }

    def run(self):
        env = self.state.document.settings.env
        env.note_reread()

        num = self.options.get('num', -1)
        res = recentpages('')
        res['num'] = num
        return [res]


explicit_title_re = re.compile(r'^<(.*?)>(.+?)\s*(?<!\x00)<(.*?)>$', re.DOTALL)


def get_file_list_ordered_by_mtime(env):
    res = []

    for docname in env.found_docs:
        abspath = env.doc2path(docname)
        mtime = os.path.getmtime(abspath)
        title = env.titles[docname]
        m = explicit_title_re.match(unicode(title))
        if m:
            title = m.group(2)
        else:
            title = None
        res.append((docname, mtime, title))

    res = list(set(res))
    res.sort(cmp=lambda x, y: cmp(x[1], y[1]), reverse=True)

    return res


def generate_template(app, env):
    if not app.builder.config.recentpages_sidebar:
        return

    templates_path = app.builder.config.templates_path

    if len(templates_path) == 0:
        app.builder.warn("no templates directory")
        return

    srcdir = app.builder.srcdir
    template_dir = os.path.join(app.builder.srcdir, templates_path[0])

    if not os.path.exists(template_dir):
        app.builder.warn("%s does not exist" % (template_dir,))
        return

    target_path = os.path.join(template_dir, 'recentpages.html')

    if os.path.exists(target_path):
        return

    if not os.access(template_dir, os.W_OK):
        app.builder.warn("%s is not writable" % (template_dir,))
        return

    contents = """{#
    recentpages.html
    ~~~~~~~~~~~~~~~~

    Sphinx sidebar template: recentpages

    :copyright: Copyright 2012 by Sho Shimauchi.
    :license: BSD, see LICENSE for details.
#}
{%- if recentpages_sidebar %}
<h3>Recentpages</h3>
{{ recentpages_content }}
{%- endif %}
"""

    op = open(target_path, 'w')
    try:
        op.write(contents)
    finally:
        op.close()


def generate_recentpages_html(app, pagename, templatename, context, doctree):
    if not app.builder.config.recentpages_sidebar:
        return

    context['recentpages_sidebar'] = True
    NUM_OF_PAGES = app.builder.config.recentpages_sidebar_pages

    env = app.builder.env
    file_list = get_file_list_ordered_by_mtime(env)
    html_content = _generate_html_sidebar(file_list, NUM_OF_PAGES)

    context['recentpages_content'] = ''.join(html_content)


def _generate_html(file_list, num):
    html_content = []
    for docname, mtime, title in file_list:
        html_content.append('%s - ' % datetime.datetime.fromtimestamp(mtime))
        html_content.append('<a href="%s.html">' % docname)
        html_content.append('%s</a><br />' % title)
        num -= 1
        if num <= 0:
            break

    return html_content


def _generate_html_sidebar(file_list, num):
    html_content = []

    current_mday = ""

    for docname, mtime, title in file_list:
        mday = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
        if current_mday != mday:
            current_mday = mday
            html_content.append('<b>%s</b><br />' % current_mday)
        html_content.append('<div style="margin-left:16px">')
        html_content.append('<a href="%s.html">' % docname)
        html_content.append('%s</a><br />' % title)
        html_content.append('</div>')
        num -= 1
        if num <= 0:
            break

    return html_content
