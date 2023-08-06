#
# Copyright (c) 2013, Prometheus Research, LLC
#


from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.util.osutil import copyfile
import re, os.path


class DemoDirective(Directive):

    has_content = True
    option_spec = {
            'layout': directives.unchanged,
    }

    layout_re = re.compile(r'^(?:[+-]?demo([,]\s*[+-]?source)?|'
                           r'[+-]?source([,]\s*[+-]?demo)?)$')

    def run(self):
        doc = self.state.document
        env = doc.settings.env
        if 'layout' in self.options:
            layout = self.options['layout']
        else:
            layout = env.config.demo_layout
        if not self.layout_re.match(layout):
            return [doc.reporter.error("invalid layout specifier: %s" % layout,
                                       lineno=self.lineno)]
        order = []
        for block in layout.split(','):
            block = block.strip()
            is_hidden = block[0] == '-'
            block = block.lstrip('+-')
            order.append((block, is_hidden))
        wrapper = nodes.compound(classes=['demo-wrapper'])
        data = "\n".join(self.content)
        for block, is_hidden in order:
            if block == 'demo':
                header = nodes.paragraph(classes=['demo-header'])
                header += nodes.Text("Demo")
                if is_hidden:
                    header['classes'].append('demo-hide')
                demo = nodes.raw(data, data,
                                 format='html',
                                 classes=['demo-area'])
                wrapper += header
                wrapper += demo
            elif block == 'source':
                header = nodes.paragraph(classes=['demo-header'])
                header += nodes.Text("Source")
                if is_hidden:
                    header['classes'].append('demo-hide')
                source = nodes.literal_block(data, data,
                                             language='html',
                                             classes=['demo-source'])
                wrapper += header
                wrapper += source
            else:
                assert False, block
        return [wrapper]


def copy_static(app, exception):
    if app.builder.name != 'html' or exception:
        return
    for filename in ['jsdemo.js', 'jsdemo.css']:
        src = os.path.join(os.path.abspath(os.path.dirname(__file__)), filename)
        dst = os.path.join(app.builder.outdir, '_static', filename)
        copyfile(src, dst)


def setup(app):
    app.add_config_value('demo_layout', '+demo, +source', 'env')
    app.add_directive('demo', DemoDirective)
    app.connect(str('build-finished'), copy_static)
    app.add_javascript('jsdemo.js')
    app.add_stylesheet('jsdemo.css')


