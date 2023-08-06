# -*- coding: utf-8 -*-
"""
    trydoc
    ------

    :copyright: Copyright 2012 by NaN Projectes de Programari Lliure, S.L.
    :license: BSD, see LICENSE for details.
"""

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.parsers.rst.directives.images import Image
from docutils.transforms import Transform
from sphinx.util.compat import Directive

import os
import re
import sys
import tempfile
import proteus

import tryton
import gtk
import gobject


def get_field_data(model_name, field_name, show_help):
    if not proteus.config._CONFIG.current:
        raise ValueError('Proteus has not been initialized.')

    Model = proteus.Model.get('ir.model')
    models = Model.find([
            ('model', '=', model_name),
            ])
    if not models:
        return None

    ModelField = proteus.Model.get('ir.model.field')
    field = ModelField.find([
            ('name', '=', field_name),
            ('model', '=', models[0].id),
            ])[0]

    text = ''
    for field in models[0].fields:
        if field.name == field_name:
            if show_help:
                if field.help:
                    text = field.help
                else:
                    text = 'Field "%s" has no help available' % field.name
            else:
                if field.field_description:
                    text = field.field_description
                else:
                    text = 'Field "%s" has no description available' % field.name
            break

    return text


class FieldDirective(Directive):
    has_content = True
    required_arguments = 1
    optional_arguments = 1
    final_argument_whitespace = False
    option_spec = {
            'help': directives.flag
            }

    def run(self):
        content = self.arguments[0]
        if 'help' in self.options:
            show_help = True
        else:
            show_help = False

        model_name, field_name = content.split('/')

        text = get_field_data(model_name, field_name, show_help)
        if text is None:
            return [self.state_machine.reporter.warning(
                    'Model "%s" not found.' % model_name, line=self.lineno)]

        return [nodes.Text(text)]

def get_ref_data(module_name, fs_id, field):
    if not proteus.config._CONFIG.current:
        raise ValueError('Proteus has not been initialized.')
    ModelData = proteus.Model.get('ir.model.data')

    records = ModelData.find([
            ('module', '=', module_name),
            ('fs_id', '=', fs_id),
            ])
    if not records:
        return None

    db_id = records[0].db_id
    # model cannot be unicode
    model = str(records[0].model)

    Model = proteus.Model.get(model)
    record = Model(db_id)
    return getattr(record, field)

class TryRefDirective(Directive):
    has_content = True
    required_arguments = 1
    optional_arguments = 1
    final_argument_whitespace = False
    option_spec = {}

    def run(self):
        content = self.arguments[0]

        ref, field = content.split('/')
        module_name, fs_id = ref.split('.')

        text = get_ref_data(module_name, fs_id, field)
        if text is None:
            return [self.state_machine.reporter.warning(
                    'Reference "%s" not found.' % content, line=self.lineno)]

        return [nodes.Text(text)]

files_to_delete = []

class ViewDirective(Image):
    option_spec = Image.option_spec.copy()
    option_spec.update({
            'field': directives.unchanged,
            })
    counter = 0

    def run(self):
        view = str(self.arguments[0])
        field = self.options.get('field')

        self.counter += 1
        # TODO: Create snapshot
        fd, self.filename = tempfile.mkstemp(suffix='.png', dir='.')

        files_to_delete.append(self.filename)
        self.filename = os.path.basename(self.filename)

        #self.filename = 'screenshot-%03d.png' % self.counter
        self.screenshot()

        self.arguments[0] = self.filename
        image_node_list = Image.run(self)
        return image_node_list

    def screenshot(self):
        #disp = Display(visible=True)
        #disp.start()
        #disp.redirect_display(True)
        #print "ENV: ", os.environ
        #print "AA: ", disp.new_display_var
        # TODO:
        # Use: tryton://localhost/test/model/party.party
        main = tryton.gui.Main(self)
        gobject.timeout_add(200, self.drawWindow, main.window)
        gtk.main()
        #gtk.main_iteration()
        #import time
        #time.sleep(1)
        return True

    #main.sig_login()
    #gtk.main()
    #client = tryton.client.TrytonClient()
    #client.run()

    def drawWindow(self, win):
        # Code below from: 
        # http://stackoverflow.com/questions/7518376/creating-a-screenshot-of-a-gtk-window
        # More info here:
        # http://burtonini.com/computing/screenshot-tng.py

        width, height = win.get_size()
        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, width, height)

        # Retrieve the pixel data from the gdk.window attribute (win.window)
        # of the gtk.window object
        screenshot = pixbuf.get_from_drawable(win.window, win.get_colormap(), 
        0, 0, 0, 0, width, height)

        screenshot.save(self.filename, 'png')
        gtk.main_quit()

        # Return False to stop the repeating interval
        return False


