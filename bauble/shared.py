# shared.py

import logging
from gi.repository import Gtk
#from gi.repository import Pango
from bauble.utils import set_widget_value
#from bauble.utils import safe_set_text
from bauble import prefs

logger = logging.getLogger(__name__)

# class InfoExpander(Gtk.Expander):
#     """
#     Abstract class for an expandable info box.
#     """

#     def __init__(self, label):
#         super().__init__()
#         self.set_label(label)
#         self.vbox = Gtk.VBox()
#         self.add(self.vbox)
#         self.set_expanded(True)


class InfoExpander(Gtk.Expander):
    """
    an abstract class that is really just a generic expander with a vbox
    to extend this you just have to implement the update() method
    """

    # preference for storing the expanded state
    expanded_pref = None

    def __init__(self, label, widgets=None):
        """
        :param label: The name of this info expander, displayed on the expander.
        :param widgets: A bauble.utils.BuilderWidgets instance.
        """
        super().__init__()
        self.set_label(label)
        self.vbox = Gtk.VBox(spacing=10)  # Standardizes spacing
        self.vbox.set_border_width(5)
        self.add(self.vbox)
        self.widgets = widgets or {}  # Ensure widgets is always a dictionary
        if not self.expanded_pref:
            self.set_expanded(True)
        self.connect("notify::expanded", self.on_expanded)

    def on_expanded(self, expander, *args):
        """
        Save the expanded state in preferences, if specified.
        """
        if self.expanded_pref:
            prefs.prefs[self.expanded_pref] = expander.get_expanded()
            prefs.prefs.save()
            
    def set_labeled_value(self, prefix, value):
        """
        Toggle visibility of a labeled field and set its value.
        
        Labels and data widgets are identified using `prefix+'_label'`
        and `prefix+'_data'`.

        :param prefix: The identifier for the label and data widgets.
        :param value: The value to set. If empty, hides the widgets.
        """
        label_widget = self.widgets.get(f"{prefix}_label")
        data_widget = self.widgets.get(f"{prefix}_data")

        if data_widget and label_widget:
            if value:
                self.widget_set_value(f"{prefix}_data", value)
                label_widget.set_visible(True)
                data_widget.set_visible(True)
            else:
                label_widget.set_visible(False)
                data_widget.set_visible(False)
        else:
            logger.warning(f"Widgets for prefix '{prefix}' not found.")

    def widget_set_value(self, widget_name, value, markup=False, default=None):
        """
        a shorthand for L{bauble.utils.set_widget_value()}
        """
        set_widget_value(
            self.widgets[widget_name], value, markup, default
        )

    def update(self, value):
        """
        This method should be implemented by classes that extend InfoExpander
        """
        raise NotImplementedError("InfoExpander.update(): not implemented")


class Action(Gtk.Action):
    """
    Represents an action with a callback and optional visibility toggles.
    """

    def __init__(self, name, label, tooltip=None, stock_id=None, callback=None):
        super().__init__(name=name, label=label, tooltip=tooltip, stock_id=stock_id)
        self.callback = callback

    def execute(self, *args):
        if self.callback:
            self.callback(*args)
