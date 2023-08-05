import gettext

import pango
import gtk

from kiwi.ui.widgets.entry import ProxyEntry
from kiwi.ui.widgets.label import ProxyLabel

_ = lambda m: gettext.dgettext('kiwi', m)


class EditableLabel(gtk.HBox):
    def __init__(self, value=None):
        gtk.HBox.__init__(self)

        self.entry = ProxyEntry()
        self.entry.connect('activate', self._on_entry__activate)
        self.pack_start(self.entry, True, True, padding=0)

        self.label = ProxyLabel()
        self.pack_start(self.label, True, True, padding=0)
        self.label.modify_font(pango.FontDescription('Sans 16'))
        self.label.set_alignment(0.0, 0.5)
        self.label.set_ellipsize(pango.ELLIPSIZE_END)
        self.label.set_selectable(True)

        self.edit_button = gtk.Button(_('edit'))
        self.edit_button.connect('clicked',
                                self._on_edit_button__clicked)
        self.pack_end(self.edit_button, False, False, padding=6)

        self.update(value)
        if not value:
            self.entry.show()
        else:
            self.label.show()
            self.edit_button.show()

    def update(self, text):
        self.label.update(text)
        self.entry.update(text)

    def _on_entry__activate(self, entry):
        self._toggle_edit_entry()

    def _on_edit_button__clicked(self, button):
        self._toggle_edit_entry()

    def _toggle_edit_entry(self):
        if self.label.get_visible():
            add_widget = self.entry
            remove_widget = self.label
            markup = _('done')
        else:
            add_widget = self.label
            remove_widget = self.entry
            markup = _('edit')
        add_widget.update(remove_widget.read())
        self.edit_button.set_label(markup)
        remove_widget.hide()
        add_widget.show()

        if self.entry.get_visible():
            self.entry.grab_focus()
