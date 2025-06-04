from gi.repository import GObject, Gedit, Gtk

class GEditLocalLLaMA(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "geditlocalllama"
    window = GObject.Property(type=Gedit.Window)

    def __init__(self):
        super().__init__()

    def do_activate(self):
        # Add a button to the UI
        self.button = Gtk.Button(label="Click Me")
        self.button.connect("clicked", self.on_button_clicked)

        # Add to Gedit bottom panel (Gtk.Stack in Gedit 41+)
        panel = self.window.get_bottom_panel()
        panel.add_titled(self.button, "MyPluginButton", "My Plugin")
        panel.show()

    def do_deactivate(self):
        panel = self.window.get_bottom_panel()
        panel.remove(self.button)

    def do_update_state(self):
        pass

    def on_button_clicked(self, button):
        print("Hello from Gedit Plugin!")
