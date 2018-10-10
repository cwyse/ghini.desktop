# -*- coding: utf-8 -*-
#
# Copyright 2008-2010 Brett Adams
# Copyright 2012-2018 Mario Frasca <mario@anche.no>.
# Copyright 2017 Jardín Botánico de Quito
# Copyright 2017 Ross Demuth
#
# This file is part of ghini.desktop.
#
# ghini.desktop is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ghini.desktop is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ghini.desktop. If not, see <http://www.gnu.org/licenses/>.

#
# __init__.py
#
# Description : report plugin
#
import os
import traceback

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject

from threading import Thread

from sqlalchemy import union

import bauble

from bauble.error import BaubleError
import bauble.utils as butils
import bauble.paths as bpaths
from bauble.prefs import prefs
import bauble.pluginmgr as pluginmgr
from bauble.plugins.plants import Family, Genus, Species, VernacularName
from bauble.plugins.garden import Accession, Plant, Location, Source, Contact
from bauble.plugins.tag import Tag

from bauble.editor import (
    GenericEditorView, GenericEditorPresenter)

from .flat_export import FlatFileExportTool
from .utils import PS, SVG

# name: formatter_kwargs
config_list_pref = 'report.options'

# the default report generator to select on start
default_config_pref = 'report.xsl'
formatter_settings_expanded_pref = 'report.settings.expanded'


def get_plant_query(obj, session):
    """
    """
    # .order_by(None) is needed for the later union() to work properly
    q = session.query(Plant)
    if isinstance(obj, Family):
        return q.join('accession', 'species', 'genus', 'family').filter_by(id=obj.id)
    elif isinstance(obj, Genus):
        return q.join('accession', 'species', 'genus').filter_by(id=obj.id)
    elif isinstance(obj, Species):
        return q.join('accession', 'species').filter_by(id=obj.id)
    elif isinstance(obj, VernacularName):
        return q.join('accession', 'species', 'vernacular_names').filter_by(id=obj.id)
    elif isinstance(obj, Plant):
        return q.filter_by(id=obj.id)
    elif isinstance(obj, Accession):
        return q.join('accession').filter_by(id=obj.id)
    elif isinstance(obj, Location):
        return q.filter_by(location_id=obj.id)
    elif isinstance(obj, Contact):
        return q.join('accession', 'source', 'source_detail').filter_by(id=obj.id)
    elif isinstance(obj, Tag):
        plants = get_pertinent_objects(Plant, obj.objects)
        return q.filter(Plant.id.in_([p.id for p in plants]))
    else:
        raise BaubleError(_("Can't get plants from a %s") % type(obj).__name__)


def get_accession_query(obj, session):
    """
    """
    q = session.query(Accession)
    if isinstance(obj, Family):
        return q.join('species', 'genus', 'family').filter_by(id=obj.id)
    elif isinstance(obj, Genus):
        return q.join('species', 'genus').filter_by(id=obj.id)
    elif isinstance(obj, Species):
        return q.join('species').filter_by(id=obj.id)
    elif isinstance(obj, VernacularName):
        return q.join('species', 'vernacular_names').filter_by(id=obj.id)
    elif isinstance(obj, Plant):
        return q.join('plants').filter_by(id=obj.id)
    elif isinstance(obj, Accession):
        return q.filter_by(id=obj.id)
    elif isinstance(obj, Location):
        return q.join('plants').filter_by(location_id=obj.id)
    elif isinstance(obj, Contact):
        return q.join('source', 'source_detail').filter_by(id=obj.id)
    elif isinstance(obj, Tag):
        acc = get_pertinent_objects(Accession, obj.objects)
        return q.filter(Accession.id.in_([a.id for a in acc]))
    else:
        raise BaubleError(_("Can't get accessions from a %s") %
                          type(obj).__name__)


