from gi.repository import GObject, Gedit, Gtk, Gio, GLib, Gdk
import requests
import json
from threading import Thread

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
        view = tab.get_view()
        if view and view not in self._handler_ids:
            handler_id = view.connect("populate-popup", self.on_populate_popup)
            self._handler_ids[view] = handler_id

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

    def _get_ollama_models(self):
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            response.raise_for_status()
            models = response.json().get("models", [])
            return [m["name"] for m in models]
        except Exception as e:
            print(f"[Ollama] Failed to fetch models: {e}")
            return []

    def _get_default_model(self):
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            response.raise_for_status()
            models = response.json().get("models", [])
            models.sort(key=lambda m: m.get("size", float("inf")))
            return models[0]["name"] if models else None
        except Exception as e:
            print(f"[Ollama] Error getting default model: {e}")
            return "deepseek-r1:1.5b"

    def on_populate_popup(self, view, menu):
        models = self._get_ollama_models()
        menu.append(Gtk.SeparatorMenuItem())

        if not models:
            warning_item = Gtk.MenuItem(label="🛑 No Ollama models available")
            warning_item.set_sensitive(False)
            menu.append(warning_item)
            menu.show_all()
            return

        default_model = self._get_default_model()

        # Quick actions
        quick_generate = Gtk.MenuItem(label=f"🔮 Generate ({default_model})")
        quick_generate.connect("activate", self._generate_with_model, view, default_model)

        quick_summarize = Gtk.MenuItem(label=f"📝 Summarize ({default_model})")
        quick_summarize.connect("activate", self._summarize_with_model, view, default_model)

        menu.append(quick_generate)
        menu.append(quick_summarize)

        # Submenus for all models
        gen_menu = Gtk.Menu()
        gen_root = Gtk.MenuItem(label="🔮 Generate with...")
        gen_root.set_submenu(gen_menu)

        sum_menu = Gtk.Menu()
        sum_root = Gtk.MenuItem(label="📝 Summarize with...")
        sum_root.set_submenu(sum_menu)

        for model in models:
            gen_item = Gtk.MenuItem(label=model)
            gen_item.connect("activate", self._generate_with_model, view, model)
            gen_menu.append(gen_item)

            sum_item = Gtk.MenuItem(label=model)
            sum_item.connect("activate", self._summarize_with_model, view, model)
            sum_menu.append(sum_item)

        menu.append(gen_root)
        menu.append(sum_root)
        menu.show_all()

    def _generate_with_model(self, widget, view, model):
        self._stream_with_model(view, model, "Write more based on the following:", "Generated Output ({})".format(model))

    def _summarize_with_model(self, widget, view, model):
        self._stream_with_model(view, model, "Summarize the following:", "Summarized Output ({})".format(model))

    def _stream_with_model(self, view, model, prompt_prefix, title):
        buffer = view.get_buffer()
        if not buffer.get_has_selection():
            return
        start, end = buffer.get_selection_bounds()
        selected_text = buffer.get_text(start, end, True)

        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model,
                    "prompt": f"{prompt_prefix}\n\n{selected_text}",
                    "stream": True
                },
                timeout=60,
                stream=True
            )
            response.raise_for_status()
            self._stream_to_modal(view, title, response)
        except Exception as e:
            self._show_modal(view, title, f"[Error contacting Ollama: {e}]")

    def _stream_to_modal(self, view, title, stream):
        dialog = Gtk.Dialog(title=title, transient_for=view.get_toplevel(), modal=True)
        dialog.set_default_size(400, 300)

        content_area = dialog.get_content_area()
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_hexpand(True)
        scrolled.set_vexpand(True)

        textview = Gtk.TextView()
        textview.set_editable(False)
        textview.set_wrap_mode(Gtk.WrapMode.WORD)
        buffer = textview.get_buffer()

        scrolled.add(textview)
        content_area.pack_start(scrolled, True, True, 0)

        dialog.add_button("Copy", Gtk.ResponseType.APPLY)
        dialog.add_button("Close", Gtk.ResponseType.CLOSE)

        def append_text(text):
            end_iter = buffer.get_end_iter()
            buffer.insert(end_iter, text)

            mark = buffer.create_mark(None, buffer.get_end_iter(), True)
            textview.scroll_mark_onscreen(mark)
            return False

        def read_stream():
            try:
                for line in stream.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        if "response" in chunk:
                            GLib.idle_add(append_text, chunk["response"])
            except Exception as e:
                GLib.idle_add(append_text, f"\n[Streaming error: {e}]")

        Thread(target=read_stream, daemon=True).start()

        def on_response(dialog, response_id):
            if response_id == Gtk.ResponseType.APPLY:
                start, end = buffer.get_bounds()
                clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
                clipboard.set_text(buffer.get_text(start, end, True), -1)
            dialog.destroy()

        dialog.connect("response", on_response)
        dialog.show_all()

    def _show_modal(self, view, title, text):
        dialog = Gtk.Dialog(title=title, transient_for=view.get_toplevel(), modal=True)
        dialog.set_default_size(400, 300)

        content_area = dialog.get_content_area()
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_hexpand(True)
        scrolled.set_vexpand(True)

        textview = Gtk.TextView()
        textview.set_editable(False)
        textview.set_wrap_mode(Gtk.WrapMode.WORD)
        textview.get_buffer().set_text(text)

        scrolled.add(textview)
        content_area.pack_start(scrolled, True, True, 0)

        dialog.add_button("Copy", Gtk.ResponseType.APPLY)
        dialog.add_button("Close", Gtk.ResponseType.CLOSE)

        def on_response(dialog, response_id):
            if response_id == Gtk.ResponseType.APPLY:
                buffer = textview.get_buffer()
                start, end = buffer.get_bounds()
                clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
                clipboard.set_text(buffer.get_text(start, end, True), -1)
            dialog.destroy()

        dialog.connect("response", on_response)
        dialog.show_all()