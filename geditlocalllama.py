from gi.repository import GObject, Gedit, Gtk, Gio

class GEditLocalLLaMA(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "geditlocalllama"
    window = GObject.Property(type=Gedit.Window)

    def __init__(self):
        super().__init__()
        self._handler_ids = {}
        self._tab_added_id = None

    def do_activate(self):
        for doc in self.window.get_documents():
            self._connect_doc(doc)

        self._tab_added_id = self.window.connect("tab-added", self.on_tab_added)

    def do_deactivate(self):
        if self._tab_added_id:
            self.window.disconnect(self._tab_added_id)
            self._tab_added_id = None

        for view, handler_id in self._handler_ids.items():
            view.disconnect(handler_id)

        self._handler_ids.clear()

    def do_update_state(self):
        pass

    def on_tab_added(self, window, tab):
        doc = tab.get_document()
        self._connect_doc(doc)

    def _connect_doc(self, doc):
        file = doc.get_file()
        if not isinstance(file, Gio.File):
            return

        tab = self.window.get_tab_from_location(file)
        if tab is None:
            return

        view = tab.get_view()
        if view and view not in self._handler_ids:
            handler_id = view.connect("populate-popup", self.on_populate_popup)
            self._handler_ids[view] = handler_id

    def on_populate_popup(self, view, menu):
        generate_item = Gtk.MenuItem(label="🔮 Generate")
        summarize_item = Gtk.MenuItem(label="📝 Summarize")

        generate_item.connect("activate", self.on_generate_clicked, view)
        summarize_item.connect("activate", self.on_summarize_clicked, view)

        menu.append(Gtk.SeparatorMenuItem())
        menu.append(generate_item)
        menu.append(summarize_item)
        menu.show_all()

    def on_generate_clicked(self, widget, view):
        buffer = view.get_buffer()
        if buffer.get_has_selection():
            start, end = buffer.get_selection_bounds()
            selected_text = buffer.get_text(start, end, True)
            print(f"🔮 Generate clicked with: {selected_text}")
            buffer.delete(start, end)
            buffer.insert(start, "[Generated text goes here]")

    def on_summarize_clicked(self, widget, view):
        buffer = view.get_buffer()
        if buffer.get_has_selection():
            start, end = buffer.get_selection_bounds()
            selected_text = buffer.get_text(start, end, True)
            print(f"📝 Summarize clicked with: {selected_text}")
            buffer.delete(start, end)
            buffer.insert(start, "[Summarized content here]")