def get_species_query(obj, session):
    """
    """
    q = session.query(Species)
    if isinstance(obj, Family):
        return q.join('genus', 'family').filter_by(id=obj.id)
    elif isinstance(obj, Genus):
        return q.join('genus').filter_by(id=obj.id)
    elif isinstance(obj, Species):
        return q.filter_by(id=obj.id)
    elif isinstance(obj, VernacularName):
        return q.join('vernacular_names').filter_by(id=obj.id)
    elif isinstance(obj, Plant):
        return q.join('accessions', 'plants').filter_by(id=obj.id)
    elif isinstance(obj, Accession):
        return q.join('accessions').filter_by(id=obj.id)
    elif isinstance(obj, Location):
        return q.join('accessions', 'plants', 'location').filter_by(id=obj.id)
    elif isinstance(obj, Contact):
        return q.join('accessions', 'source', 'source_detail').filter_by(id=obj.id)
    elif isinstance(obj, Tag):
        acc = get_pertinent_objects(Species, obj.objects)
        return q.filter(Species.id.in_([a.id for a in acc]))
    else:
        raise BaubleError(_("Can't get species from a %s") %
                          type(obj).__name__)


def get_location_query(obj, session):
    """
    """
    q = session.query(Location)
    if isinstance(obj, Location):
        return q.filter_by(id=obj.id)
    elif isinstance(obj, Plant):
        return q.join('plants').filter_by(id=obj.id)
    elif isinstance(obj, Accession):
        return q.join('plants', 'accession').filter_by(id=obj.id)
    elif isinstance(obj, Family):
        return q.join('plants', 'accession', 'species', 'genus', 'family').\
            filter_by(id=obj.id)
    elif isinstance(obj, Genus):
        return q.join('plants', 'accession', 'species', 'genus').\
            filter_by(id=obj.id)
    elif isinstance(obj, Species):
        return q.join('plants', 'accession', 'species').\
            filter_by(id=obj.id)
    elif isinstance(obj, VernacularName):
        return q.join('plants', 'accession', 'species', 'vernacular_names').\
            filter_by(id=obj.id)
    elif isinstance(obj, Contact):
        return q.join('plants', 'accession', 'source', 'source_detail').\
            filter_by(id=obj.id)
    elif isinstance(obj, Tag):
        locs = get_pertinent_objects(Location, obj.objects)
        return q.filter(Location.id.in_([l.id for l in locs]))
    else:
        raise BaubleError(_("Can't get Location from a %s") %
                          type(obj).__name__)


def get_pertinent_objects(cls, objs):
    """return a query containing all `csl` objects reachable from `objs`

    :param cls:
    :param objs:
    """
    if not isinstance(objs, (list, tuple)):
        objs = [objs]
    from sqlalchemy.orm import object_session
    session = object_session(objs[0])

    get_query_func = {
        Plant: get_plant_query,
        Accession: get_accession_query,
        Species: get_species_query,
        Location: get_location_query,
    }[cls]

    queries = [get_query_func(o, session) for o in objs]
    unions = union(*[q.statement for q in queries])
    return session.query(cls).from_statement(unions)


class SettingsBox(Gtk.VBox):
    """
    the interface to use for the settings box, formatters should
    implement this interface and return it from the formatters's get_settings
    method
    """
    def __init__(self):
        super().__init__()

    def get_settings(self):
        raise NotImplementedError

    def update(self, settings):
        raise NotImplementedError


