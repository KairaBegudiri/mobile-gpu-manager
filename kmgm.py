#!/usr/bin/env python3
import gi, os, subprocess, shlex
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango, GLib

DESKTOP_PATHS = [
    "/usr/share/applications",
    os.path.expanduser("~/.local/share/applications")
]

def parse_desktop_files():
    apps = []
    for path in DESKTOP_PATHS:
        if not os.path.isdir(path):
            continue
        for file in os.listdir(path):
            if file.endswith(".desktop"):
                try:
                    full_path = os.path.join(path, file)
                    name, exec_cmd = None, None
                    with open(full_path, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.startswith("Name=") and not name:
                                name = line.strip().split("=", 1)[1]
                            if line.startswith("Exec=") and not exec_cmd:
                                exec_cmd = line.strip().split("=", 1)[1].split(" ")[0]
                    if name and exec_cmd:
                        apps.append((name, exec_cmd))
                except:
                    continue
    return sorted(apps, key=lambda x: x[0].lower())

class KMGM(Gtk.Window):
    def __init__(self):
        super().__init__(title="Kayra's Mobile GPU Manager")
        self.set_default_size(900, 600)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.add(hbox)

        internal_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.internal_search = Gtk.SearchEntry()
        self.internal_search.set_placeholder_text("Ara...")
        self.internal_search.connect("search-changed", self.filter_internal)
        self.internal_list = Gtk.ListBox()
        scroll1 = Gtk.ScrolledWindow()
        scroll1.add(self.internal_list)
        internal_vbox.pack_start(self.internal_search, False, False, 5)
        internal_vbox.pack_start(scroll1, True, True, 5)
        frame1 = Gtk.Frame(label="Dahili GPU")
        frame1.add(internal_vbox)
        hbox.pack_start(frame1, True, True, 5)

        external_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.external_search = Gtk.SearchEntry()
        self.external_search.set_placeholder_text("Ara...")
        self.external_search.connect("search-changed", self.filter_external)
        self.external_list = Gtk.ListBox()
        scroll2 = Gtk.ScrolledWindow()
        scroll2.add(self.external_list)
        external_vbox.pack_start(self.external_search, False, False, 5)
        external_vbox.pack_start(scroll2, True, True, 5)
        frame2 = Gtk.Frame(label="Harici GPU")
        frame2.add(external_vbox)
        hbox.pack_start(frame2, True, True, 5)

        right_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        frame3 = Gtk.Frame(label="Yönetim")
        frame3.set_size_request(300, -1)
        frame3.add(right_vbox)
        hbox.pack_start(frame3, False, False, 5)

        self.param_entry = Gtk.Entry()
        self.param_entry.set_placeholder_text("Çalıştırma parametreleri")
        right_vbox.pack_start(self.param_entry, False, False, 5)

        self.gpu_check = Gtk.CheckButton(label="Harici GPU kullanılsın mı?")
        self.gpu_check.connect("toggled", self.on_gpu_toggle)
        right_vbox.pack_start(self.gpu_check, False, False, 5)

        self.start_btn = Gtk.Button(label="Uygulamayı Başlat")
        self.start_btn.connect("clicked", self.on_start_app)
        right_vbox.pack_start(self.start_btn, False, False, 5)

        self.save_btn = Gtk.Button(label="Ayarları Kaydet")
        self.save_btn.connect("clicked", self.on_save)
        right_vbox.pack_start(self.save_btn, False, False, 5)

        self.desktop_check = Gtk.CheckButton(label="Masaüstüne eklensin mi?")
        right_vbox.pack_start(self.desktop_check, False, False, 5)

        self.launcher_check = Gtk.CheckButton(label="Başlatıcıya eklensin mi?")
        right_vbox.pack_start(self.launcher_check, False, False, 5)

        self.selected_app = None
        self.apps = parse_desktop_files()
        self.internal_rows = []
        self.external_rows = []

        self.populate_lists()

    def populate_lists(self):
        self.internal_list.foreach(lambda w: self.internal_list.remove(w))
        self.external_list.foreach(lambda w: self.external_list.remove(w))
        self.internal_rows.clear()
        self.external_rows.clear()

        for name, cmd in self.apps:
            row = Gtk.ListBoxRow()
            label = Gtk.Label(name, xalign=0)
            row.add(label)
            row.app_name = name
            row.cmd = cmd
            self.internal_list.add(row)
            self.internal_rows.append(row)

        self.internal_list.show_all()
        self.external_list.show_all()

        self.internal_list.connect("row-selected", self.on_row_selected)
        self.external_list.connect("row-selected", self.on_row_selected)

    def on_row_selected(self, listbox, row):
        if row:
            self.selected_app = row
            self.param_entry.set_text("")
            self.gpu_check.set_active(False)

    def on_gpu_toggle(self, button):
        if not self.selected_app:
            return
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Uygulamayı yeniden başlatmak ister misiniz?"
        )
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.YES:
            self.start_app(restart=True)

    def on_save(self, button):
        if not self.selected_app:
            return
        name = self.selected_app.app_name + " + KMGM"
        if self.desktop_check.get_active():
            desktop_path = os.path.expanduser(f"~/Desktop/{name}.desktop")
            with open(desktop_path, "w") as f:
                f.write(f"[Desktop Entry]\nName={name}\nExec={self.selected_app.cmd}\nType=Application\n")
            os.chmod(desktop_path, 0o755)
        if self.launcher_check.get_active():
            launcher_path = os.path.expanduser(f"~/.local/share/applications/{name}.desktop")
            with open(launcher_path, "w") as f:
                f.write(f"[Desktop Entry]\nName={name}\nExec={self.selected_app.cmd}\nType=Application\n")
            os.chmod(launcher_path, 0o755)
        print("Ayarlar kaydedildi.")

    def on_start_app(self, button=None, restart=False):
        if not self.selected_app:
            return
        cmd = self.selected_app.cmd
        if self.gpu_check.get_active():
            cmd = f"prime-run {cmd}"
            row = self.selected_app
            self.internal_list.remove(row)
            self.external_list.add(row)
            self.external_list.show_all()
        if self.param_entry.get_text():
            cmd = f"{cmd} {self.param_entry.get_text()}"
        subprocess.Popen(cmd, shell=True)
        print(f"Uygulama başlatıldı: {cmd}")

    def filter_internal(self, search_entry):
        text = search_entry.get_text().lower()
        for row in self.internal_rows:
            row.set_visible(text in row.app_name.lower())

    def filter_external(self, search_entry):
        text = search_entry.get_text().lower()
        for row in self.external_rows:
            row.set_visible(text in row.app_name.lower())

if __name__ == "__main__":
    win = KMGM()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