class References(Transform):
    """
    Parse and transform tryref and field references in a document.
    """

    default_priority = 999

    def apply(self):
        config = self.document.settings.env.config
        pattern = config.trydoc_pattern
        if isinstance(pattern, basestring):
            pattern = re.compile(pattern)
        for node in self.document.traverse(nodes.Text):
            parent = node.parent
            if isinstance(parent, (nodes.literal, nodes.FixedTextElement)):
                # ignore inline and block literal text
                continue
            text = unicode(node)
            modified = False

            match = pattern.search(text)
            while match:
            #for match in pattern.finditer(text):
                # catch invalid pattern with too many groups
                if len(match.groups()) != 1:
                    raise ValueError(
                        'trydoc_issue_pattern must have '
                        'exactly one group: {0!r}'.format(match.groups()))
                # extract the reference text (including the leading dash)
                reftext = match.group(0)
                # extract the reference data (excluding the leading dash)
                refdata = match.group(1)

                start = match.start(0)
                end = match.end(0)

                data = refdata.split(':')
                kind = data[0]
                content = data[1]
                if len(data) > 2:
                    options = data[2]
                else:
                    options = None

                if kind == 'field':
                    model_name, field_name = content.split('/')
                    if options == 'help':
                        show_help = True
                    else:
                        show_help = False
                    replacement = get_field_data(model_name, field_name, show_help)
                elif kind == 'tryref':
                    ref, field = content.split('/')
                    module_name, fs_id = ref.split('.')
                    replacement = get_ref_data(module_name, fs_id, field)
                else:
                    replacement = refdata

                text = text[:start] + replacement + text[end:]
                modified = True
                
                match = pattern.search(text)
                
            if modified:
                parent.replace(node, [nodes.Text(text)])


def init_transformer(app):
    if app.config.trydoc_plaintext:
        app.add_transform(References)
    if (app.config.trydoc_modules and
            proteus.config._CONFIG.current.database_name == ':memory:'):
        module_model = proteus.Model.get('ir.module.module')
        modules_to_install = []
        for module_to_install in app.config.trydoc_modules:
            res = module_model.find([('name', '=', module_to_install)])
            #if app.config.verbose:
            sys.stderr.write("Module found with name '%s': %s.\n"
                    % (module_to_install, res))
            if res:
                modules_to_install.append(res[0].id)
        if modules_to_install:
            proteus_context = proteus.config._CONFIG.current.context
            #if app.config.verbose:
            sys.stderr.write("It will install the next modules: %s with "
                    "context %s.\n" % (modules_to_install,
                                proteus_context))
            module_model.install(modules_to_install, proteus_context)
        proteus.Wizard('ir.module.module.install_upgrade').execute('upgrade')


def remove_temporary_files(app, exception):
    for x in files_to_delete:
        if os.path.exists(x):
            os.remove(x)

def setup(app):
    app.add_config_value('trydoc_server', None, 'env')
    app.add_config_value('trydoc_plaintext', True, 'env')
    app.add_config_value('trydoc_pattern', re.compile(r'@(.|[^@]+)@'), 'env')
    app.add_config_value('trydoc_modules', [], 'env')
    #app.add_config_value('verbose', False, 'env'), 

    app.add_directive('field', FieldDirective)
    app.add_directive('tryref', TryRefDirective)
    app.add_directive('view', ViewDirective)

    app.connect(b'builder-inited', init_transformer)
    app.connect(b'build-finished', remove_temporary_files)