class FormatterPlugin(pluginmgr.Plugin):
    '''
    an interface class that a plugin should implement if it wants to generate
    reports with the ReportToolPlugin

    NOTE: the title class attribute must be a unique string
    '''

    title = ''

    @classmethod
    def init(cls):
        '''inform report presenter that this plugin is available

        (extend in derived classes)
        '''
        cls.install()  # plugins still not versioned...
        ReportToolDialogPresenter.formatter_class_map[cls.title] = cls

    @staticmethod
    def format(objs, **kwargs):
        '''
        called when the use clicks on OK, this is the worker
        '''
        raise NotImplementedError

    @classmethod
    def get_template(cls, name):
        '''return Template object corresponding to name within Plugin

        In principle, a Template object is what is going to perform the
        rendering, unless the Plugin overrides the behaviour.

        The contract with a minimum Template object is that its .filename
        field points to the original file name.

        '''
        result = type('Template', (object, ), {'filename': ''})()
        for path in [os.path.join(bpaths.user_dir(), 'templates', name),
                     os.path.join(bpaths.lib_dir(), 'plugins', 'report', 'templates', name)]:
            if os.path.exists(path):
                result.filename = path
                break
        return result

    @classmethod
    def can_handle(cls, name):
        '''tell whether plugin can handle template
        '''
        try:
            if name.endswith(cls.extension):
                return cls.get_iteration_domain(name) != ''
            else:
                return False
        except Exception as e:
            logger.debug("%s can't handle template %s - %s(%s)" % (cls.title, name, type(e).__name__, e))
            return False

    @classmethod
    def get_options(cls, name):
        '''return template options list

        an element in the options list is a 4-tuple of strings, describing a
        field: (name, type, default, tooltip)

        '''
        try:
            template = cls.get_template(name)
            filename = template.filename
            with open(filename) as f:
                option_lines = [m for m in [cls.option_pattern.match(i.strip())
                                            for i in f.readlines()]
                                if m is not None]
        except:
            option_lines = []

        return [i.groups() for i in option_lines]

    @classmethod
    def get_iteration_domain(cls, name):
        '''return template iteration domain

        a template that does not declare its iteration domain is not
        considered valid.

        '''
        try:
            template = cls.get_template(name)
            filename = template.filename
            with open(filename) as f:
                domains = [m.group(1) for m in [cls.domain_pattern.match(line.strip())
                                                for line in f.readlines()]
                           if m is not None]
                try:
                    domain = domains[0]
                except IndexError as e:
                    logger.debug("template %s(%s) contains no %s DOMAIN declaration" % (template, filename, cls.title, ))
                    domain = ''
        except Exception as e:
            logger.debug("template %s can't be read - %s(%s)" % (name, type(e).__name__, e))
            domain = ''

        return domain


class TemplateFormatterPlugin(FormatterPlugin):
    """intermediate base for template-based textual formatters.

    this is an abstract base class, used by Mako and Jinja2 formatter
    plugins.  you must override the `get_template` method, and define the
    four fields `title`, `extension`, `domain_pattern` and `option_pattern`.

    """

    @classmethod
    def install(cls, import_defaults=True):
        "create templates dir on plugin installation"
        logger.debug("installing %s plugin" % cls.title)
        container_dir = os.path.join(bpaths.appdata_dir(), 'templates')
        if not os.path.exists(container_dir):
            os.mkdir(container_dir)

    @classmethod
    def get_template(cls, filename):
        raise NotImplementedError

    @classmethod
    def format(cls, objs, **kwargs):
        template_name = kwargs['template']
        use_private = kwargs.get('private', True)
        template = cls.get_template(template_name)

        from bauble import db
        session = db.Session()
        values = list(map(session.merge, objs))
        report = template.render(values=values, options=kwargs)
        session.close()
        # Template name is guaranteed in the form
        # ›<name>.<dotless-extension><cls.extension>‹.  Get the dotless
        # extension from the template file name, produce output with that
        # extension.
        head, ext = os.path.splitext(template_name[:-len(cls.extension)])
        import tempfile
        fd, filename = tempfile.mkstemp(suffix=ext)
        if isinstance(report, str):
            report = report.encode('utf8')
        os.write(fd, report)
        os.close(fd)
        try:
            butils.desktop.open("file://%s" % filename)
        except OSError:
            butils.message_dialog(_('Could not open the report with the '
                                    'default program. You can open the '
                                    'file manually at %s') % filename)
        return report


