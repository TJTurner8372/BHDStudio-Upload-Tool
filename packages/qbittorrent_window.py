import pathlib
from configparser import ConfigParser
from tkinter import (
    Toplevel,
    LabelFrame,
    W,
    N,
    E,
    S,
    Checkbutton,
    StringVar,
    DISABLED,
    ttk,
    Frame,
    Entry,
    filedialog,
    Label,
    SUNKEN,
    messagebox,
)
from packages.hoverbutton import HoverButton
from custom_hovertip import CustomTooltipLabel


class QBittorrentWindow:
    """gui window to set up qBittorrent injection"""

    def __init__(
        self,
        master,
        options_menu,
        custom_window_bg_color,
        font,
        font_size,
        custom_label_frame_color_dict,
        custom_frame_color_dict,
        custom_button_color_dict,
        custom_entry_colors_dict,
        custom_label_colors_dict,
    ):
        # define config parser used within the class
        self.qbit_config = ConfigParser()
        self.configfile = "runtime/config.ini"
        self.qbit_config.read(self.configfile)

        # define instance variables
        self.master = master
        self.options_menu = options_menu
        self.custom_window_bg_color = custom_window_bg_color
        self.font = font
        self.font_size = font_size
        self.custom_label_frame_color_dict = custom_label_frame_color_dict
        self.custom_frame_color_dict = custom_frame_color_dict
        self.custom_button_color_dict = custom_button_color_dict
        self.custom_entry_colors_dict = custom_entry_colors_dict
        self.custom_label_colors_dict = custom_label_colors_dict

        # disable menu option
        self.options_menu.entryconfig("qBittorrent Injection", state="disabled")

        # remove binding for control+q to prevent multiple windows from potentially being opened
        self.master.unbind("<Control-q>")

        # define window and it's attributes
        self.qbit_window = Toplevel(self.master)
        self.qbit_window.configure(
            background=self.custom_window_bg_color
        )  # window background color
        self.qbit_window.title("qBittorrent Injection")  # set window title
        self.qbit_window.geometry(
            f'{600}x{340}+{str(int(self.master.geometry().split("+")[1]) + 60)}+'
            f'{str(int(self.master.geometry().split("+")[2]) + 120)}'
        )
        self.qbit_window.protocol(
            "WM_DELETE_WINDOW", self.win_exit
        )  # define what 'X' does
        self.qbit_window.grab_set()  # force attention to window until closed
        self.qbit_window.lift(self.master)  # lift this window above all tkinter windows
        self.qbit_window.grid_columnconfigure(0, weight=1)
        self.qbit_window.grid_columnconfigure(1, weight=1)
        self.qbit_window.grid_columnconfigure(2, weight=1)
        self.qbit_window.grid_rowconfigure(0, weight=1)
        self.qbit_window.grid_rowconfigure(1, weight=1000)
        self.qbit_window.grid_rowconfigure(2, weight=1)

        # adjust root transparency
        self.master.wm_attributes("-alpha", 0.92)

        # create injection enabled/disabled variable
        self.injection_enable = StringVar()
        self.injection_enable.set(
            self.qbit_config["qbit_client"]["qbit_injection_toggle"]
        )

        # define injection option for paused torrent
        self.injection_toggle = Checkbutton(
            self.qbit_window,
            text="Enable Injection",
            variable=self.injection_enable,
            onvalue="true",
            offvalue="false",
            command=self.injection_toggle_func,
        )
        self.injection_toggle.grid(
            row=0, column=0, columnspan=3, padx=5, pady=(5, 3), sticky=E + W
        )
        self.injection_toggle.configure(
            background=self.custom_window_bg_color,
            foreground=self.custom_button_color_dict["foreground"],
            activebackground=self.custom_window_bg_color,
            activeforeground=self.custom_button_color_dict["foreground"],
            selectcolor=custom_window_bg_color,
            font=(self.font, self.font_size + 2),
        )

        # create a tool tip for injection toggle widget
        CustomTooltipLabel(
            anchor_widget=self.injection_toggle,
            hover_delay=400,
            background=custom_window_bg_color,
            foreground=self.custom_label_frame_color_dict["foreground"],
            font=(self.font, 9, "bold"),
            text="Enables automatic qBittorrent torrent client\ninjection when "
            "uploading your torrent to BeyondHD",
        )

        # define options label frame
        self.injection_type = LabelFrame(
            self.qbit_window,
            text=" Injection Options ",
            labelanchor="nw",
            bd=3,
            font=(self.font, 10, "bold"),
            fg=self.custom_label_frame_color_dict["foreground"],
            bg=self.custom_label_frame_color_dict["background"],
        )
        self.injection_type.grid(
            column=0, row=1, columnspan=3, padx=5, pady=(5, 3), sticky=W + E + N + S
        )

        self.injection_type.grid_rowconfigure(0, weight=300)
        self.injection_type.grid_rowconfigure(1, weight=1)
        self.injection_type.grid_columnconfigure(0, weight=1)
        self.injection_type.grid_columnconfigure(1, weight=1)

        # define injection type variable
        self.injection_type_var = StringVar()
        self.injection_type_var.set(
            self.qbit_config["qbit_client"]["qbit_injection_type"]
        )

        # define tabbed window
        self.injection_tabs = ttk.Notebook(self.injection_type, cursor="hand2")
        self.injection_tabs.grid(
            row=0, column=0, columnspan=4, sticky=E + W + N + S, padx=2, pady=(2, 2)
        )
        self.injection_tabs.grid_columnconfigure(0, weight=1)
        self.injection_tabs.grid_rowconfigure(1, weight=1)

        # change injection type based on selected tab
        self.injection_tabs.bind("<<NotebookTabChanged>>", self.tab_changed)

        # webui tab
        self.webui_tab = Frame(
            self.injection_tabs, bg=self.custom_frame_color_dict["specialbg"]
        )
        self.injection_tabs.add(self.webui_tab, text=" WebUI ")
        self.webui_tab.grid_rowconfigure(0, weight=1)
        self.webui_tab.grid_columnconfigure(0, weight=100)
        self.webui_tab.grid_columnconfigure(3, weight=1)

        # cli tab
        self.cli_tab = Frame(
            self.injection_tabs, bg=self.custom_frame_color_dict["specialbg"]
        )
        self.injection_tabs.add(self.cli_tab, text=" CLI ")
        self.cli_tab.grid_rowconfigure(0, weight=1)
        self.cli_tab.grid_rowconfigure(1, weight=1)
        self.cli_tab.grid_columnconfigure(0, weight=1)
        self.cli_tab.grid_columnconfigure(1, weight=1)

        # qBittorrent path label frame
        self.qbittorrent_frame = Frame(
            self.cli_tab,
            bd=0,
            bg=self.custom_frame_color_dict["specialbg"],
        )
        self.qbittorrent_frame.grid(
            column=0, row=0, columnspan=4, padx=5, pady=(0, 3), sticky=E + W + N + S
        )
        self.qbittorrent_frame.grid_rowconfigure(0, weight=1)
        self.qbittorrent_frame.grid_columnconfigure(0, weight=1)
        self.qbittorrent_frame.grid_columnconfigure(1, weight=1000)

        # set qbittorrent cli button
        self.set_path = HoverButton(
            self.qbittorrent_frame,
            text="Set",
            command=self.set_qbittorrent_path,
            borderwidth="3",
            width=12,
            foreground=self.custom_button_color_dict["foreground"],
            background=self.custom_button_color_dict["background"],
            activeforeground=self.custom_button_color_dict["activeforeground"],
            activebackground=self.custom_button_color_dict["activebackground"],
            disabledforeground=self.custom_button_color_dict["disabledforeground"],
        )
        self.set_path.grid(row=0, column=0, padx=5, pady=(5, 3), sticky=W + E)

        # qBittorrent program path variable
        self.qbittorrent_client_path = StringVar()

        # qBittorrent cli entry path
        self.qbit_path_entry = Entry(
            self.qbittorrent_frame,
            borderwidth=4,
            textvariable=self.qbittorrent_client_path,
            fg=self.custom_entry_colors_dict["foreground"],
            bg=self.custom_entry_colors_dict["background"],
            disabledforeground=self.custom_entry_colors_dict["disabledforeground"],
            disabledbackground=self.custom_entry_colors_dict["disabledbackground"],
            state=DISABLED,
        )
        self.qbit_path_entry.grid(
            row=0, column=1, columnspan=3, padx=5, pady=(5, 2), sticky=W + E
        )

        # update entry box with saved path var if it exists
        if pathlib.Path(self.qbit_config["qbit_client"]["qbit_path"]).is_file():
            self.qbittorrent_client_path.set(
                str(pathlib.Path(self.qbit_config["qbit_client"]["qbit_path"]))
            )

        # define variable option for paused torrent
        self.cli_paused_var = StringVar()

        # set variable from the config
        self.cli_paused_var.set(self.qbit_config["qbit_client"]["qbit_cli_paused"])

        # define injection option for paused torrent
        self.cli_paused = Checkbutton(
            self.cli_tab,
            text="Torrent Paused",
            variable=self.cli_paused_var,
            onvalue="true",
            offvalue="false",
        )
        self.cli_paused.grid(row=1, column=0, padx=5, pady=(5, 3), sticky=E + W)
        self.cli_paused.configure(
            background=self.custom_frame_color_dict["specialbg"],
            foreground=self.custom_button_color_dict["foreground"],
            activebackground=self.custom_frame_color_dict["specialbg"],
            activeforeground=self.custom_button_color_dict["foreground"],
            selectcolor=custom_window_bg_color,
            font=(self.font, self.font_size + 1),
        )

        # define injection option variable
        self.cli_skipped_var = StringVar()

        # set skipped torrent variable from config
        self.cli_skipped_var.set(self.qbit_config["qbit_client"]["qbit_cli_skip_check"])

        # define injection option for skipped torrent
        self.cli_skip_check = Checkbutton(
            self.cli_tab,
            text="Skip Check",
            variable=self.cli_skipped_var,
            onvalue="true",
            offvalue="false",
        )
        self.cli_skip_check.grid(row=1, column=1, padx=5, pady=(5, 3), sticky=E + W)
        self.cli_skip_check.configure(
            background=self.custom_frame_color_dict["specialbg"],
            foreground=self.custom_button_color_dict["foreground"],
            activebackground=self.custom_frame_color_dict["specialbg"],
            activeforeground=self.custom_button_color_dict["foreground"],
            selectcolor=custom_window_bg_color,
            font=(self.font, self.font_size + 1),
        )
        ##

        # set tab
        if "webui" in self.injection_type_var.get():
            self.injection_tabs.select(0)
        elif "cli" in self.injection_type_var.get():
            self.injection_tabs.select(1)

        # cancel button
        self.cancel_button = HoverButton(
            self.qbit_window,
            text="Cancel",
            command=self.win_exit,
            borderwidth="3",
            width=12,
            foreground=self.custom_button_color_dict["foreground"],
            background=self.custom_button_color_dict["background"],
            activeforeground=self.custom_button_color_dict["activeforeground"],
            activebackground=self.custom_button_color_dict["activebackground"],
            disabledforeground=self.custom_button_color_dict["disabledforeground"],
        )
        self.cancel_button.grid(row=2, column=0, padx=5, pady=(5, 3), sticky=W + S + N)

        # status label
        self.qbit_status_label = Label(
            self.qbit_window,
            text=f"Injection Mode: {self.injection_type_var.get().upper()}",
            bd=0,
            relief=SUNKEN,
            background=self.custom_label_colors_dict["background"],
            fg=self.custom_label_colors_dict["foreground"],
            font=(self.font, self.font_size - 1),
        )
        self.qbit_status_label.grid(
            row=2, column=1, padx=5, pady=(5, 3), sticky=S + N + W + E
        )

        # apply button
        self.apply_button = HoverButton(
            self.qbit_window,
            text="Apply",
            command=self.apply_button_function,
            borderwidth="3",
            width=12,
            foreground=self.custom_button_color_dict["foreground"],
            background=self.custom_button_color_dict["background"],
            activeforeground=self.custom_button_color_dict["activeforeground"],
            activebackground=self.custom_button_color_dict["activebackground"],
            disabledforeground=self.custom_button_color_dict["disabledforeground"],
        )
        self.apply_button.grid(row=2, column=2, padx=5, pady=(5, 3), sticky=E + S + N)

    # def update_cli_paused_var(self):
    #     """update cli paused variable to config"""
    #     update_cli_parser = ConfigParser()
    #     update_cli_parser.read(self.configfile)
    #     update_cli_parser.set("qbit_client", "qbit_cli_paused", self.cli_paused_var.get())
    #     with open(self.configfile, "w") as cli_cfg:
    #         update_cli_parser.write(cli_cfg)
    #
    # def update_cli_skipped_var(self):
    #     """update cli skipped variable to config"""
    #     update_skip_parser = ConfigParser()
    #     update_skip_parser.read(self.configfile)
    #     update_skip_parser.set("qbit_client", "qbit_cli_skip_check", self.cli_skipped_var.get())
    #     with open(self.configfile, "w") as cli_cfg1:
    #         update_skip_parser.write(cli_cfg1)

    def injection_toggle_func(self):
        """update config file with injection enabled/disable"""
        injection_enable_disable_parser = ConfigParser()
        injection_enable_disable_parser.read(self.configfile)
        injection_enable_disable_parser.set(
            "qbit_client", "qbit_injection_toggle", self.injection_enable.get()
        )
        with open(self.configfile, "w") as enable_disable:
            injection_enable_disable_parser.write(enable_disable)

    def set_qbittorrent_path(self):
        """set path to qbittorrent"""
        qbit_path_parser = ConfigParser()
        qbit_path_parser.read(self.configfile)

        # check config file for existing path
        if (
            qbit_path_parser["qbit_client"]["qbit_path"] != ""
            and pathlib.Path(qbit_path_parser["qbit_client"]["qbit_path"]).is_file()
        ):
            qbit_path_directory = pathlib.Path(
                qbit_path_parser["qbit_client"]["qbit_path"]
            ).parent
            qbit_exe = pathlib.Path(qbit_path_parser["qbit_client"]["qbit_path"]).name
        else:
            qbit_path_directory = "/"
            qbit_exe = ""

        # dialog to define the path
        qbit_app_path = filedialog.askopenfilename(
            parent=self.qbit_window,
            title="Set Path to qBittorrent",
            initialdir=qbit_path_directory,
            initialfile=qbit_exe,
            filetypes=[("qBittorrent", "qbittorrent.exe")],
        )

        if qbit_app_path:
            # update entry variable
            self.qbittorrent_client_path.set(str(pathlib.Path(qbit_app_path)))

            # write new path to config
            qbit_path_parser.set(
                "qbit_client", "qbit_path", str(pathlib.Path(qbit_app_path))
            )
            with open(self.configfile, "w") as qbit_path_cfg:
                qbit_path_parser.write(qbit_path_cfg)

    def tab_changed(self, _):
        """
        Re-assign injection type var each time the tab is changed
        If selected tab is webui update variable to webui, if selected tab is cli update variable to cli

        Update status label with injection type
        """
        if (
            str(self.injection_tabs.tab(self.injection_tabs.select(), "text"))
            .lower()
            .strip()
            == "webui"
        ):
            self.injection_type_var.set("webui")
        elif (
            str(self.injection_tabs.tab(self.injection_tabs.select(), "text"))
            .lower()
            .strip()
            == "cli"
        ):
            self.injection_type_var.set("cli")

        self.qbit_status_label.config(
            text=f"Injection Mode: {self.injection_type_var.get().upper()}"
        )

    def apply_button_function(self):
        """run when apply button is selected"""

        # define parser for apply
        apply_btn_parser = ConfigParser()
        apply_btn_parser.read(self.configfile)

        # run different functions based off of selected injection type
        if self.injection_type_var.get() == "webui":
            pass
        elif self.injection_type_var.get() == "cli":
            apply_btn_parser.set(
                "qbit_client", "qbit_cli_skip_check", self.cli_skipped_var.get()
            )
            apply_btn_parser.set(
                "qbit_client", "qbit_cli_paused", self.cli_paused_var.get()
            )

        # update config information to file
        with open(self.configfile, "w") as apply_cfg:
            apply_btn_parser.write(apply_cfg)

        # check if all parameters are correctly setup
        if self.injection_enable.get() == "true":
            if self.injection_type_var.get().lower() == "cli":
                if not pathlib.Path(self.qbittorrent_client_path.get()).is_file():
                    messagebox.showerror(
                        parent=self.qbit_window,
                        title="Error",
                        message="qBittorrent.exe path must be defined or "
                        "injection mode must be set to disabled",
                    )
                    return  # exit

        # run exit function
        self.win_exit()

    def win_exit(self):
        """run when exiting qbittorrent injection option window"""

        # re-enable qbittorrent injection menu option
        self.options_menu.entryconfig("qBittorrent Injection", state="normal")

        # re-enable control+q binding (needs finished when module is completed)
        self.master.bind(
            "<Control-q>",
            lambda event: QBittorrentWindow(
                master=self.master,
                options_menu=self.options_menu,
                custom_window_bg_color=self.custom_window_bg_color,
                font=self.font,
                font_size=self.font_size,
                custom_label_frame_color_dict=self.custom_label_frame_color_dict,
                custom_frame_color_dict=self.custom_frame_color_dict,
                custom_button_color_dict=self.custom_button_color_dict,
                custom_entry_colors_dict=self.custom_entry_colors_dict,
                custom_label_colors_dict=self.custom_label_colors_dict,
            ),
        )

        # restore transparency
        self.master.wm_attributes("-alpha", 1.0)

        # close window
        self.qbit_window.destroy()
