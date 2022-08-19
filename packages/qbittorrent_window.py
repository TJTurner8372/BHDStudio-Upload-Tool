import re
from configparser import ConfigParser
from tkinter import (
    Toplevel,
    W,
    N,
    E,
    S,
    Checkbutton,
    StringVar,
    Frame,
    Entry,
    Label,
    SUNKEN,
    messagebox,
)

from custom_hovertip import CustomTooltipLabel

from packages.hoverbutton import HoverButton


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

        # host name var
        self.host_name_var = StringVar()
        self.host_name_var.set(self.qbit_config["qbit_client"]["qbit_url"])

        # host port var
        self.host_port_var = StringVar()
        self.host_port_var.set(self.qbit_config["qbit_client"]["qbit_port"])

        # username var
        self.user_name_var = StringVar()
        self.user_name_var.set(self.qbit_config["qbit_client"]["qbit_user"])

        # password var
        self.pass_word_var = StringVar()
        self.pass_word_var.set(self.qbit_config["qbit_client"]["qbit_password"])

        # category var
        self.category_var = StringVar()
        self.category_var.set(self.qbit_config["qbit_client"]["qbit_category"])

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
            f'{600}x{360}+{str(int(self.master.geometry().split("+")[1]) + 60)}+'
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
            background=self.custom_window_bg_color,
            foreground=self.custom_button_color_dict["foreground"],
            activebackground=self.custom_window_bg_color,
            activeforeground=self.custom_button_color_dict["foreground"],
            selectcolor=custom_window_bg_color,
            font=(self.font, self.font_size + 2, "bold"),
        )
        self.injection_toggle.grid(
            row=0, column=0, columnspan=3, padx=5, pady=(5, 3), sticky=E + W
        )

        # create a tool tip for injection toggle widget
        CustomTooltipLabel(
            anchor_widget=self.injection_toggle,
            hover_delay=400,
            background=custom_window_bg_color,
            foreground=self.custom_label_frame_color_dict["foreground"],
            font=(self.font, self.font_size, "bold"),
            text="Enables automatic qBittorrent torrent client\ninjection when "
            "uploading your torrent to BeyondHD",
        )

        # define frame
        self.injection_frame = Frame(
            self.qbit_window,
            bd=0,
            bg=self.custom_label_frame_color_dict["background"],
        )
        self.injection_frame.grid(
            row=1, column=0, columnspan=3, padx=5, pady=(5, 3), sticky=W + E + N + S
        )

        for i_f in range(10):
            self.injection_frame.grid_rowconfigure(i_f, weight=1)
        for i_f_1 in range(3):
            self.injection_frame.grid_columnconfigure(i_f_1, weight=1)

        # host label
        self.host_label = Label(
            self.injection_frame,
            text="Host:",
            bd=0,
            relief=SUNKEN,
            background=self.custom_label_colors_dict["background"],
            fg=self.custom_button_color_dict["activeforeground"],
            font=(self.font, self.font_size, "bold"),
        )
        self.host_label.grid(row=0, column=0, padx=5, pady=(5, 0), sticky=S + W)

        # host entry
        self.host_name = Entry(
            self.injection_frame,
            borderwidth=4,
            textvariable=self.host_name_var,
            fg=self.custom_entry_colors_dict["foreground"],
            bg=self.custom_entry_colors_dict["background"],
            disabledforeground=self.custom_entry_colors_dict["disabledforeground"],
            disabledbackground=self.custom_entry_colors_dict["disabledbackground"],
        )
        self.host_name.grid(
            row=1, column=0, columnspan=3, padx=5, pady=(2, 2), sticky=W + E + N
        )

        # host tooltip label
        CustomTooltipLabel(
            anchor_widget=self.host_name,
            hover_delay=400,
            background=custom_window_bg_color,
            foreground=self.custom_label_frame_color_dict["foreground"],
            font=(self.font, self.font_size, "bold"),
            text="If qBittorrent is ran locally:\n'localhost' or '127.0.0.1'\n\nDefine host-name IP "
            "address:\ne.g. '8.8.8.8'",
        )

        # host port
        self.host_port = Label(
            self.injection_frame,
            text="Port:",
            bd=0,
            relief=SUNKEN,
            background=self.custom_label_colors_dict["background"],
            fg=self.custom_button_color_dict["activeforeground"],
            font=(self.font, self.font_size, "bold"),
        )
        self.host_port.grid(row=2, column=0, padx=5, pady=(5, 0), sticky=S + W)

        # host port entry
        self.host_port_name = Entry(
            self.injection_frame,
            borderwidth=4,
            textvariable=self.host_port_var,
            fg=self.custom_entry_colors_dict["foreground"],
            bg=self.custom_entry_colors_dict["background"],
            disabledforeground=self.custom_entry_colors_dict["disabledforeground"],
            disabledbackground=self.custom_entry_colors_dict["disabledbackground"],
        )
        self.host_port_name.grid(
            row=3, column=0, columnspan=3, padx=5, pady=(2, 2), sticky=W + E + N
        )

        # host tooltip label
        CustomTooltipLabel(
            anchor_widget=self.host_port_name,
            hover_delay=400,
            background=custom_window_bg_color,
            foreground=self.custom_label_frame_color_dict["foreground"],
            font=(self.font, self.font_size, "bold"),
            text="e.g. '8080' (8080 is default)",
        )

        # username label
        self.user_name = Label(
            self.injection_frame,
            text="User:",
            bd=0,
            relief=SUNKEN,
            background=self.custom_label_colors_dict["background"],
            fg=self.custom_button_color_dict["activeforeground"],
            font=(self.font, self.font_size, "bold"),
        )
        self.user_name.grid(row=4, column=0, padx=5, pady=(5, 0), sticky=S + W)

        # username entry
        self.host_port_name = Entry(
            self.injection_frame,
            borderwidth=4,
            textvariable=self.user_name_var,
            fg=self.custom_entry_colors_dict["foreground"],
            bg=self.custom_entry_colors_dict["background"],
            disabledforeground=self.custom_entry_colors_dict["disabledforeground"],
            disabledbackground=self.custom_entry_colors_dict["disabledbackground"],
        )
        self.host_port_name.grid(
            row=5, column=0, columnspan=3, padx=5, pady=(2, 2), sticky=W + E + N
        )

        # password label
        self.password_label = Label(
            self.injection_frame,
            text="Password:",
            bd=0,
            relief=SUNKEN,
            background=self.custom_label_colors_dict["background"],
            fg=self.custom_button_color_dict["activeforeground"],
            font=(self.font, self.font_size, "bold"),
        )
        self.password_label.grid(row=6, column=0, padx=5, pady=(5, 0), sticky=S + W)

        # password entry
        self.pass_word_entry = Entry(
            self.injection_frame,
            borderwidth=4,
            textvariable=self.pass_word_var,
            show="*",
            fg=self.custom_entry_colors_dict["foreground"],
            bg=self.custom_entry_colors_dict["background"],
            disabledforeground=self.custom_entry_colors_dict["disabledforeground"],
            disabledbackground=self.custom_entry_colors_dict["disabledbackground"],
        )
        self.pass_word_entry.grid(
            row=7, column=0, columnspan=3, padx=5, pady=(2, 2), sticky=W + E + N
        )

        # show password when mouse hovers over password entry box
        self.pass_word_entry.bind(
            "<Enter>", lambda event: self.pass_word_entry.config(show="")
        )
        self.pass_word_entry.bind(
            "<Leave>", lambda event: self.pass_word_entry.config(show="*")
        )

        # category label
        self.category_label = Label(
            self.injection_frame,
            text="Category:",
            bd=0,
            relief=SUNKEN,
            background=self.custom_label_colors_dict["background"],
            fg=self.custom_button_color_dict["activeforeground"],
            font=(self.font, self.font_size, "bold"),
        )
        self.category_label.grid(row=8, column=0, padx=5, pady=(5, 0), sticky=S + W)

        # category entry
        self.category_entry = Entry(
            self.injection_frame,
            borderwidth=4,
            textvariable=self.category_var,
            fg=self.custom_entry_colors_dict["foreground"],
            bg=self.custom_entry_colors_dict["background"],
            disabledforeground=self.custom_entry_colors_dict["disabledforeground"],
            disabledbackground=self.custom_entry_colors_dict["disabledbackground"],
        )
        self.category_entry.grid(
            row=9, column=0, columnspan=3, padx=5, pady=(2, 2), sticky=W + E + N
        )

        # host tooltip label
        CustomTooltipLabel(
            anchor_widget=self.category_entry,
            hover_delay=400,
            background=custom_window_bg_color,
            foreground=self.custom_label_frame_color_dict["foreground"],
            font=(self.font, self.font_size, "bold"),
            text="If injecting remotely, you must first setup a category\nin qBittorrent and define the category "
            "here\n\nOtherwise leave this blank\n\nNOTE: Case Sensitive",
        )

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

    def injection_toggle_func(self):
        """update config file with injection enabled/disable"""
        injection_enable_disable_parser = ConfigParser()
        injection_enable_disable_parser.read(self.configfile)
        injection_enable_disable_parser.set(
            "qbit_client", "qbit_injection_toggle", self.injection_enable.get()
        )
        with open(self.configfile, "w") as enable_disable:
            injection_enable_disable_parser.write(enable_disable)

    def apply_button_function(self):
        """run when apply button is selected"""

        # check for host name
        if self.host_name_var.get().strip() == "":
            self.host_name_var.set("localhost")

        # check for port
        if self.host_port_var.get().strip() == "":
            self.host_port_var.set("8080")
        else:
            check_for_only_digits = re.search(r"\D", self.host_port_var.get())
            if check_for_only_digits:
                self.show_error(
                    "Port entry box should only be numerical digits... e.g. 8080"
                )
                return

        # check for username
        if self.user_name_var.get().strip() == "":
            self.show_error(
                "You must setup a user name in qBittorrent's WebUI settings and enter it here"
            )
            return

        # check for password
        if self.pass_word_var.get().strip() == "":
            self.show_error(
                "You must setup a password in the qBittorrent's WebUI settings and enter it here"
            )
            return

        # check for category
        if (
            self.host_name_var.get().strip() != "localhost"
            or self.host_name_var.get().strip() != "127.0.0.1"
        ):
            if self.category_var.get().strip() == "":
                self.show_error(
                    "When injecting remotely you MUST set-up a category within qBittorrent and define "
                    "that category in the Category entry box"
                )
                return

        # define parser for apply
        apply_btn_parser = ConfigParser()
        apply_btn_parser.read(self.configfile)

        # define all settings for config file
        apply_btn_parser.set(
            "qbit_client", "qbit_url", self.host_name_var.get().strip()
        )
        apply_btn_parser.set(
            "qbit_client", "qbit_port", self.host_port_var.get().strip()
        )
        apply_btn_parser.set(
            "qbit_client", "qbit_user", self.user_name_var.get().strip()
        )
        apply_btn_parser.set(
            "qbit_client", "qbit_password", self.pass_word_var.get().strip()
        )
        apply_btn_parser.set(
            "qbit_client", "qbit_category", self.category_var.get().strip()
        )

        # save all settings in config file
        with open(self.configfile, "w") as apply_cfg:
            apply_btn_parser.write(apply_cfg)

        # show bask info prompt
        messagebox.showinfo(
            parent=self.qbit_window,
            title="Information",
            message="Making changes in qBittorrent WebUI or Category settings requires a "
            "client restart to work properly. Ensure that you have restarted the client "
            "before attempting to use automatic injection",
        )

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

    def show_error(self, error_message):
        messagebox.showerror(
            parent=self.qbit_window, title="Error", message=error_message
        )