class ReportToolDialogPresenter(GenericEditorPresenter):
    '''presenter, and at same time model.

    Let user set parameters for report production, return them to invoking
    function, and die.

    '''

    # to be populated by template plugins
    formatter_class_map = {}  # title->class

    def __init__(self, view):
        super().__init__(model=self, view=view, refresh_view=False)
        self.start_thread(Thread(target=self.populate_names_combo))

        self.view.widget_set_sensitive('ok_button', False)

        # set the names combo to the default. this activates
        # on_names_combo_changes, which does the rest of the work
        combo = self.view.widgets.names_combo
        default = prefs[default_config_pref]
        self.view.widget_set_value('names_combo', default)
        # hard_coded_options are part of the glade interface, we do not
        # remove them when selecting a different template.
        self.hard_coded_options = set(self.view.widgets.options_box.get_children())

    def set_prefs_for(self, name, settings):
        '''
        This will overwrite any other report settings with name
        '''
        template_options = prefs[config_list_pref] or {}
        template_options[name] = settings
        prefs[config_list_pref] = template_options

    def on_new_button_clicked(self, *args):
        d = Gtk.Dialog(_("Activate Formatter Template"), self.view.get_window(),
                       Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                       buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                                Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
        d.vbox.set_spacing(10)
        d.set_default_response(Gtk.ResponseType.ACCEPT)

        # label
        text = '<b>%s</b>' % _('Enter a Name and choose a Formatter Template')
        label = Gtk.Label()
        label.set_markup(text)
        label.set_xalign(0)
        d.vbox.pack_start(label, True, True, 0)

        # file_chooser_widget
        chooser = Gtk.FileChooserWidget(0)
        d.vbox.pack_start(chooser, True, True, 0)

        # action
        d.show_all()
        names = set([i[0] for i in self.view.widgets.names_ls])
        while True:
            if d.run() != Gtk.ResponseType.ACCEPT:
                break
            template = chooser.get_filename()
            name = os.path.basename(template)
            if template is None:
                # ignore action on emtpy choice
                continue
            elif name in names:
                butils.message_dialog(_('name ›%s‹ is already in use') % name)
                continue
            else:
                for plugin in self.formatter_class_map.values():
                    if plugin.can_handle(template):
                        break
                else:
                    butils.message_dialog(_('Not a template, or no valid formatter installed.'))
                    continue

            self.set_prefs_for(name, {})
            # copy template to user data as name
            src = template
            dst = os.path.join(bpaths.user_dir(), 'templates', name)
            import shutil
            shutil.copy(src, dst)
            # reflect changes in view
            self.add_name_to_combo_and_select_it(name, plugin)
            break
        d.destroy()
        
    def on_remove_button_clicked(self, *args):
        '''remove user-template, or mark package-template as hidden

        we have no "hidden" template flag yet.
        '''
        butils.message_dialog('this is not implemented yet.')
        pass

    def on_names_combo_changed(self, combo, *args):
        self.options = {}
        name = self.view.widget_get_value('names_combo')
        self.view.widget_set_sensitive('details_box', (name or '') != '')
        prefs[default_config_pref] = name  # set the default to the new name
        GObject.idle_add(self._names_combo_changed_idle, combo)

    def _names_combo_changed_idle(self, combo):
        name = self.view.widget_get_value('names_combo')
        settings = prefs[config_list_pref].get(name, {})

        self.view.widget_set_sensitive('ok_button', False)
        self.view.widget_set_value('basename_entry', '')
        self.view.widget_set_value('formatter_entry', '')
        self.view.widget_set_value('domain_entry', '')

        try:
            row = self.view.widgets.names_combo.get_active()
            title = self.view.widgets.names_ls[row][1]
            plugin = self.formatter_class_map[title]
            domain = plugin.get_iteration_domain(name)
            if domain == '':
                raise IndexError(name)
            if domain == 'raw':
                model = bauble.gui.get_results_model()
                top_left_content = model[0][0]
                domain = '(%s)' % top_left_content.__class__.__name__.lower()
            self.view.widget_set_value('basename_entry', name)
            self.view.widget_set_value('formatter_entry', title)
            self.view.widget_set_value('domain_entry', domain)
            self.view.widget_set_sensitive('ok_button', True)
        except Exception as e:
            butils.message_dialog('Template %s raised %s(%s).' % (name, type(e).__name__, e))
            return

        self.set_prefs_for(name, settings)

        self.defaults = []
        options_box = self.view.widgets.options_box
        # empty the options box
        for child in options_box.get_children():
            if child in self.hard_coded_options:
                continue
            options_box.remove(child)
        # which options does the template accept? (can be None)
        option_fields = plugin.get_options(name)
        current_row = 1  # should not be hard coded
        # populate the options box
        for fname, ftype, fdefault, ftooltip in option_fields:
            row = Gtk.HBox()
            label = Gtk.Label(fname.replace('_', ' ') + _(':'))
            label.set_alignment(0, 0.5)
            ftype = ftype.lower()
            if ftype == 'bool':
                fdefault = fdefault.lower() not in ['false', '0']
                self.options.setdefault(fname, fdefault)
                entry = Gtk.CheckButton()
                entry.set_margin_left(4)
                entry.set_active(self.options[fname])
                entry.connect('toggled', self.set_bool_option, fname)
            else:
                self.options.setdefault(fname, fdefault)
                entry = Gtk.Entry()
                entry.set_text(self.options[fname])
                entry.connect('changed', self.set_option, fname)
            entry.set_tooltip_text(ftooltip)
            # entry updates the corresponding item in report.options
            self.defaults.append((entry, fdefault))
            options_box.attach(label, 0, current_row, 1, 1)
            options_box.attach(entry, 1, current_row, 2, 1)
            current_row += 1
        if self.defaults:
            button = Gtk.Button(_('Reset to defaults'))
            button.connect('clicked', self.reset_options)
            options_box.attach(button, 3, current_row - 1, 2, 1)
        options_box.show_all()

    def reset_options(self, widget):
        for entry, value in self.defaults:
            if isinstance(value, bool):
                entry.set_active(value)
            else:
                entry.set_text(value)

    def set_option(self, widget, fname):
        self.options[fname] = widget.get_text()

    def set_bool_option(self, widget, fname):
            self.options[fname] = widget.get_active()

    def add_name_to_combo_and_select_it(self, name, plugin):
        '''the names tells it all

        scan through the names_ls, first column:1, holding the plugin.title,
        then column:0 holding the template name, and they are both in
        alphabetical order.

        '''

        names_ls = self.view.widgets.names_ls
        for n, row in enumerate(names_ls):
            if row[1] < plugin.title:
                continue
            if row[0] < name:
                continue
            break
        names_ls.insert(n, (name[:-len(plugin.extension)], plugin.title,))
        GObject.idle_add(self.view.widget_set_value, 'names_combo', name)

    def populate_names_combo(self):
        '''populate names_ls from package- and user-templates

        please note: prefs[config_list_pref] are just user defined settings.
        if a template can be found, it is considered active and should be
        shown in the combo.

        '''
        paths = [os.path.join(bpaths.user_dir(), 'templates'),
                 os.path.join(bpaths.lib_dir(), 'plugins', 'report', 'templates'), ]
        self.view.widgets.names_ls.clear()
        for title in sorted(self.formatter_class_map):  # sort templates by plugin
            plugin = self.formatter_class_map[title]
            logger.debug("scanning %s templates for %s" % (title, plugin))
            for path in paths:
                logger.debug("scanning path %s" % (path, ))
                for candidate in sorted(os.listdir(path)):  # then by name
                    if plugin.can_handle(candidate):
                        logger.debug('%s accepts %s' % (title, candidate, ))
                        self.view.widgets.names_ls.append((candidate, title, ))
                    else:
                        logger.debug('%s refuses %s' % (title, candidate, ))

    def save_formatter_settings(self):
        template_options = prefs[config_list_pref]
        name = self.view.widget_get_value('names_combo')
        template_options[name] = self.options
        prefs[config_list_pref] = template_options

    def selection_to_domain(self, domain):
        '''convert the selection to the corresponding domain

        if domain is one of species, accession, plant, location, then
        retrieve all objects in the domain that are associated to the
        selected objects.

        if domain looks like `(domain)`, then it is an implicit domain,
        i.e.: it was inferred from the selection itself, so the selection
        itself is what we need.

        if the domain is `raw`, also that tells us to return the raw
        selection (the template will handle it).

        '''
        try:
            cls = {
                'plant': Plant,
                'accession': Accession,
                'species': Species,
                'location': Location,
            }[domain]
            return sorted(get_pertinent_objects(cls, self.selection),
                          key=butils.natsort_key)
        except KeyError:
            return self.selection

    def start(self):
        '''collect user choices, invokes formatter, repeat.

        '''
        results_model = bauble.gui.get_results_model()  # guaranteed not empty
        self.selection = [row[0] for row in results_model]  # only top level selected
        from sqlalchemy.orm import object_session
        self.session = object_session(self.selection[0])  # reuse the same session

        formatter = None
        settings = None
        while True:
            response = self.view.start()
            if response != Gtk.ResponseType.OK:
                break

            name = self.view.widget_get_value('names_combo')
            prefs[default_config_pref] = name
            self.save_formatter_settings()
            settings = prefs[config_list_pref].get(name, {})
            settings['template'] = name
            domain = self.view.widget_get_value('domain_entry')
            title = self.view.widget_get_value('formatter_entry')
            formatter = self.formatter_class_map[title]
            todo = self.selection_to_domain(domain)
            if todo:
                self.work_thread = Thread(target=self.run_thread, args=[formatter, todo, settings])
                self.running = True
                GObject.timeout_add(200, self.update_progress)
                self.view.widgets.main_grid.set_sensitive(False)
                self.view.widget_set_sensitive('ok_button', False)
                self.view.widget_set_sensitive('cancel_button', False)
                self.work_thread.start()
            else:
                translated_name = {
                    'plant': _('plants/clones'),
                    'accession': _('accessions'),
                    'species': _('species'),
                    'location': _('locations'),
                }[domain]
                butils.message_dialog(_('There are no %s in the search results.\n'
                                       'Please try another search.') % translated_name)

        self.view.disconnect_all()

    def update_progress(self):
        if self.running:
            self.view.widgets.progressbar.pulse()
        return self.running

    def run_thread(self, formatter, todo, settings):
        from bauble import db
        session = db.Session()
        todo = [session.merge(i) for i in todo]
        try:
            formatter.format(todo, **settings)
        except Exception as e:
            butils.idle_message("formatting %s objects of type %s\n%s(%s)\n%s" % (len(todo), type((todo+[None])[0]).__name__, type(e).__name__, e, traceback.format_exc()), type=Gtk.MessageType.ERROR)
                             
        session.close()
        GObject.idle_add(self.stop_progress)

    def stop_progress(self):
        self.running = False
        self.work_thread.join()
        self.view.widgets.main_grid.set_sensitive(True)
        self.view.widget_set_sensitive('ok_button', True)
        self.view.widget_set_sensitive('cancel_button', True)
        self.view.widgets.progressbar.set_fraction(0)
        

class ReportTool(pluginmgr.Tool):
    category = (_('Report'), "plugins/report/tool-report.png")
    label = _("From Template")
    icon_name = "text-x-generic-template"

    @classmethod
    def start(self):
        '''
        '''
        # is anything selected?  if not, refuse even considering
        if not bauble.gui.get_results_model():
            return

        bauble.gui.set_busy(True)
        ok = False
        try:
            filename = os.path.join(bpaths.lib_dir(), "plugins", "report", 'report.glade')
            view = GenericEditorView(filename, root_widget_name='report_dialog')
            presenter = ReportToolDialogPresenter(view)
            presenter.start()
        except AssertionError as e:
            logger.debug(e)
            logger.debug(traceback.format_exc())
            parent = None
            if hasattr(self, 'view') and hasattr(self.view, 'dialog'):
                parent = self.view.get_window()

            butils.message_details_dialog("AssertionError(%s)" % e, traceback.format_exc(),
                                         Gtk.MessageType.ERROR, parent=parent)
        except Exception as e:
            logger.debug(traceback.format_exc())
            butils.message_details_dialog(_('Formatting Error\n\n'
                                           '%s(%s)') % (type(e).__name__, butils.utf8(e)),
                                         traceback.format_exc(),
                                         Gtk.MessageType.ERROR)
        bauble.gui.set_busy(False)
        return


class ReportToolPlugin(pluginmgr.Plugin):
    '''
    '''
    tools = [ReportTool, FlatFileExportTool, ]


try:
    import lxml.etree as etree
    import lxml._elementpath  # put this here so py2exe picks it up
except ImportError:
    butils.message_dialog('The <i>lxml</i> package is required for the '
                         'Report plugin')
else:
    def plugin():
        from bauble.plugins.report.xsl import XSLFormatterPlugin
        from bauble.plugins.report.mako import MakoFormatterPlugin
        from bauble.plugins.report.jinja2 import Jinja2FormatterPlugin
        return [ReportToolPlugin, XSLFormatterPlugin,
                MakoFormatterPlugin, Jinja2FormatterPlugin]
