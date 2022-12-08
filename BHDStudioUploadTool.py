import base64
import math
import os
import pathlib
import re
import shutil
import subprocess
import sys
import threading
import tkinter.scrolledtext as scrolledtextwidget
import webbrowser
import zipfile
from ctypes import windll
from io import BytesIO
from queue import Queue, Empty
from random import choice
from tkinter import (
    filedialog,
    StringVar,
    ttk,
    messagebox,
    NORMAL,
    DISABLED,
    N,
    S,
    W,
    E,
    Toplevel,
    LabelFrame,
    END,
    Label,
    Checkbutton,
    OptionMenu,
    Entry,
    HORIZONTAL,
    SUNKEN,
    Button,
    TclError,
    font,
    Menu,
    Text,
    INSERT,
    colorchooser,
    Frame,
    Scrollbar,
    VERTICAL,
    PhotoImage,
    BooleanVar,
    Listbox,
    SINGLE,
    CENTER,
    WORD,
    LEFT,
    Spinbox,
    IntVar,
)

import awsmfunc
import pyperclip
import requests
import torf
import vapoursynth as vs
from PIL import Image, ImageTk
from cryptography.fernet import Fernet
from custom_hovertip import CustomTooltipLabel
from imdb import Cinemagoer
from numpy import linspace
from pymediainfo import MediaInfo
from tkinterdnd2 import DND_FILES, TkinterDnD
from torf import Torrent

from packages.About import openaboutwindow
from packages.default_config_params import *
from packages.deluge_window import DelugeWindow
from packages.dupe_checker import dupe_check
from packages.filter_title import edition_title_extractor
from packages.github_token import github_token
from packages.hoverbutton import HoverButton
from packages.icon import (
    base_64_icon,
    imdb_icon,
    tmdb_icon,
    bhd_upload_icon,
    bhd_upload_icon_disabled,
    seed_leech_arrow,
)
from packages.image_viewer import ImageViewer
from packages.qbittorrent_window import QBittorrentWindow
from packages.show_streams import stream_menu
from packages.source_pickle import get_saved_source_info, save_source_info
from packages.tmdb_key import tmdb_api_key
from packages.torrent_clients import Clients
from packages.user_pw_key import crypto_key

# check if program had a file dropped/any commands on the .exe or script upon launch
try:  # if it does set dropped file/command to a variable
    cli_command = sys.argv[1]
except IndexError:  # if it doesn't set variable to None
    cli_command = None

# determine if program is ran from exe or py
if pathlib.Path(sys.argv[0]).suffix == ".exe":
    app_type = "bundled"
else:
    app_type = "script"

# Set variable to True if you want errors to pop up in window + console, False for console only
if app_type == "bundled":
    enable_error_logger = (
        True  # Change this to false if you don't want to log errors to pop up window
    )
elif app_type == "script":
    enable_error_logger = False  # Enable this to true for debugging in dev environment

# Set main window title variable
main_root_title = "BHDStudio Upload Tool v1.64"

# create runtime folder if it does not exist
pathlib.Path(pathlib.Path.cwd() / "runtime").mkdir(parents=True, exist_ok=True)

# define theme colors based on user selection
if (
    config["themes"]["selected_theme"] == "bhd_theme"
    or config["themes"]["selected_theme"] == ""
):
    from packages.themes.bhd_theme import *

elif config["themes"]["selected_theme"] == "dark_green_theme":
    from packages.themes.dark_green_theme import *

elif config["themes"]["selected_theme"] == "dark_red_theme":
    from packages.themes.dark_red_theme import *

elif config["themes"]["selected_theme"] == "dark_yellow_theme":
    from packages.themes.dark_yellow_theme import *

elif config["themes"]["selected_theme"] == "dark_orange_theme":
    from packages.themes.dark_orange_theme import *

elif config["themes"]["selected_theme"] == "dark_cyan_theme":
    from packages.themes.dark_cyan_theme import *

elif config["themes"]["selected_theme"] == "dark_purple_theme":
    from packages.themes.dark_purple_theme import *

elif config["themes"]["selected_theme"] == "mid_dark_green_theme":
    from packages.themes.mid_dark_green_theme import *

elif config["themes"]["selected_theme"] == "mid_dark_red_theme":
    from packages.themes.mid_dark_red_theme import *

elif config["themes"]["selected_theme"] == "mid_dark_yellow_theme":
    from packages.themes.mid_dark_yellow_theme import *

elif config["themes"]["selected_theme"] == "mid_dark_orange_theme":
    from packages.themes.mid_dark_orange_theme import *

elif config["themes"]["selected_theme"] == "mid_dark_cyan_theme":
    from packages.themes.mid_dark_cyan_theme import *

elif config["themes"]["selected_theme"] == "mid_dark_purple_theme":
    from packages.themes.mid_dark_purple_theme import *

elif config["themes"]["selected_theme"] == "light_theme":
    from packages.themes.light_theme import *


def root_exit_function():
    """root exit function"""

    def save_config_information_root():
        # root exit parser
        root_exit_parser = ConfigParser()
        root_exit_parser.read(config_file)

        # save main gui window position/geometry
        if root.wm_state() == "normal":
            if (
                root_exit_parser["save_window_locations"]["bhdstudiotool"]
                != root.geometry()
            ):
                root_exit_parser.set(
                    "save_window_locations", "bhdstudiotool", root.geometry()
                )
                with open(config_file, "w") as root_exit_config_file:
                    root_exit_parser.write(root_exit_config_file)

    # check for opened windows before closing
    open_tops = False  # Set variable for open toplevel windows
    for widget in root.winfo_children():  # Loop through roots children
        if isinstance(
            widget, Toplevel
        ):  # If any of roots children is a TopLevel window
            open_tops = True  # Set variable for open tops to True
    if open_tops:  # If open_tops is True
        confirm_exit = messagebox.askyesno(
            title="Prompt",
            message="Are you sure you want to exit the program?\n\n"
            "Warning: This will close all windows",
            parent=root,
        )
        if confirm_exit:  # If user wants to exit, kill app and all of it's children
            save_config_information_root()
            root.destroy()  # root destroy
    if not open_tops:  # If no top levels are found, exit the program without prompt
        save_config_information_root()
        root.destroy()  # root destroy


# define root
root = TkinterDnD.Tk()

# define temp widgets to get default system colors
if config["themes"]["selected_theme"] == "system_theme":
    custom_window_bg_color = root.cget("bg")

    temp_btn = Button()
    custom_button_colors = {
        "foreground": temp_btn.cget("fg"),
        "background": temp_btn.cget("bg"),
        "activeforeground": temp_btn.cget("activeforeground"),
        "activebackground": temp_btn.cget("activebackground"),
        "disabledforeground": temp_btn.cget("disabledforeground"),
    }

    temp_entry = Entry()
    custom_entry_colors = {
        "foreground": temp_entry.cget("fg"),
        "background": temp_entry.cget("bg"),
        "disabledforeground": temp_entry.cget("disabledforeground"),
        "disabledbackground": temp_entry.cget("disabledbackground"),
    }

    temp_lbl_frame = LabelFrame()
    custom_label_frame_colors = {
        "foreground": temp_lbl_frame.cget("fg"),
        "background": temp_lbl_frame.cget("bg"),
    }

    temp_frame = Frame()
    custom_frame_bg_colors = {
        "background": temp_frame.cget("bg"),
        "highlightcolor": temp_frame.cget("highlightcolor"),
        "specialbg": temp_frame.cget("bg"),
    }

    temp_label = Label()
    custom_label_colors = {
        "foreground": temp_label.cget("fg"),
        "background": temp_label.cget("bg"),
    }

    temp_scrolled_text = scrolledtextwidget.ScrolledText()
    custom_scrolled_text_widget_color = {
        "foreground": temp_scrolled_text.cget("fg"),
        "background": temp_scrolled_text.cget("bg"),
    }

    temp_listbox = Listbox()
    custom_listbox_color = {
        "foreground": temp_listbox.cget("fg"),
        "background": temp_listbox.cget("bg"),
        "selectbackground": temp_listbox.cget("selectbackground"),
        "selectforeground": temp_listbox.cget("selectforeground"),
    }

    temp_spinbox = Spinbox()
    custom_spinbox_color = {
        "foreground": temp_spinbox.cget("fg"),
        "background": temp_spinbox.cget("bg"),
        "buttonbackground": temp_spinbox.cget("buttonbackground"),
        "readonlybackground": temp_spinbox.cget("readonlybackground"),
    }

    temp_text = Text()
    custom_text_color = {
        "background": temp_text.cget("bg"),
        "foreground": temp_text.cget("fg"),
    }

# root window configuration
root.title(main_root_title)
root.title(main_root_title)
root.iconphoto(True, PhotoImage(data=base_64_icon))
root.configure(background=custom_window_bg_color)
if config["save_window_locations"]["bhdstudiotool"] != "":
    root.geometry(config["save_window_locations"]["bhdstudiotool"])
root.protocol("WM_DELETE_WINDOW", root_exit_function)

# Block of code to fix DPI awareness issues on Windows 7 or higher
try:
    windll.shcore.SetProcessDpiAwareness(2)  # if your Windows version >= 8.1
except (Exception,):
    windll.user32.SetProcessDPIAware()  # Windows 8.0 or less
# Block of code to fix DPI awareness issues on Windows 7 or higher

for n in range(4):
    root.grid_columnconfigure(n, weight=1)
for n in range(5):
    root.grid_rowconfigure(n, weight=1)

detect_font = font.nametofont(
    "TkDefaultFont"
)  # Get default font value into Font object
set_font = detect_font.actual().get("family")
default_font_size = detect_font.actual().get("size")
if config["ui_scale"]["value"] != "0":
    set_font_size = int(config["ui_scale"]["value"])
else:
    set_font_size = default_font_size
detect_fixed_font = font.nametofont("TkFixedFont")
set_fixed_font = detect_fixed_font.actual().get("family")

if config["themes"]["selected_theme"] != "system_theme":
    # Custom Tkinter Theme-----------------------------------------
    custom_style = ttk.Style()
    custom_style.theme_create(
        "jlw_style",
        parent="alt",
        settings={
            # Notebook Theme Settings -------------------
            "TNotebook": {
                "configure": {
                    "tabmargins": [5, 5, 5, 0],
                    "background": custom_frame_bg_colors["background"],
                }
            },
            "TNotebook.Tab": {
                "configure": {
                    "padding": [5, 1],
                    "background": custom_listbox_color["selectbackground"],
                    "foreground": custom_button_colors["foreground"],
                    "focuscolor": "",
                },
                "map": {
                    "background": [("selected", custom_frame_bg_colors["specialbg"])],
                    "expand": [("selected", [1, 1, 1, 0])],
                },
            },
            # Notebook Theme Settings -------------------
            # ComboBox Theme Settings -------------------
            "TCombobox": {
                "configure": {
                    "selectbackground": custom_listbox_color["selectbackground"],
                    "fieldbackground": custom_listbox_color["selectbackground"],
                    "foreground": custom_listbox_color["foreground"],
                    "selectforeground": custom_listbox_color["selectforeground"],
                }
            },
        },
        # ComboBox Theme Settings -------------------
    )
    custom_style.theme_use("jlw_style")  # Enable the use of the custom theme
    custom_style.layout(
        "text.Horizontal.TProgressbar",
        [
            (
                "Horizontal.Progressbar.trough",
                {
                    "children": [
                        (
                            "Horizontal.Progressbar.pbar",
                            {"side": "left", "sticky": "ns"},
                        )
                    ],
                    "sticky": "nswe",
                },
            ),
            ("Horizontal.Progressbar.label", {"sticky": "nswe"}),
        ],
    )
    # set initial text
    custom_style.configure(
        "text.Horizontal.TProgressbar",
        text="",
        anchor="center",
        background=custom_button_colors["foreground"],
        foreground=custom_button_colors["activeforeground"],
    )
    custom_style.master.option_add(
        "*TCombobox*Listbox.foreground", custom_listbox_color["foreground"]
    )
    custom_style.master.option_add(
        "*TCombobox*Listbox.background", custom_listbox_color["background"]
    )
    custom_style.master.option_add(
        "*TCombobox*Listbox.selectBackground", custom_listbox_color["background"]
    )
    custom_style.master.option_add(
        "*TCombobox*Listbox.selectForeground", custom_listbox_color["selectforeground"]
    )

    # ------------------------------------------ Custom Tkinter Theme


# Logger class, handles all traceback/stdout errors for program, writes to file and to window -------------------------
class Logger(
    object
):  # Logger class, this class puts stderr errors into a window and file at the same time
    def __init__(self):
        self.terminal = sys.stderr  # Redirects sys.stderr

    def write(self, message):
        global info_scrolled
        self.terminal.write(message)
        try:
            info_scrolled.config(state=NORMAL)
            if str(message).rstrip():
                info_scrolled.insert(END, str(message).strip())
            if not str(message).rstrip():
                info_scrolled.insert(END, f"{str(message)}\n")
            info_scrolled.see(END)
            info_scrolled.config(state=DISABLED)
        except (NameError, TclError):
            error_window = Toplevel()
            error_window.title("Traceback Error(s)")
            error_window.configure(background=custom_window_bg_color)
            window_height = 400
            window_width = 600
            error_window.geometry(
                f'{window_width}x{window_height}+{root.geometry().split("+")[1]}+'
                f'{root.geometry().split("+")[2]}'
            )
            for e_w in range(4):
                error_window.grid_columnconfigure(e_w, weight=1)
            error_window.grid_rowconfigure(0, weight=1)
            info_scrolled = scrolledtextwidget.ScrolledText(
                error_window,
                wrap=WORD,
                bd=8,
                bg=custom_scrolled_text_widget_color["background"],
                fg=custom_scrolled_text_widget_color["foreground"],
            )
            info_scrolled.grid(
                row=0, column=0, columnspan=4, pady=5, padx=5, sticky=E + W + N + S
            )

            info_scrolled.insert(END, message)
            info_scrolled.see(END)
            info_scrolled.config(state=DISABLED)

            report_error = HoverButton(
                error_window,
                text="Report Error",
                command=lambda: webbrowser.open(
                    "https://github.com/jlw4049/BHDStudio-Upload-"
                    "Tool/issues/new?assignees=jlw4049&labels=bug"
                    "&template=bug_report.md&title="
                ),
                borderwidth="3",
                foreground=custom_button_colors["foreground"],
                background=custom_button_colors["background"],
                activeforeground=custom_button_colors["activeforeground"],
                activebackground=custom_button_colors["activebackground"],
                disabledforeground=custom_button_colors["disabledforeground"],
            )
            report_error.grid(
                row=1, column=3, columnspan=1, padx=10, pady=(5, 4), sticky=S + E + N
            )

            force_close_root = HoverButton(
                error_window,
                text="Force Close Program",
                command=root.destroy,
                borderwidth="3",
                foreground=custom_button_colors["foreground"],
                background=custom_button_colors["background"],
                activeforeground=custom_button_colors["activeforeground"],
                activebackground=custom_button_colors["activebackground"],
                disabledforeground=custom_button_colors["disabledforeground"],
            )
            force_close_root.grid(
                row=1, column=0, columnspan=1, padx=10, pady=(5, 4), sticky=S + W + N
            )

            def right_click_menu_func(x_y_pos):
                """mouse button 3 (right click) to pop up menu"""

                # get the position of cursor
                right_click_menu.tk_popup(x_y_pos.x_root, x_y_pos.y_root)

            right_click_menu = Menu(
                info_scrolled, tearoff=False
            )  # This is the right click menu
            right_click_menu.add_command(
                label="Copy to clipboard",
                command=lambda: pyperclip.copy(info_scrolled.get(1.0, END).strip()),
            )
            info_scrolled.bind(
                "<Button-3>", right_click_menu_func
            )  # Uses mouse button 3 to open the menu
            CustomTooltipLabel(
                info_scrolled, "Right click to copy", hover_delay=800
            )  # Hover tip tool-tip
            error_window.grab_set()  # Brings attention to this window until it's closed
            root.bell()  # Error bell sound

    def flush(self):
        pass

    def __exit__(self):  # Class exit function
        sys.stderr = sys.__stderr__  # Redirect stderr back to original stderr
        # self.error_log_file.close()  # Close file


# start logger if enabled
if enable_error_logger:
    sys.stderr = Logger()

# variables to be used within the program
source_file_path = StringVar()
source_loaded = StringVar()
source_file_information = {}
encode_file_path = StringVar()
encode_file_rename = BooleanVar()
encode_file_resolution = StringVar()
encode_media_info = StringVar()
encode_file_audio = StringVar()
encode_hdr_string = StringVar()
torrent_file_path = StringVar()
nfo_info_var = StringVar()
automatic_workflow_boolean = BooleanVar()
live_boolean = BooleanVar()
anonymous_boolean = BooleanVar()
movie_search_var = StringVar()
movie_search_active = BooleanVar()
tmdb_id_var = StringVar()
imdb_id_var = StringVar()
release_date_var = StringVar()
rating_var = StringVar()
screenshot_comparison_var = StringVar()
screenshot_selected_var = StringVar()
screenshot_sync_var = StringVar()
loaded_script_info = StringVar()
script_mode = StringVar()
input_script_path = StringVar()


# function to clear all variables
def clear_all_variables():
    source_file_path.set("")
    source_loaded.set("")
    source_file_information.clear()
    encode_file_path.set("")
    encode_file_rename.set(False)
    encode_file_resolution.set("")
    encode_media_info.set("")
    encode_file_audio.set("")
    encode_hdr_string.set("")
    torrent_file_path.set("")
    nfo_info_var.set("")
    automatic_workflow_boolean.set(False)
    live_boolean.set(False)
    anonymous_boolean.set(False)
    movie_search_var.set("")
    movie_search_active.set(False)
    tmdb_id_var.set("")
    imdb_id_var.set("")
    release_date_var.set("")
    rating_var.set("")
    screenshot_comparison_var.set("")
    screenshot_selected_var.set("")
    screenshot_sync_var.set("")
    loaded_script_info.set("")
    script_mode.set("")
    input_script_path.set("")


# function to open imdb links with and without the id
def open_imdb_link():
    if imdb_id_var.get() != "":
        webbrowser.open(f"https://imdb.com/title/{imdb_id_var.get()}")
    else:
        webbrowser.open("https://www.imdb.com/")


# function to open tmdb links with and without the id
def open_tmdb_link():
    if tmdb_id_var.get() != "":
        webbrowser.open(f"https://www.themoviedb.org/movie/{tmdb_id_var.get()}")
    else:
        webbrowser.open("https://www.themoviedb.org/movie")


# function to search tmdb for information
def search_movie_global_function(*args):
    # set parser
    movie_window_parser = ConfigParser()
    movie_window_parser.read(config_file)

    # decode imdb img for use with the buttons
    decode_resize_imdb_image = Image.open(BytesIO(base64.b64decode(imdb_icon))).resize(
        (35, 35)
    )
    imdb_img = ImageTk.PhotoImage(decode_resize_imdb_image)

    # decode tmdb img for use with the buttons
    decode_resize_tmdb_image = Image.open(BytesIO(base64.b64decode(tmdb_icon))).resize(
        (35, 35)
    )
    tmdb_img = ImageTk.PhotoImage(decode_resize_tmdb_image)

    def movie_info_exit_function():
        """movie window exit function"""

        # set stop thread to True
        stop_thread.set()

        # set parser
        exit_movie_window_parser = ConfigParser()
        exit_movie_window_parser.read(config_file)

        # save window position/geometry
        if movie_info_window.wm_state() == "normal":
            if (
                exit_movie_window_parser["save_window_locations"]["movie_info"]
                != movie_info_window.geometry()
            ):
                exit_movie_window_parser.set(
                    "save_window_locations",
                    "movie_info",
                    movie_info_window.geometry(),
                )
                with open(config_file, "w") as root_exit_config_file:
                    exit_movie_window_parser.write(root_exit_config_file)

        # close movie info window
        movie_info_window.destroy()

    def get_imdb_update_filename():
        """function to get imdb title name as well as id's for both imdb and tmdb"""
        # check if imdb id is missing
        if imdb_id_var.get() == "None":
            messagebox.showerror(
                parent=movie_info_window,
                title="Missing IMDb ID",
                message="Please manually search for the proper IMDb ID and manually "
                "add it to the IMDb entry box",
            )
            return  # exit the function

        # if there is an imdb title
        if "t" in imdb_id_var.get():
            imdb_module = Cinemagoer()
            movie = imdb_module.get_movie(str(imdb_id_var.get()).replace("t", ""))
            imdb_movie_name = f"{str(movie['title'])} {str(movie['year'])}"
            source_file_information.update(
                {
                    "imdb_movie_name": imdb_movie_name,
                    "imdb_id": imdb_id_var.get(),
                    "tmdb_id": tmdb_id_var.get(),
                    "source_movie_year": f"{str(movie['year'])}",
                }
            )

        # if user has not selected anything in the window
        elif imdb_id_var.get().strip() == "":
            messagebox.showinfo(
                parent=movie_info_window,
                title="Prompt",
                message='You must select a movie before clicking "Confirm"',
            )
            return  # exit the function

        movie_info_exit_function()  # close movie_info_window

    # movie info window
    movie_info_window = Toplevel()
    movie_info_window.configure(
        background=custom_window_bg_color
    )  # Set's the background color
    movie_info_window.title("Movie Selection")  # Toplevel Title
    if movie_window_parser["save_window_locations"]["movie_info"] != "":
        movie_info_window.geometry(
            movie_window_parser["save_window_locations"]["movie_info"]
        )
    movie_info_window.grab_set()
    movie_info_window.protocol("WM_DELETE_WINDOW", movie_info_exit_function)

    # Row/Grid configures
    for m_i_w_c in range(6):
        movie_info_window.grid_columnconfigure(m_i_w_c, weight=1)
    for m_i_w_r in range(4):
        movie_info_window.grid_rowconfigure(m_i_w_r, weight=1)
    # Row/Grid configures

    # Set dynamic listbox frame
    movie_listbox_frame = Frame(
        movie_info_window, bg=custom_frame_bg_colors["background"]
    )
    movie_listbox_frame.grid(
        column=0, columnspan=6, row=0, padx=5, pady=(5, 3), sticky=N + S + E + W
    )
    movie_listbox_frame.grid_rowconfigure(0, weight=1)
    movie_listbox_frame.grid_columnconfigure(0, weight=1)

    right_scrollbar = Scrollbar(movie_listbox_frame, orient=VERTICAL)  # Scrollbars
    bottom_scrollbar = Scrollbar(movie_listbox_frame, orient=HORIZONTAL)

    # Create listbox
    movie_listbox = Listbox(
        movie_listbox_frame,
        xscrollcommand=bottom_scrollbar.set,
        activestyle="none",
        yscrollcommand=right_scrollbar.set,
        bd=2,
        height=10,
        selectmode=SINGLE,
        font=(set_font, set_font_size + 2),
        bg=custom_listbox_color["background"],
        fg=custom_listbox_color["foreground"],
        selectbackground=custom_listbox_color["selectbackground"],
        selectforeground=custom_listbox_color["selectforeground"],
    )
    movie_listbox.grid(row=0, column=0, columnspan=5, sticky=N + E + S + W)

    # add scrollbars to the listbox
    right_scrollbar.config(command=movie_listbox.yview)
    right_scrollbar.grid(row=0, column=5, rowspan=2, sticky=N + W + S)
    bottom_scrollbar.config(command=movie_listbox.xview)
    bottom_scrollbar.grid(row=1, column=0, sticky=W + E + N)

    # define stop thread event
    stop_thread = threading.Event()

    # define api thread queue
    api_thread_queue = Queue()

    def update_movie_listbox(movie_dict):
        """update the list box with supplied dictionary"""

        # loop through the keys (movie titles) and display them in the listbox
        for key in movie_dict.keys():
            movie_listbox.insert(END, key)

        # function that is run each time a movie is selected to update all the information in the window
        def update_movie_info(event):
            selection = event.widget.curselection()  # get current selection
            # if there is a selection
            if selection:
                movie_listbox_index = selection[0]  # define index of selection
                movie_data = event.widget.get(movie_listbox_index)

                # delete plot text and update it
                plot_scrolled_text.delete("1.0", END)
                plot_scrolled_text.insert(END, movie_dict[movie_data]["plot"])

                # update imdb and tmdb entry box's
                imdb_id_var.set(movie_dict[movie_data]["imdb_id"])
                tmdb_id_var.set(movie_dict[movie_data]["tvdb_id"])

                # update release date label
                release_date_var.set(movie_dict[movie_data]["full_release_date"])

                # update rating label
                rating_var.set(f"{movie_dict[movie_data]['vote_average']} / 10")

        # bind listbox select event to the updater
        movie_listbox.bind("<<ListboxSelect>>", update_movie_info)

    def api_thread_poll_loop():
        """loop to poll the queue and update the GUI for the api search function"""

        # if there is data set it to a variable
        try:
            api_queue_data = api_thread_queue.get_nowait()
        except Empty:
            api_queue_data = None

        # if data is not equal to None
        if api_queue_data is not None:

            # if False is sent to the queue exit this loop
            if not api_queue_data:
                # send task done to the queue
                api_thread_queue.task_done()

                # exit this loop
                return

            # if the data has Error as the first key, use this to spawn message box's
            elif list(api_queue_data.keys())[0] == "Error":
                # spawn message box
                messagebox.showerror(
                    parent=movie_info_window,
                    title=api_queue_data["Error"]["title"],
                    message=api_queue_data["Error"]["message"],
                )

                # send task done to the queue
                api_thread_queue.task_done()

                # join queue thread to exit safely
                api_thread_queue.join()

                # exit this loop
                return

            # if the data has "Listbox" as the first key, control basic listbox functions
            elif list(api_queue_data.keys())[0] == "Listbox":

                # delete listbox contents
                if api_queue_data["Listbox"] == "Delete":
                    # send task done to the queue
                    api_thread_queue.task_done()

                    # delete movie list box
                    movie_listbox.delete(0, END)

                # if it's a simple string that IS NOT Delete, display it in the list box
                elif api_queue_data["Listbox"] != "Delete":
                    # send task done to the queue
                    api_thread_queue.task_done()

                    # insert simple string into the listbox
                    movie_listbox.insert(END, api_queue_data["Listbox"])

            # if the data has "Listbox Dict", run the function to update the listbox with the queued dictionary
            elif list(api_queue_data.keys())[0] == "Listbox Dict":
                # send task done to the queue
                api_thread_queue.task_done()

                # update listbox with listbox dict information
                update_movie_listbox(api_queue_data["Listbox Dict"])

        # keep polling data every millisecond
        root.after(1, api_thread_poll_loop)

    def run_api_check(api_queue):
        """threaded search tmdb for input"""

        if movie_search_active.get():
            return

        # set movie_search_active to True, in order to not allow another thread to be started
        movie_search_active.set(True)

        # send api queue to delete listbox and add text to it
        api_queue.put({"Listbox": "Delete"})
        api_queue.put({"Listbox": "Loading, please wait..."})

        # regex to collect title name
        collect_title = re.finditer(r"\d{4}", movie_search_var.get().strip())

        # create empty list
        title_span = []

        # loop through the regex to collect title only
        for title_only in collect_title:
            title_span.append(title_only.span())

        # attempt to remove anything extra from title name
        try:
            movie_title = (
                str(movie_search_var.get()[0 : title_span[-1][0]])
                .replace(".", " ")
                .replace("(", "")
                .replace(")", "")
                .strip()
            )
        except IndexError:
            movie_title = str(movie_search_var.get().strip())

        # attempt to get only the movie title year
        collect_year = re.findall(r"\d{4}", movie_search_var.get().strip())

        # if any 4 digits are detected in the string
        if collect_year:

            # get only the last set of digits
            movie_year = collect_year[-1]

        # if no 4 digits are detected set movie year to ""
        else:
            movie_year = ""

        # try to get imdb movie name from tmdb
        try:
            search_movie = requests.get(
                f"https://api.themoviedb.org/3/search/movie?api_key={tmdb_api_key}&language"
                f"=en-US&page=1&include_adult=false&query={movie_title}&year={movie_year}"
            )
        except requests.exceptions.ConnectionError:
            # if there was an error set imdb_movie_name to "None"
            source_file_information.update({"imdb_movie_name": "None"})

            # prompt a message box via the api queue
            api_queue.put(
                {
                    "Error": {
                        "title": "Connection Error",
                        "message": "There was an error connecting to "
                        "the internet.\n\nTitle name will be "
                        "determined from source file only",
                    }
                }
            )

            # exit the movie info window
            movie_info_exit_function()

            # exit this function
            return

        # define an empty dictionary
        movie_dict = {}

        # loop through json results
        for results in search_movie.json()["results"]:
            # find imdb_id data through tmdb
            imdb_id = requests.get(
                f"https://api.themoviedb.org/3/movie/{results['id']}/external_ids?api_key={tmdb_api_key}"
            )
            # if release date string isn't nothing
            if imdb_id.json()["imdb_id"] and results["release_date"]:
                # convert release date to standard month/day/year
                release_date = str(results["release_date"]).split("-")
                full_release_date = (
                    f"{release_date[1]}-{release_date[2]}-{release_date[0]}"
                )
                # update dictionary
                movie_dict.update(
                    {
                        f"{results['title']} ({release_date[0]})": {
                            "tvdb_id": f"{results['id']}",
                            "imdb_id": f"{imdb_id.json()['imdb_id']}",
                            "plot": f"{results['overview']}",
                            "vote_average": f"{str(results['vote_average'])}",
                            "full_release_date": full_release_date,
                        }
                    }
                )
                # if thread event stop was called
                if stop_thread.is_set():
                    movie_search_active.set(False)  # set active search to false
                    break  # break from loop

        # if stop_thread was called and closed the loop
        if not movie_search_active.get():
            return  # exit function

        # clear movie list box
        api_queue.put({"Listbox": "Delete"})

        # add all the movies into a listbox dict
        api_queue.put({"Listbox Dict": movie_dict})

        # set active search to false
        movie_search_active.set(False)

        # set api queue to false in order to kill the polling loop
        api_queue.put(False)

    # plot frame
    plot_frame = LabelFrame(
        movie_info_window,
        text=" Plot ",
        labelanchor="nw",
        bd=3,
        font=(set_font, set_font_size, "bold"),
        fg=custom_label_frame_colors["foreground"],
        bg=custom_label_frame_colors["background"],
    )
    plot_frame.grid(column=0, row=1, columnspan=6, padx=5, pady=(5, 3), sticky=E + W)

    plot_frame.grid_rowconfigure(0, weight=1)
    plot_frame.grid_columnconfigure(0, weight=1)

    # plot text window
    plot_scrolled_text = scrolledtextwidget.ScrolledText(
        plot_frame,
        height=6,
        wrap=WORD,
        bd=2,
        bg=custom_scrolled_text_widget_color["background"],
        fg=custom_scrolled_text_widget_color["foreground"],
    )
    plot_scrolled_text.grid(
        row=0, column=0, columnspan=6, pady=(0, 5), padx=5, sticky=E + W
    )

    # internal search frame
    internal_search_frame = LabelFrame(
        movie_info_window,
        text=" Search ",
        labelanchor="nw",
        bd=3,
        font=(set_font, set_font_size, "bold"),
        fg=custom_label_frame_colors["foreground"],
        bg=custom_label_frame_colors["background"],
    )
    internal_search_frame.grid(
        column=0, row=2, columnspan=6, padx=5, pady=(5, 3), sticky=E + W
    )

    internal_search_frame.grid_rowconfigure(0, weight=1)
    internal_search_frame.grid_rowconfigure(1, weight=1)
    internal_search_frame.grid_columnconfigure(0, weight=1)

    # movie selection label frame
    movie_selection_lbl_frame = LabelFrame(
        internal_search_frame, bg=custom_label_frame_colors["background"], border=0
    )
    movie_selection_lbl_frame.grid(column=0, row=0, columnspan=6, sticky=E + W)
    movie_selection_lbl_frame.grid_rowconfigure(0, weight=1)
    movie_selection_lbl_frame.grid_columnconfigure(0, weight=1)
    movie_selection_lbl_frame.grid_columnconfigure(1, weight=100)

    source_input_lbl_ms = Label(
        movie_selection_lbl_frame,
        text=f"Source Name:",
        background=custom_label_colors["background"],
        fg=custom_label_colors["foreground"],
        font=(set_font, set_font_size - 1, "bold"),
    )
    source_input_lbl_ms.grid(
        row=0, column=0, columnspan=1, padx=(5, 0), pady=(5, 3), sticky=W
    )

    try:
        source_path_name = str(
            pathlib.Path(
                pathlib.Path(source_file_information["source_path"]).name
            ).with_suffix("")
        )
    except KeyError:
        source_path_name = ""

    source_input_lbl_ms2 = Label(
        movie_selection_lbl_frame,
        wraplength=960,
        text=str(source_path_name),
        background=custom_label_colors["background"],
        fg=custom_label_colors["foreground"],
        font=(set_fixed_font, set_font_size - 1),
    )
    source_input_lbl_ms2.grid(
        row=0, column=1, columnspan=5, padx=(2, 5), pady=(5, 3), sticky=W
    )

    # internal search box
    search_entry_box2 = Entry(
        internal_search_frame,
        borderwidth=4,
        textvariable=movie_search_var,
        fg=custom_entry_colors["foreground"],
        bg=custom_entry_colors["background"],
        disabledforeground=custom_entry_colors["disabledforeground"],
        disabledbackground=custom_entry_colors["disabledbackground"],
        font=(set_fixed_font, set_font_size),
    )
    search_entry_box2.grid(
        row=1, column=0, columnspan=5, padx=5, pady=(5, 3), sticky=E + W
    )

    # run function to get title name only
    movie_input_filtered = edition_title_extractor(str(source_path_name))[1]

    # insert movie into entry box/update var
    movie_search_var.set(movie_input_filtered)

    def start_search(*enter_args):
        """thread the search for the movie title"""

        # set stop thread to false
        stop_thread.clear()

        # define thread to search for movie title
        api_thread = threading.Thread(
            target=run_api_check, args=(api_thread_queue,), daemon=True
        )

        # start loop to poll queue
        root.after(100, api_thread_poll_loop)

        # start thread
        api_thread.start()

    # bind "Enter" key to run the function
    search_entry_box2.bind("<Return>", start_search)

    # internal search button
    search_button2 = HoverButton(
        internal_search_frame,
        text="Search",
        command=start_search,
        borderwidth="3",
        width=12,
        foreground=custom_button_colors["foreground"],
        background=custom_button_colors["background"],
        activeforeground=custom_button_colors["activeforeground"],
        activebackground=custom_button_colors["activebackground"],
        disabledforeground=custom_button_colors["disabledforeground"],
    )
    search_button2.grid(
        row=1, column=5, columnspan=1, padx=5, pady=(5, 3), sticky=E + S + N
    )

    def enable_disable_internal_search_btn():
        """function to enable and disable the internal search button if a current search is active"""

        try:
            if movie_search_active.get():  # if search is active disable button
                search_button2.config(state=DISABLED)
            else:  # if search is not active enable button
                search_button2.config(state=NORMAL)
        except TclError:
            pass

        # loop to enable/disable buttons
        movie_info_window.after(50, enable_disable_internal_search_btn)

    # start loop to check internal button
    enable_disable_internal_search_btn()

    # information frame
    information_frame = Frame(
        movie_info_window, bd=0, bg=custom_frame_bg_colors["background"]
    )
    information_frame.grid(
        column=0, row=3, columnspan=7, padx=5, pady=(5, 3), sticky=E + W
    )
    information_frame.grid_rowconfigure(0, weight=1)
    information_frame.grid_rowconfigure(1, weight=1)
    information_frame.grid_columnconfigure(0, weight=1)
    information_frame.grid_columnconfigure(1, weight=100)
    information_frame.grid_columnconfigure(2, weight=1000)
    information_frame.grid_columnconfigure(3, weight=10000)
    information_frame.grid_columnconfigure(4, weight=100000)
    information_frame.grid_columnconfigure(5, weight=1000000)
    information_frame.grid_columnconfigure(6, weight=1)

    # imdb clickable icon button
    imdb_button2 = Button(
        information_frame,
        image=imdb_img,
        borderwidth=0,
        cursor="hand2",
        bg=custom_window_bg_color,
        activebackground=custom_window_bg_color,
        command=open_imdb_link,
    )
    imdb_button2.grid(
        row=0, column=0, columnspan=1, rowspan=2, padx=5, pady=(5, 2), sticky=W
    )
    imdb_button2.photo = imdb_img

    # imdb entry box internal
    imdb_entry_box2 = Entry(
        information_frame,
        borderwidth=4,
        textvariable=imdb_id_var,
        fg=custom_entry_colors["foreground"],
        bg=custom_entry_colors["background"],
        disabledforeground=custom_entry_colors["disabledforeground"],
        disabledbackground=custom_entry_colors["disabledbackground"],
        font=(set_fixed_font, set_font_size),
    )
    imdb_entry_box2.grid(row=0, column=1, rowspan=2, padx=5, pady=(5, 2), sticky=W)

    # tmdb clickable icon button
    tmdb_button2 = Button(
        information_frame,
        image=tmdb_img,
        borderwidth=0,
        cursor="hand2",
        bg=custom_window_bg_color,
        activebackground=custom_window_bg_color,
        command=open_tmdb_link,
    )
    tmdb_button2.grid(row=0, column=2, rowspan=2, padx=5, pady=(5, 2), sticky=W)
    tmdb_button2.photo = tmdb_img

    # tmdb internal entry box
    tmdb_entry_box2 = Entry(
        information_frame,
        borderwidth=4,
        textvariable=tmdb_id_var,
        fg=custom_entry_colors["foreground"],
        bg=custom_entry_colors["background"],
        disabledforeground=custom_entry_colors["disabledforeground"],
        disabledbackground=custom_entry_colors["disabledbackground"],
        font=(set_fixed_font, set_font_size),
    )
    tmdb_entry_box2.grid(row=0, column=3, rowspan=2, padx=5, pady=(5, 2), sticky=W)

    # release date labels
    release_date_label = Label(
        information_frame,
        text="Release Date:",
        background=custom_label_colors["background"],
        fg=custom_label_colors["foreground"],
        font=(set_font, set_font_size + 1, "bold"),
    )
    release_date_label.grid(row=0, column=4, sticky=W, padx=(5, 0), pady=(5, 2))

    release_date_label2 = Label(
        information_frame,
        textvariable=release_date_var,
        width=10,
        background=custom_label_colors["background"],
        fg=custom_label_colors["foreground"],
        font=(set_font, set_font_size),
    )
    release_date_label2.grid(row=0, column=5, sticky=W, padx=(1, 5), pady=(5, 2))

    # rating labels
    rating_label = Label(
        information_frame,
        text="           Rating:",
        background=custom_label_colors["background"],
        fg=custom_label_colors["foreground"],
        font=(set_font, set_font_size + 1, "bold"),
    )
    rating_label.grid(row=1, column=4, sticky=W, padx=(5, 0), pady=(5, 2))

    rating_label2 = Label(
        information_frame,
        textvariable=rating_var,
        width=10,
        background=custom_label_colors["background"],
        fg=custom_label_colors["foreground"],
        font=(set_font, set_font_size),
    )
    rating_label2.grid(row=1, column=5, sticky=W, padx=(1, 5), pady=(5, 2))

    # confirm movie button
    confirm_movie_btn = HoverButton(
        information_frame,
        text="Confirm",
        command=get_imdb_update_filename,
        borderwidth="3",
        width=10,
        foreground=custom_button_colors["foreground"],
        background=custom_button_colors["background"],
        activeforeground=custom_button_colors["activeforeground"],
        activebackground=custom_button_colors["activebackground"],
        disabledforeground=custom_button_colors["disabledforeground"],
    )
    confirm_movie_btn.grid(row=1, column=6, padx=5, pady=(5, 2), sticky=E)

    movie_info_window.focus_set()  # focus's id window

    # clear movie list box
    movie_listbox.delete(0, END)

    # set stop thread event to false
    stop_thread.clear()

    # start thread to search for movie title
    if source_path_name != "":
        start_search()

    # wait for window to close
    movie_info_window.wait_window()


def source_input_function(*args):
    """function for source file input"""

    # define parser
    source_input_parser = ConfigParser()
    source_input_parser.read(config_file)

    # update last used folder
    source_input_parser.set("last_used_folder", "path", str(pathlib.Path(*args).parent))
    with open(config_file, "w") as s_i_c_config:
        source_input_parser.write(s_i_c_config)

    # update directory variable
    if pathlib.Path(source_input_parser["last_used_folder"]["path"]).is_dir():
        s_i_f_initial_dir = pathlib.Path(
            source_input_parser["last_used_folder"]["path"]
        )
    else:
        s_i_f_initial_dir = "/"

    # check if script is the correct script
    if str(pathlib.Path(pathlib.Path(*args).name).with_suffix("")).endswith("_source"):
        messagebox.showinfo(
            parent=root,
            title="Wrong script file",
            message='You must select the script without the suffix "_source" '
            "in the filename before the scripts extension",
        )
        return  # exit this function

    # clear variables and boxes
    image_listbox.config(state=NORMAL)  # enable image list box
    image_listbox.delete(0, END)  # delete image list box contents
    image_listbox.config(state=DISABLED)  # disable image list box
    screenshot_scrolledtext.delete("1.0", END)  # clear contents of url notebook tab
    tabs.select(image_tab)  # select first tab in the image box
    delete_encode_entry()  # clear encode entry
    source_file_information.clear()  # clear dictionary
    delete_source_entry()  # clear source entry
    clear_all_variables()  # clear all variables
    audio_pop_up_var = StringVar()  # audio pop up var

    # check if script is avisynth
    if pathlib.Path(*args).suffix == ".avs":
        script_mode.set("avs")
    # check if script is vapoursynth
    elif pathlib.Path(*args).suffix == ".vpy":
        script_mode.set("vpy")
    # if input is not a script
    else:
        messagebox.showerror(
            parent=root,
            title="Incorrect File",
            message="Dropped file must be an AviSynth or VapourSynth script",
        )
        return  # exit the function

    # assign path to script file for later use
    input_script_path.set(*args)

    # open avisynth script
    if script_mode.get() == "avs":
        with open(*args, "rt") as encode_script:
            # search file for info
            search_file = encode_script.read()
            get_source_file = re.search(r'FFVideoSource\("(.+?)",', search_file)
            get_crop = re.search(r"Crop\((.+)\)", search_file)

            # load search file to global string var to be used by encode function
            loaded_script_info.set(search_file)

    # open vapoursynth script
    elif script_mode.get() == "vpy":
        with open(*args, "rt") as encode_script:
            # search file for info
            search_file = encode_script.read()
            get_source_file = re.search(
                r'else core\.ffms2\.Source\(r"(.+?)",', search_file
            )
            get_crop = re.search(r"Crop\(clip,\s(.+)\)", search_file)

            # load search file to global string var to be used by encode function
            loaded_script_info.set(search_file)

    # if we cannot locate the source file
    if not get_source_file or not pathlib.Path(get_source_file.group(1)).is_file():
        find_source = messagebox.askyesno(
            parent=root,
            title="Missing Source",
            message="Cannot locate source file. Would you like to manually find this?",
        )

        # open prompt to navigate to file
        if find_source:
            source_file_input = filedialog.askopenfilename(
                parent=root,
                title="Select Source File",
                initialdir=s_i_f_initial_dir,
                filetypes=[("Media Files", "*.*")],
            )
            if source_file_input:
                loaded_source_file = source_file_input

        # if user does not want to find the source exit the function
        elif not find_source:
            return  # exit the function

    # if we find the source file
    else:
        loaded_source_file = get_source_file.group(1)

    try:
        media_info = MediaInfo.parse(pathlib.Path(loaded_source_file))
    except UnboundLocalError:
        return  # exit the function

    # check to ensure file dropped has a video track
    if not media_info.general_tracks[0].count_of_video_streams:
        messagebox.showerror(
            parent=root,
            title="Error",
            message="Incorrect file format or missing video stream",
        )
        return  # exit the function

    # set video track
    video_track = media_info.video_tracks[0]

    # set general track
    general_track = media_info.general_tracks[0]

    # calculate average video bitrate
    if video_track.stream_size and video_track.duration:
        calculate_average_video_bitrate = round(
            (float(video_track.stream_size) / 1000)
            / ((float(video_track.duration) / 60000) * 0.0075)
            / 1000
        )

    # if one of the above metrics is missing attempt to calculate it roughly with the general track info
    elif general_track.file_size and general_track.duration:
        calculate_average_video_bitrate = round(
            (float(general_track.file_size) / 1000)
            / ((float(general_track.duration) / 60000) * 0.0075)
            / 1000
            * 0.88
        )

    # if for some reason neither can produce the bitrate
    else:
        calculate_average_video_bitrate = "N/A"

    # get stream size
    if video_track.other_stream_size:
        v_stream_size = video_track.other_stream_size[3]
    # if video track is missing the above metrics get it from general
    elif general_track.other_file_size[3]:
        v_stream_size = general_track.other_file_size[3]
    # if for some reason general and video are missing the metrics just print it as N/A
    else:
        v_stream_size = "N/A"

    # update source labels
    update_source_label = (
        f"Avg BR:  {str(calculate_average_video_bitrate)} kbps  |  "
        f"Res:  {str(video_track.width)}x{str(video_track.height)}  |  "
        f"FPS:  {str(video_track.frame_rate)}  |  "
        f"Size:  {str(v_stream_size)}"
    )
    hdr_string = ""
    if video_track.other_hdr_format:
        hdr_string = f"HDR format:  {str(video_track.hdr_format)} / {str(video_track.hdr_format_compatibility)}"
    elif not video_track.other_hdr_format:
        hdr_string = ""

    # if source has 0 audio streams (this should never happen)
    if not media_info.general_tracks[0].count_of_audio_streams:
        audio_missing = messagebox.askyesno(
            parent=root,
            title="Missing Audio Track",
            message="Source has no audio track\n\nWould you like to manually open an audio file? ",
        )
        # if user presses "No"
        if not audio_missing:
            return  # exit this function

        # if user presses "Yes"
        elif audio_missing:
            manual_audio_input = filedialog.askopenfilename(
                parent=root,
                title="Select Soure Audio File",
                initialdir=s_i_f_initial_dir,
                filetypes=[("Source Audio", "*.*")],
            )
            if not manual_audio_input:
                return  # exit this function

            elif manual_audio_input:
                try:
                    audio_media_info = (
                        MediaInfo.parse(pathlib.Path(manual_audio_input))
                        .audio_tracks[0]
                        .to_data()
                    )
                except IndexError:
                    messagebox.showerror(
                        parent=root,
                        title="Error",
                        message="Opened file has no audio tracks...",
                    )
                    return  # exit function

                # selected source audio track info
                source_file_information.update(
                    {"source_selected_audio_info": audio_media_info, "audio_track": "0"}
                )

    # if source has at least 1 audio stream
    else:
        # if source file only has 2 or more tracks
        if int(media_info.general_tracks[0].count_of_audio_streams) >= 2:
            audio_track_win = Toplevel()  # Toplevel window
            audio_track_win.configure(background=custom_window_bg_color)
            audio_track_win.title("Audio Track Selection")
            # Open on top left of root window
            audio_track_win.geometry(
                f'+{str(int(root.geometry().split("+")[1]) + 108)}+'
                f'{str(int(root.geometry().split("+")[2]) + 80)}'
            )
            # audio_track_win.wm_transient(root)
            audio_track_win.resizable(False, False)  # makes window not resizable
            audio_track_win.grab_set()  # forces audio_track_win to stay on top of root
            audio_track_win.wm_overrideredirect(True)
            root.wm_attributes(
                "-alpha", 0.92
            )  # set main gui to be slightly transparent
            audio_track_win.grid_rowconfigure(0, weight=1)
            audio_track_win.grid_columnconfigure(0, weight=1)

            track_frame = Frame(
                audio_track_win,
                highlightbackground=custom_frame_bg_colors["highlightcolor"],
                highlightthickness=2,
                bg=custom_frame_bg_colors["background"],
                highlightcolor=custom_frame_bg_colors["highlightcolor"],
            )
            track_frame.grid(column=0, row=0, columnspan=3, sticky=N + S + E + W)
            for e_n_f in range(3):
                track_frame.grid_columnconfigure(e_n_f, weight=1)
                track_frame.grid_rowconfigure(e_n_f, weight=1)

            # create label
            track_selection_label = Label(
                track_frame,
                text="Select audio source that down-mix was encoded from:",
                background=custom_label_colors["background"],
                fg=custom_label_colors["foreground"],
                font=(set_font, set_font_size, "bold"),
            )
            track_selection_label.grid(
                row=0, column=0, columnspan=3, sticky=W + N, padx=5, pady=(2, 0)
            )

            # create drop down menu set
            audio_stream_track_counter = {}
            for i in range(int(media_info.general_tracks[0].count_of_audio_streams)):
                audio_stream_track_counter[
                    f"Track #{i + 1}  |  {stream_menu(loaded_source_file)[i]}"
                ] = i

            audio_pop_up_var.set(
                next(iter(audio_stream_track_counter))
            )  # set the default option
            audio_pop_up_menu = OptionMenu(
                track_frame, audio_pop_up_var, *audio_stream_track_counter.keys()
            )
            audio_pop_up_menu.config(
                highlightthickness=1,
                width=48,
                anchor="w",
                activebackground=custom_button_colors["activebackground"],
                activeforeground=custom_button_colors["activeforeground"],
                background=custom_button_colors["background"],
                foreground=custom_button_colors["foreground"],
                font=(set_font, set_font_size),
            )
            audio_pop_up_menu.grid(
                row=1, column=0, columnspan=3, padx=10, pady=6, sticky=N + W + E
            )
            audio_pop_up_menu["menu"].configure(
                activebackground=custom_button_colors["activebackground"],
                activeforeground=custom_button_colors["activeforeground"],
                background=custom_button_colors["background"],
                foreground=custom_button_colors["foreground"],
                font=(set_font, set_font_size),
            )

            # create 'OK' button
            def audio_ok_button_function():
                audio_pop_up_var.set(audio_stream_track_counter[audio_pop_up_var.get()])
                root.wm_attributes("-alpha", 1.0)  # restore transparency
                audio_track_win.destroy()

            audio_track_okay_btn = HoverButton(
                track_frame,
                text="OK",
                command=audio_ok_button_function,
                borderwidth="3",
                width=8,
                foreground=custom_button_colors["foreground"],
                background=custom_button_colors["background"],
                activeforeground=custom_button_colors["activeforeground"],
                activebackground=custom_button_colors["activebackground"],
                disabledforeground=custom_button_colors["disabledforeground"],
            )
            audio_track_okay_btn.grid(
                row=2, column=2, columnspan=1, padx=7, pady=5, sticky=S + E
            )
            audio_track_win.wait_window()

        # if source file only has 1 audio track
        elif int(media_info.general_tracks[0].count_of_audio_streams) == 1:
            audio_pop_up_var.set("0")

        # selected source audio track info
        source_file_information.update(
            {
                "source_selected_audio_info": media_info.audio_tracks[
                    int(audio_pop_up_var.get())
                ].to_data()
            }
        )

        # audio track selection
        source_file_information.update({"audio_track": audio_pop_up_var.get()})

    # set source variables
    source_loaded.set("loaded")  # set string var to loaded

    # update dictionary
    # source input path
    source_file_information.update(
        {"source_path": str(pathlib.Path(loaded_source_file))}
    )

    # resolution
    source_file_information.update(
        {"resolution": f"{str(video_track.width)}x{str(video_track.height)}"}
    )

    # crop
    if get_crop:
        # convert crop for VapourSynth
        if script_mode.get() == "vpy":
            get_left = get_crop.group(1).split(",")[0].strip()
            get_right = get_crop.group(1).split(",")[1].strip()
            get_top = get_crop.group(1).split(",")[2].strip()
            get_bottom = get_crop.group(1).split(",")[3].strip()
        # convert crop for AviSynth
        elif script_mode.get() == "avs":
            get_left = get_crop.group(1).split(",")[0].replace("-", "").strip()
            get_right = get_crop.group(1).split(",")[2].replace("-", "").strip()
            get_top = get_crop.group(1).split(",")[1].replace("-", "").strip()
            get_bottom = get_crop.group(1).split(",")[3].replace("-", "").strip()

        # add converted crop info to dictionary
        source_file_information.update(
            {
                "crop": {
                    "left": get_left,
                    "right": get_right,
                    "top": get_top,
                    "bottom": get_bottom,
                }
            }
        )
    # if crop is None
    if not get_crop:
        source_file_information.update({"crop": "None"})

    # hdr
    if hdr_string != "":
        source_file_information.update({"hdr": "True"})
    else:
        source_file_information.update({"hdr": "False"})

    # video format
    if video_track.format:
        source_file_information.update({"format": f"{str(video_track.format)}"})

    # run function to get filename only
    source_name = edition_title_extractor(str(pathlib.Path(loaded_source_file).name))

    # check for existing source data
    pickle_location = pathlib.Path(
        pathlib.Path(source_file_information["source_path"]).parent
        / pathlib.Path(
            pathlib.Path(source_file_information["source_path"]).name
        ).with_suffix(".dat")
    )

    # if pickle file exists clear source_file_information and get data from source file
    if pickle_location.is_file():
        # prompt the user if they'd like re-use existing data
        use_existing_source_data = messagebox.askyesno(
            parent=root,
            title="Use Existing Data?",
            message="Existing source data detected, would you like to load it?",
        )

        # if user selects "yes"
        if use_existing_source_data:
            # clear source file information
            source_file_information.clear()

            # update source file information with pickle data
            source_file_information.update(get_saved_source_info(pickle_location))

        # if user selects "no
        elif not use_existing_source_data:
            # delete old pickle data
            pathlib.Path(pickle_location).unlink(missing_ok=True)

            # clear source file information
            source_file_information.clear()

            # re-run source input function
            source_input_function(*args)

            # exit this function
            return

    # if pickle file does not exist, collect the data and save to file for use later
    elif not pickle_location.is_file():

        # use imdb to check to double-check detected title
        root.withdraw()  # hide root window
        search_movie_global_function(source_name[1])  # run movie search function
        advanced_root_deiconify()  # re-open root window

        # get edition from source name results
        extracted_edition = ""
        if source_name[0] != "":
            extracted_edition = f" {source_name[0]}"

        # add 'UHD' to filename if it's 2160p
        uhd_string = ""
        if 1920 < int(video_track.width) <= 3840:
            uhd_string = " UHD"

        # add full final name and year to the dictionary
        try:
            if source_file_information["imdb_movie_name"] != "None":
                source_file_information.update(
                    {
                        "source_file_name": f"{source_file_information['imdb_movie_name']}"
                        f"{uhd_string}{extracted_edition} BluRay"
                    }
                )
            # if there was a connection error key 'imdb_movie_name' will be 'None', get title name manually
            elif source_file_information["imdb_movie_name"] == "None":
                source_file_information.update(
                    {
                        "source_file_name": f"{source_name}{uhd_string}"
                        f"{extracted_edition} BluRay"
                    }
                )
        except KeyError:
            return  # exit this function

        # save source_file_information to pickle file for use later
        save_source_info(pickle_location, source_file_information)

    # update labels
    source_label.config(text=update_source_label)
    source_hdr_label.config(text=hdr_string)
    source_file_path.set(str(pathlib.Path(loaded_source_file)))

    source_entry_box.config(state=NORMAL)
    source_entry_box.delete(0, END)
    source_entry_box.insert(END, pathlib.Path(loaded_source_file).name)
    source_entry_box.config(state=DISABLED)

    # return function
    return loaded_source_file


def encode_input_function(*args):
    # define parser
    encode_input_function_parser = ConfigParser()
    encode_input_function_parser.read(config_file)

    # check if source is loaded
    if source_loaded.get() == "":
        messagebox.showinfo(
            parent=root, title="Info", message="You must open a source file first"
        )
        return  # exit function

    # code to check input extension
    if pathlib.Path(*args).suffix != ".mp4":
        messagebox.showerror(
            parent=root,
            title="Incorrect container",
            message=f'Incorrect container/extension "{pathlib.Path(*args).suffix}":\n\n'
            f"BHDStudio encodes are muxed into MP4 containers and should have a "
            f'".mp4" extension',
        )
        delete_encode_entry()
        return  # exit function

    # if file has the correct extension type parse it
    media_info = MediaInfo.parse(pathlib.Path(*args))

    # function to generate generic errors
    def encode_input_error_box(media_info_count, track_type, error_string):
        error_message = (
            f'"{pathlib.Path(*args).stem}":\n\nHas {media_info_count} {track_type} track'
            f"(s)\n\n{error_string}"
        )
        messagebox.showerror(
            parent=root, title="Incorrect Format", message=error_message
        )
        delete_encode_entry()

    # video checks ----------------------------------------------------------------------------------------------------
    # if encode is missing the video track
    if not media_info.general_tracks[0].count_of_video_streams:
        encode_input_error_box(
            "0", "video", "BHDStudio encodes should have 1 video track"
        )
        return  # exit function

    # if encode has more than 1 video track
    if int(media_info.general_tracks[0].count_of_video_streams) > 1:
        encode_input_error_box(
            media_info.general_tracks[0].count_of_video_streams,
            "video",
            "BHDStudio encodes should only have 1 video track",
        )
        return  # exit function

    # select video track for parsing
    video_track = media_info.video_tracks[0]

    # calculate average video bit rate for encode
    # calculate_average_video_bit_rate = round((float(video_track.stream_size) / 1000) /
    #                                          ((float(video_track.duration) / 60000) * 0.0075) / 1000)

    # check for un-even crops
    width_value = int(
        str(source_file_information.get("resolution")).split("x")[0]
    ) - int(video_track.width)
    height_value = int(
        str(source_file_information.get("resolution")).split("x")[1]
    ) - int(video_track.height)
    if (int(width_value) % 2) != 0 or (int(height_value) % 2) != 0:
        messagebox.showerror(
            parent=root,
            title="Crop Error",
            message=f'Resolution: "{str(video_track.width)}x{str(video_track.height)}"\n\n'
            f"BHDStudio encodes should only be cropped in even numbers",
        )
        delete_encode_entry()
        return  # exit function

    # error function for resolution check and miss match bit rates
    def resolution_bit_rate_miss_match_error(res_error_string):
        messagebox.showerror(
            parent=root,
            title="Resolution/Bit rate Miss Match",
            message=res_error_string,
        )
        delete_encode_entry()

    # detect resolution and check miss match bit rates
    try:
        encode_settings_used_bit_rate = int(
            str(video_track.encoding_settings)
            .split("bitrate=")[1]
            .split("/")[0]
            .strip()
        )
    except IndexError:
        messagebox.showerror(
            parent=root,
            title="Error",
            message="File was likely encoded with incorrect settings. As it's missing the 2-pass bitrate string.",
        )
        return  # exit the function

    if video_track.width <= 1280:  # 720p
        encoded_source_resolution = "720p"
        if encode_settings_used_bit_rate != 4000:
            resolution_bit_rate_miss_match_error(
                f"Input bit rate: {str(encode_settings_used_bit_rate)} kbps\n\n"
                f"Bit rate for 720p encodes should be 4000 kbps"
            )
            return  # exit function
    elif video_track.width <= 1920:  # 1080p
        encoded_source_resolution = "1080p"
        if encode_settings_used_bit_rate != 8000:
            resolution_bit_rate_miss_match_error(
                f"Input bit rate: {str(encode_settings_used_bit_rate)} kbps\n\n"
                f"Bit rate for 1080p encodes should be 8000 kbps"
            )
            return  # exit function

    elif video_track.width <= 3840:  # 2160p
        encoded_source_resolution = "2160p"
        if encode_settings_used_bit_rate != 16000:
            resolution_bit_rate_miss_match_error(
                f"Input bit rate: {str(encode_settings_used_bit_rate)} kbps\n\n"
                f"Bit rate for 2160p encodes should be 16000 kbps"
            )
            return  # exit function

    # set encode file resolution string var
    encode_file_resolution.set(encoded_source_resolution)

    # check for source resolution vs encode resolution (do not allow 2160p encode on a 1080p source)
    source_width = str(source_file_information["resolution"]).split("x")[0]
    if int(source_width) <= 1920:  # 1080p
        source_resolution = "1080p"
        allowed_encode_resolutions = ["720p", "1080p"]
    elif int(source_width) <= 3840:  # 2160p
        source_resolution = "2160p"
        allowed_encode_resolutions = ["2160p"]
    if encoded_source_resolution not in allowed_encode_resolutions:
        messagebox.showerror(
            parent=root,
            title="Error",
            message=f"Source resolution {source_resolution}:\n"
            f"Encode resolution {encoded_source_resolution}\n\n"
            f"Allowed encode resolutions based on source:\n"
            f'"{", ".join(allowed_encode_resolutions)}"',
        )
        return  # exit function

    # check for duplicates on BeyondHD --------------------------------------------------------------------------------
    check_for_dupe = dupe_check(
        api_key=encode_input_function_parser["bhd_upload_api"]["key"],
        title=source_file_information["imdb_movie_name"],
        resolution=encoded_source_resolution,
    )

    if check_for_dupe:
        messagebox.showinfo(
            parent=root,
            title="Potential Duplicate",
            message="Detected potential duplicate releases, review these before continuing.",
        )
        dupe_check_window(check_for_dupe)

    # audio checks ----------------------------------------------------------------------------------------------------
    # if encode is missing the audio track
    if not media_info.general_tracks[0].count_of_audio_streams:
        encode_input_error_box(
            "0", "audio", "BHDStudio encodes should have 1 audio track"
        )
        return  # exit function

    # if encode has more than 1 audio track
    if int(media_info.general_tracks[0].count_of_audio_streams) > 1:
        encode_input_error_box(
            media_info.general_tracks[0].count_of_audio_streams,
            "audio",
            "BHDStudio encodes should only have 1 audio track",
        )
        return  # exit function

    # select audio track #1
    audio_track = media_info.audio_tracks[0]

    # check audio track format
    if str(audio_track.format) != "AC-3":
        messagebox.showerror(
            parent=root,
            title="Error",
            message=f'Audio format "{str(audio_track.format)}" '
            f'is not correct.\n\nBHDStudio encodes should be in "Dolby Digital (AC-3)" only',
        )
        return  # exit function

    # check if audio channels was properly encoded from source
    source_audio_channels = int(
        source_file_information["source_selected_audio_info"]["channel_s"]
    )
    # 720p check, define accepted bhd audio channels
    if encoded_source_resolution == "720p":
        if source_audio_channels == 1:
            bhd_accepted_audio_channels = 1
        elif source_audio_channels >= 2:
            bhd_accepted_audio_channels = 2

    # 1080p/2160p check, define accepted bhd audio channels
    elif encoded_source_resolution == "1080p" or encoded_source_resolution == "2160p":
        if source_audio_channels == 1:
            bhd_accepted_audio_channels = 1
        elif source_audio_channels in (2, 3, 4, 5):
            bhd_accepted_audio_channels = 2
        elif source_audio_channels in (6, 7, 8):
            bhd_accepted_audio_channels = 6

    # compare encoded audio channels against BHD accepted audio channels, if they are not the same prompt an error
    if int(audio_track.channel_s) != bhd_accepted_audio_channels:
        # generate cleaner audio strings for source
        if source_audio_channels == 1:
            source_audio_string = "1.0"
        elif source_audio_channels == 2:
            source_audio_string = "2.0"
        elif source_audio_channels == 3:
            source_audio_string = "2.1"
        elif source_audio_channels == 6:
            source_audio_string = "5.1"
        elif source_audio_channels == 7:
            source_audio_string = "6.1"
        elif source_audio_channels == 8:
            source_audio_string = "7.1"
        else:
            source_audio_string = str(source_audio_channels)

        # generate cleaner audio strings for encode
        if bhd_accepted_audio_channels == 1:
            encode_audio_string = "1.0"
        elif bhd_accepted_audio_channels == 2:
            encode_audio_string = "2.0 (dplII)"
        elif bhd_accepted_audio_channels == 6:
            encode_audio_string = "5.1"
        messagebox.showerror(
            parent=root,
            title="Error",
            message=f"Source audio is {source_audio_string}\n\n"
            f"{encoded_source_resolution} BHDStudio audio should be Dolby Digital "
            f"{encode_audio_string}",
        )
        return  # exit function

    # update audio channel string var for use with the uploader
    if bhd_accepted_audio_channels == 1:
        encode_file_audio.set("DD1.0")
    elif bhd_accepted_audio_channels == 2:
        encode_file_audio.set("DD2.0")
    elif bhd_accepted_audio_channels == 6:
        encode_file_audio.set("DD5.1")

    # audio channel string conversion and error check
    if audio_track.channel_s == 1:
        audio_channels_string = "1.0"
    elif audio_track.channel_s == 2:
        audio_channels_string = "2.0"
    elif audio_track.channel_s == 6:
        audio_channels_string = "5.1"
    else:
        messagebox.showerror(
            parent=root,
            title="Incorrect Format",
            message=f"Incorrect audio channel format {str(audio_track.channel_s)}:\n\nBHDStudio "
            f"encodes audio channels should be 1.0, 2.0 (dplII), or 5.1",
        )
        delete_encode_entry()
        return  # exit function

    calculate_average_video_bitrate = round(
        (float(video_track.stream_size) / 1000)
        / ((float(video_track.duration) / 60000) * 0.0075)
        / 1000
    )

    update_source_label = (
        f"Avg BR:  {str(calculate_average_video_bitrate)} kbps  |  "
        f"Res:  {str(video_track.width)}x{str(video_track.height)}  |  "
        f"FPS:  {str(video_track.frame_rate)}  |  "
        f"Audio:  {str(audio_track.format)} / {audio_channels_string} / "
        f"{str(audio_track.other_bit_rate[0]).replace('kb/s', '').strip().replace(' ', '')} kbps"
    )
    hdr_string = ""
    if video_track.other_hdr_format:
        hdr_string = f"HDR format:  {str(video_track.hdr_format)} / {str(video_track.hdr_format_compatibility)}"
        if "hdr10" in hdr_string.lower():
            encode_hdr_string.set("HDR")
    elif not video_track.other_hdr_format:
        hdr_string = ""
        encode_hdr_string.set("")

    release_notes_scrolled.config(state=NORMAL)
    release_notes_scrolled.delete("1.0", END)
    release_notes_scrolled.insert(
        END, "-Optimized for PLEX, emby, Jellyfin, and other streaming platforms"
    )
    if audio_channels_string == "1.0":
        release_notes_scrolled.insert(
            END, "\n-Downmixed Lossless audio track to Dolby Digital 1.0"
        )
    elif audio_channels_string == "2.0":
        release_notes_scrolled.insert(
            END, "\n-Downmixed Lossless audio track to Dolby Pro Logic II 2.0"
        )
    elif audio_channels_string == "5.1":
        release_notes_scrolled.insert(
            END, "\n-Downmixed Lossless audio track to Dolby Digital 5.1"
        )
    if "HDR10+" in str(video_track.hdr_format_compatibility):
        release_notes_scrolled.insert(END, "\n-HDR10+ compatible")
        release_notes_scrolled.insert(END, "\n-Screenshots tone mapped for comparison")
    elif "HDR10" in str(video_track.hdr_format_compatibility):
        release_notes_scrolled.insert(END, "\n-HDR10 compatible")
        release_notes_scrolled.insert(END, "\n-Screenshots tone mapped for comparison")
    release_notes_scrolled.config(state=DISABLED)

    # update release notes automatically
    # clear all check buttons
    enable_clear_all_checkbuttons()

    # create empty list
    script_info_list = []

    # search each line of the opened file in memory
    for each_line in loaded_script_info.get().splitlines():
        # remove any commented lines
        if not each_line.startswith("#"):
            # remove all ending newlines and ignore empty strings
            if each_line.rstrip() != "":
                # append the remaining data to a list to be parsed
                script_info_list.append(each_line.rstrip())

    # parse list to update release notes for vapoursynth scripts
    if script_mode.get() == "vpy":
        # find fill border info
        for info in script_info_list:
            fill_border_info = re.search(r"fillborders\((.+)\)", info, re.IGNORECASE)
            if fill_border_info:
                get_digits = re.findall(r"\d+", fill_border_info.group(1))[:-1]
                check_if_all_zero = any(int(i) != 0 for i in get_digits)
                # if any numbers are not equal to 0 (meaning fill borders was actually used)
                if check_if_all_zero:
                    # set fill borders var to 'on' and run fill border update function
                    fill_borders_var.set("on")
                    update_fill_borders()
                # break from loop
                break

        # check for hard coded subs
        hard_code_subs = re.search(r"textsubmod", str(script_info_list), re.IGNORECASE)
        # if hard code subs are found update forced sub var
        if hard_code_subs:
            forced_subtitles_burned_var.set("on")
            update_forced_var()

        # check for balance borders
        for info in script_info_list:
            balance_border_info = re.search(r"bbmod\((.+)\)", info, re.IGNORECASE)
            if balance_border_info:
                bb_digits = re.findall(r"\d+", balance_border_info.group(1))[:-2]
                bb_all_zero = any(int(i) != 0 for i in bb_digits)
                # if any numbers are not equal to 0 (meaning balance borders was actually used)
                if bb_all_zero:
                    # set balance borders to 'on' and run the update function
                    balance_borders_var.set("on")
                    update_balanced_borders()
                # break from the loop
                break

    # parse list to update release notes for avisynth scripts
    elif script_mode.get() == "avs":
        # find fill border info
        for info in script_info_list:
            fill_border_info = re.search(r"fill.+\(([\s\d,]*)\)", info, re.IGNORECASE)
            if fill_border_info:
                get_digits = re.findall(r"\d+", fill_border_info.group(1))
                check_if_all_zero = any(int(i) != 0 for i in get_digits)
                # if any numbers are not equal to 0 (meaning fill borders was actually used)
                if check_if_all_zero:
                    # set fill borders var to 'on' and run fill border update function
                    fill_borders_var.set("on")
                    update_fill_borders()
                # break from loop
                break

        # check for hard coded subs
        hard_code_subs = re.search(
            r"textsub|vobsub", str(script_info_list), re.IGNORECASE
        )
        # if hard code subs are found update forced sub var
        if hard_code_subs:
            forced_subtitles_burned_var.set("on")
            update_forced_var()

        # check for balance borders
        for info in script_info_list:
            balance_border_info = re.search(
                r"balanceborders\((.+)\)", info, re.IGNORECASE
            )
            if balance_border_info:
                bb_digits = re.findall(r"\d+", balance_border_info.group(1))[:-2]
                bb_all_zero = any(int(i) != 0 for i in bb_digits)
                # if any numbers are not equal to 0 (meaning balance borders was actually used)
                if bb_all_zero:
                    # set balance borders to 'on' and run the update function
                    balance_borders_var.set("on")
                    update_balanced_borders()
                # break from the loop
                break

    # set torrent name
    if encode_input_function_parser["torrent_settings"]["default_path"] != "":
        torrent_file_path.set(
            str(
                pathlib.Path(
                    encode_input_function_parser["torrent_settings"]["default_path"]
                )
                / pathlib.Path(pathlib.Path(*args).name).with_suffix(".torrent")
            )
        )
    else:
        torrent_file_path.set(str(pathlib.Path(*args).with_suffix(".torrent")))

    # set media info memory file
    media_info_original = MediaInfo.parse(
        pathlib.Path(*args), full=False, output=""
    )  # parse identical to mediainfo
    encode_media_info.set(media_info_original)

    # update labels
    encode_label.config(text=update_source_label)
    encode_hdr_label.config(text=hdr_string)
    encode_file_path.set(str(pathlib.Path(*args)))
    encode_entry_box.config(state=NORMAL)
    encode_entry_box.delete(0, END)
    encode_entry_box.insert(END, pathlib.Path(*args).name)
    encode_entry_box.config(state=DISABLED)

    # check for unsupported tagged chapters
    try:
        encode_chapter = media_info.menu_tracks[0].to_data()
    except IndexError:
        messagebox.showerror(
            parent=root,
            title="Error",
            message="Missing chapters. You need to re-mux the file with chapters.",
        )
        return  # exit the function

    if re.search(r"\d+:\d+:\d+\.\d+", list(encode_chapter.values())[-1]):
        messagebox.showerror(
            parent=root,
            title="Error",
            message="Chapters appear to be 'Tagged'.\n\nBHDStudio encodes only support "
            "'Numbered' and 'Named' chapters. You will need to re-create the "
            "chapters via MeGui/StaxRip included chapter creator or download them "
            "from the ChapterDB.\n\nYou can then re-mux the encoded file via "
            "Mp4-Mux-Tool.",
        )
        return  # exit the function

    # ensure encode file is named correctly to BHDStudio standards based off of source file input
    if encode_hdr_string.get() != "":
        enc_dropped_hdr = " HDR"
    else:
        enc_dropped_hdr = ""

    suggested_bhd_filename = (
        f"{source_file_information['source_file_name']} {encoded_source_resolution} "
        f"{str(encode_file_audio.get()).replace('DD', 'DD.')}{enc_dropped_hdr} "
        f"{video_track.encoded_library_name}-BHDStudio"
        f"{str(pathlib.Path(*args).suffix)}".replace(" ", ".")
    )

    source_file_information.update(
        {"suggested_bhd_title": suggested_bhd_filename.replace("DD.", "DD")}
    )

    # remove any special characters from the filename
    suggested_bhd_filename = re.sub(r'[\\/:*?"<>|\s]', ".", suggested_bhd_filename)

    # re-add hyphen that was removed from BHDStudio above
    suggested_bhd_filename = suggested_bhd_filename.replace(".BHDStudio", "-BHDStudio")

    # remove multiple '.'s from file name
    suggested_bhd_filename = re.sub(r"\.{2,}", ".", suggested_bhd_filename)

    # if program has already renamed the file ignore this block of code
    if not encode_file_rename.get():
        if str(pathlib.Path(*args).name) != suggested_bhd_filename:
            # rename encode window
            rename_encode_window = Toplevel()
            rename_encode_window.title("Confirm Filename")
            rename_encode_window.configure(background=custom_window_bg_color)
            rename_encode_window.geometry(
                f'{600}x{460}+{str(int(root.geometry().split("+")[1]) + 60)}+'
                f'{str(int(root.geometry().split("+")[2]) + 230)}'
            )
            rename_encode_window.resizable(False, False)
            rename_encode_window.grab_set()
            rename_encode_window.wm_transient(root)
            rename_encode_window.protocol(
                "WM_DELETE_WINDOW",
                lambda: [
                    rename_encode_window.destroy(),
                    root.wm_attributes("-alpha", 1.0),
                ],
            )
            root.wm_attributes(
                "-alpha", 0.90
            )  # set parent window to be slightly transparent
            rename_encode_window.grid_rowconfigure(0, weight=1)
            rename_encode_window.grid_columnconfigure(0, weight=1)

            # rename encode frame
            rename_enc_frame = Frame(
                rename_encode_window,
                highlightbackground=custom_frame_bg_colors["highlightcolor"],
                highlightthickness=2,
                bg=custom_frame_bg_colors["background"],
                highlightcolor=custom_frame_bg_colors["highlightcolor"],
            )
            rename_enc_frame.grid(column=0, row=0, columnspan=3, sticky=N + S + E + W)
            for col_e_f in range(3):
                rename_enc_frame.grid_columnconfigure(col_e_f, weight=1)
            for row_e_f in range(10):
                rename_enc_frame.grid_rowconfigure(row_e_f, weight=1)

            # create label
            rename_info_lbl = Label(
                rename_enc_frame,
                text=f"Source Name:",
                background=custom_label_colors["background"],
                fg=custom_label_colors["foreground"],
                font=(set_font, set_font_size, "bold"),
            )
            rename_info_lbl.grid(
                row=0, column=0, columnspan=3, sticky=W + S + E, padx=5, pady=(2, 0)
            )

            # create label
            rename_info_lbl1 = Label(
                rename_enc_frame,
                wraplength=590,
                text=str(pathlib.Path(source_file_information["source_path"]).name),
                background=custom_label_colors["background"],
                fg=custom_label_colors["foreground"],
                font=(set_fixed_font, set_font_size),
            )
            rename_info_lbl1.grid(
                row=1, column=0, columnspan=3, sticky=W + N + E, padx=5, pady=(2, 0)
            )

            # create label
            rename_info_lbl2 = Label(
                rename_enc_frame,
                text="Encode Name:",
                background=custom_label_colors["background"],
                fg=custom_label_colors["foreground"],
                font=(set_font, set_font_size, "bold"),
            )
            rename_info_lbl2.grid(
                row=2, column=0, columnspan=3, sticky=W + S + E, padx=5, pady=(2, 0)
            )

            # create label
            rename_info_lbl2 = Label(
                rename_enc_frame,
                wraplength=590,
                text=str(pathlib.Path(*args).name),
                background=custom_label_colors["background"],
                fg=custom_label_colors["foreground"],
                font=(set_fixed_font, set_font_size),
            )
            rename_info_lbl2.grid(
                row=3, column=0, columnspan=3, sticky=W + N + E, padx=5, pady=(2, 0)
            )

            def injection_point(x):
                """find the point to inject dubbed/subbed/imax after movie year"""

                # get year from source input
                if source_file_information["source_movie_year"] != "":
                    search_index = (
                        int(x.rindex(str(source_file_information["source_movie_year"])))
                        + 5
                    )

                    return search_index

            def update_generated_name(chk_btn):
                """determine which check button was pressed and update the title based on the selection"""
                nonlocal custom_entry_box, suggested_bhd_filename, imax_var, subbed_var, dubbed_var

                # if check button is IMAX
                if chk_btn == "imax":
                    if imax_var.get():
                        inject_index = injection_point(suggested_bhd_filename)
                        suggested_bhd_filename = (
                            suggested_bhd_filename[:inject_index]
                            + "IMAX."
                            + suggested_bhd_filename[inject_index:]
                        )

                    elif not imax_var.get():
                        suggested_bhd_filename = suggested_bhd_filename.replace(
                            "IMAX.", ""
                        )

                # if check button is Subbed
                elif chk_btn == "subbed":
                    if subbed_var.get():
                        dubbed_var.set(0)
                        dubbed_check_button.config(state=DISABLED)
                        suggested_bhd_filename = suggested_bhd_filename.replace(
                            "Dubbed.", ""
                        )
                        inject_index = injection_point(suggested_bhd_filename)
                        suggested_bhd_filename = (
                            suggested_bhd_filename[:inject_index]
                            + "Subbed."
                            + suggested_bhd_filename[inject_index:]
                        )

                    elif not subbed_var.get():
                        dubbed_check_button.config(state=NORMAL)
                        suggested_bhd_filename = suggested_bhd_filename.replace(
                            "Subbed.", ""
                        )

                # If check button is Dubbed
                elif chk_btn == "dubbed":
                    if dubbed_var.get():
                        subbed_var.set(0)
                        subbed_check_button.config(state=DISABLED)
                        suggested_bhd_filename = suggested_bhd_filename.replace(
                            "Subbed.", ""
                        )
                        inject_index = injection_point(suggested_bhd_filename)
                        suggested_bhd_filename = (
                            suggested_bhd_filename[:inject_index]
                            + "Dubbed."
                            + suggested_bhd_filename[inject_index:]
                        )

                # if check button is director's cut
                elif chk_btn == "director":
                    if director_var.get():
                        inject_index = injection_point(suggested_bhd_filename)
                        suggested_bhd_filename = (
                            suggested_bhd_filename[:inject_index]
                            + "Director's.Cut."
                            + suggested_bhd_filename[inject_index:]
                        )

                    elif not director_var.get():
                        suggested_bhd_filename = suggested_bhd_filename.replace(
                            "Director's.Cut.", ""
                        )

                # if check button is extended cut
                elif chk_btn == "extended":
                    if extended_var.get():
                        inject_index = injection_point(suggested_bhd_filename)
                        suggested_bhd_filename = (
                            suggested_bhd_filename[:inject_index]
                            + "Extended.Cut."
                            + suggested_bhd_filename[inject_index:]
                        )

                    elif not extended_var.get():
                        suggested_bhd_filename = suggested_bhd_filename.replace(
                            "Extended.Cut.", ""
                        )

                # if check button is theatrical cut
                elif chk_btn == "theatrical":
                    if theatrical_var.get():
                        inject_index = injection_point(suggested_bhd_filename)
                        suggested_bhd_filename = (
                            suggested_bhd_filename[:inject_index]
                            + "Theatrical.Cut."
                            + suggested_bhd_filename[inject_index:]
                        )

                    elif not theatrical_var.get():
                        suggested_bhd_filename = suggested_bhd_filename.replace(
                            "Theatrical.Cut.", ""
                        )

                # if check button is unrated
                elif chk_btn == "unrated":
                    if unrated_var.get():
                        inject_index = injection_point(suggested_bhd_filename)
                        suggested_bhd_filename = (
                            suggested_bhd_filename[:inject_index]
                            + "Unrated."
                            + suggested_bhd_filename[inject_index:]
                        )

                    elif not unrated_var.get():
                        suggested_bhd_filename = suggested_bhd_filename.replace(
                            "Unrated.", ""
                        )

                custom_entry_box.delete(0, END)
                custom_entry_box.insert(END, suggested_bhd_filename)

            # imax check button
            imax_var = IntVar()
            imax_check_button = Checkbutton(
                rename_enc_frame,
                text="IMAX",
                takefocus=False,
                variable=imax_var,
                command=lambda: update_generated_name("imax"),
                onvalue=1,
                offvalue=0,
                background=custom_window_bg_color,
                foreground=custom_button_colors["foreground"],
                activebackground=custom_window_bg_color,
                activeforeground=custom_button_colors["foreground"],
                selectcolor=custom_frame_bg_colors["specialbg"],
                font=(set_font, set_font_size + 1),
            )
            imax_check_button.grid(
                row=4, column=0, padx=5, pady=0, sticky=S + E + W + N
            )
            if "imax" in suggested_bhd_filename.lower():
                imax_var.set(1)

            # subbed check button
            subbed_var = IntVar()
            subbed_check_button = Checkbutton(
                rename_enc_frame,
                text="Subbed",
                takefocus=False,
                variable=subbed_var,
                command=lambda: update_generated_name("subbed"),
                onvalue=1,
                offvalue=0,
                background=custom_window_bg_color,
                foreground=custom_button_colors["foreground"],
                activebackground=custom_window_bg_color,
                activeforeground=custom_button_colors["foreground"],
                selectcolor=custom_frame_bg_colors["specialbg"],
                font=(set_font, set_font_size + 1),
            )
            subbed_check_button.grid(
                row=4, column=1, padx=5, pady=0, sticky=S + E + W + N
            )
            if "subbed" in suggested_bhd_filename.lower():
                subbed_var.set(1)

            # dubbed check button
            dubbed_var = IntVar()
            dubbed_check_button = Checkbutton(
                rename_enc_frame,
                text="Dubbed",
                takefocus=False,
                variable=dubbed_var,
                command=lambda: update_generated_name("dubbed"),
                onvalue=1,
                offvalue=0,
                background=custom_window_bg_color,
                foreground=custom_button_colors["foreground"],
                activebackground=custom_window_bg_color,
                activeforeground=custom_button_colors["foreground"],
                selectcolor=custom_frame_bg_colors["specialbg"],
                font=(set_font, set_font_size + 1),
            )
            dubbed_check_button.grid(
                row=4, column=2, padx=5, pady=0, sticky=S + E + W + N
            )
            if "dubbed" in suggested_bhd_filename.lower():
                dubbed_var.set(1)

            # director's cut check button
            director_var = IntVar()
            director_check_button = Checkbutton(
                rename_enc_frame,
                text="Director's Cut",
                takefocus=False,
                variable=director_var,
                command=lambda: update_generated_name("director"),
                onvalue=1,
                offvalue=0,
                background=custom_window_bg_color,
                foreground=custom_button_colors["foreground"],
                activebackground=custom_window_bg_color,
                activeforeground=custom_button_colors["foreground"],
                selectcolor=custom_frame_bg_colors["specialbg"],
                font=(set_font, set_font_size + 1),
            )
            director_check_button.grid(
                row=5, column=0, padx=5, pady=0, sticky=S + E + W + N
            )
            if "director" in suggested_bhd_filename.lower():
                director_var.set(1)

            # extended cut check button
            extended_var = IntVar()
            extended_check_button = Checkbutton(
                rename_enc_frame,
                text="Extended Cut",
                takefocus=False,
                variable=extended_var,
                command=lambda: update_generated_name("extended"),
                onvalue=1,
                offvalue=0,
                background=custom_window_bg_color,
                foreground=custom_button_colors["foreground"],
                activebackground=custom_window_bg_color,
                activeforeground=custom_button_colors["foreground"],
                selectcolor=custom_frame_bg_colors["specialbg"],
                font=(set_font, set_font_size + 1),
            )
            extended_check_button.grid(
                row=5, column=1, padx=5, pady=0, sticky=S + E + W + N
            )
            if "extended" in suggested_bhd_filename.lower():
                extended_var.set(1)

            # theatrical cut check button
            theatrical_var = IntVar()
            theatrical_check_button = Checkbutton(
                rename_enc_frame,
                text="Theatrical Cut",
                takefocus=False,
                variable=theatrical_var,
                command=lambda: update_generated_name("theatrical"),
                onvalue=1,
                offvalue=0,
                background=custom_window_bg_color,
                foreground=custom_button_colors["foreground"],
                activebackground=custom_window_bg_color,
                activeforeground=custom_button_colors["foreground"],
                selectcolor=custom_frame_bg_colors["specialbg"],
                font=(set_font, set_font_size + 1),
            )
            theatrical_check_button.grid(
                row=5, column=2, padx=5, pady=0, sticky=S + E + W + N
            )
            if "theatrical" in suggested_bhd_filename.lower():
                theatrical_var.set(1)

            # unrated check button
            unrated_var = IntVar()
            unrated_check_button = Checkbutton(
                rename_enc_frame,
                text="Unrated",
                takefocus=False,
                variable=unrated_var,
                command=lambda: update_generated_name("unrated"),
                onvalue=1,
                offvalue=0,
                background=custom_window_bg_color,
                foreground=custom_button_colors["foreground"],
                activebackground=custom_window_bg_color,
                activeforeground=custom_button_colors["foreground"],
                selectcolor=custom_frame_bg_colors["specialbg"],
                font=(set_font, set_font_size + 1),
            )
            unrated_check_button.grid(
                row=6, column=0, padx=5, pady=0, sticky=S + E + W + N
            )
            if "unrated" in suggested_bhd_filename.lower():
                unrated_var.set(1)

            # create label
            rename_info_lbl3 = Label(
                rename_enc_frame,
                text="Suggested Name:",
                background=custom_label_colors["background"],
                fg=custom_label_colors["foreground"],
                font=(set_font, set_font_size, "bold"),
            )
            rename_info_lbl3.grid(row=7, column=0, sticky=W + S, padx=5, pady=(2, 0))

            # create entry box
            custom_entry_box = Entry(
                rename_enc_frame,
                borderwidth=4,
                fg=custom_entry_colors["foreground"],
                bg=custom_entry_colors["background"],
                font=(set_fixed_font, set_font_size),
            )
            custom_entry_box.grid(
                row=8, column=0, columnspan=3, padx=10, pady=(0, 5), sticky=E + W + N
            )
            custom_entry_box.insert(END, str(suggested_bhd_filename))

            def rename_file_func():
                """Rename encode input to the correct name"""
                if not custom_entry_box.get().strip().endswith(".mp4"):
                    messagebox.showerror(
                        parent=rename_encode_window,
                        title="Missing Suffix",
                        message='Filename must have ".mp4" suffix!\n\ne.g. "MovieName.mp4"',
                    )
                    return  # exit function

                # rename the file
                try:
                    renamed_enc = pathlib.Path(*args).rename(
                        pathlib.Path(*args).parent / custom_entry_box.get().strip()
                    )
                # if file exists delete old file and rename
                except FileExistsError:
                    pathlib.Path(
                        pathlib.Path(*args).parent / custom_entry_box.get().strip()
                    ).unlink(missing_ok=True)
                    renamed_enc = pathlib.Path(*args).rename(
                        pathlib.Path(*args).parent / custom_entry_box.get().strip()
                    )

                root.wm_attributes("-alpha", 1.0)  # restore transparency
                rename_encode_window.destroy()  # close window
                encode_file_path.set(str(renamed_enc))  # update global variable
                # bypass rename function on next loop
                encode_file_rename.set(True)
                # re-run encode input with the renamed file
                encode_input_function(pathlib.Path(renamed_enc))

            # create 'Rename' button
            rename_okay_btn = HoverButton(
                rename_enc_frame,
                text="Rename",
                command=rename_file_func,
                borderwidth="3",
                width=8,
                foreground=custom_button_colors["foreground"],
                background=custom_button_colors["background"],
                activeforeground=custom_button_colors["activeforeground"],
                activebackground=custom_button_colors["activebackground"],
                disabledforeground=custom_button_colors["disabledforeground"],
            )
            rename_okay_btn.grid(
                row=9, column=2, columnspan=1, padx=7, pady=5, sticky=S + E
            )

            # create 'Cancel' button
            rename_cancel_btn = HoverButton(
                rename_enc_frame,
                text="Cancel",
                width=8,
                command=lambda: [
                    rename_encode_window.destroy(),
                    root.wm_attributes("-alpha", 1.0),
                ],
                borderwidth="3",
                foreground=custom_button_colors["foreground"],
                background=custom_button_colors["background"],
                activeforeground=custom_button_colors["activeforeground"],
                activebackground=custom_button_colors["activebackground"],
                disabledforeground=custom_button_colors["disabledforeground"],
            )
            rename_cancel_btn.grid(
                row=9, column=0, columnspan=1, padx=7, pady=5, sticky=S + W
            )

            rename_encode_window.wait_window()  # wait for window to be closed


def drop_function(event):
    file_input = [x for x in root.splitlist(event.data)][0]

    # directory is dropped run the staxrip function
    if pathlib.Path(file_input).is_dir():
        staxrip_working_directory(file_input)

    # if a file is dropped run the manual function
    elif pathlib.Path(file_input).is_file():
        widget_source = str(event.widget.cget("text")).strip()
        # if widget is in source frame run source input function
        if "source" in widget_source.lower():
            source_input_function(file_input)
        # if the widget is in encode frame run encode input function
        elif "encode" in widget_source.lower():
            encode_file_rename.set(False)
            encode_input_function(file_input)


# source --------------------------------------------------------------------------------------------------------------
source_frame = LabelFrame(
    root,
    text=" Source (*.avs / *.vpy / StaxRip Temp Directory) ",
    labelanchor="nw",
    bd=3,
    font=(set_font, set_font_size + 1, "bold"),
    fg=custom_label_frame_colors["foreground"],
    bg=custom_label_frame_colors["background"],
)
source_frame.grid(column=0, row=0, columnspan=4, padx=5, pady=(5, 3), sticky=E + W)

source_frame.grid_rowconfigure(0, weight=1)
source_frame.grid_rowconfigure(1, weight=1)
source_frame.grid_columnconfigure(0, weight=10)
source_frame.grid_columnconfigure(1, weight=100)
source_frame.grid_columnconfigure(2, weight=0)
# Hover tip tool-tip
CustomTooltipLabel(
    anchor_widget=source_frame,
    hover_delay=400,
    background=custom_window_bg_color,
    foreground=custom_label_frame_colors["foreground"],
    font=(set_fixed_font, set_font_size, "bold"),
    text="Select Open\nor\nDrag and Drop either the StaxRip Temp Dir or the *.avs/*.vpy script",
)
source_frame.drop_target_register(DND_FILES)
source_frame.dnd_bind("<<Drop>>", drop_function)


def manual_source_input():
    # define parser
    manual_source_parser = ConfigParser()
    manual_source_parser.read(config_file)

    # check if last used folder exists
    if pathlib.Path(manual_source_parser["last_used_folder"]["path"]).is_dir():
        manual_initial_dir = pathlib.Path(
            manual_source_parser["last_used_folder"]["path"]
        )
    else:
        manual_initial_dir = "/"

    # get source file input
    source_file_input = filedialog.askopenfilename(
        parent=root,
        title="Select Source Script " '(script file without suffix "_source")',
        initialdir=manual_initial_dir,
        filetypes=[("AviSynth, Vapoursynth", "*.avs *.vpy")],
    )
    if source_file_input:
        source_input_function(source_file_input)


# multiple source input button and pop up menu
def source_input_popup_menu(*args):  # Menu for input button
    source_input_menu = Menu(
        root,
        tearoff=False,
        font=(set_font, set_font_size + 1),
        background=custom_button_colors["background"],
        foreground=custom_button_colors["foreground"],
        activebackground=custom_button_colors["activebackground"],
        activeforeground=custom_button_colors["activeforeground"],
    )  # menu
    source_input_menu.add_command(label="Open Script", command=manual_source_input)
    source_input_menu.add_separator()
    source_input_menu.add_command(
        label="Open StaxRip Temp Dir", command=staxrip_manual_open
    )
    source_input_menu.tk_popup(
        source_button.winfo_rootx(), source_button.winfo_rooty() + 5
    )


# source button
source_button = HoverButton(
    source_frame,
    text="Open",
    command=source_input_popup_menu,
    borderwidth="3",
    foreground=custom_button_colors["foreground"],
    background=custom_button_colors["background"],
    activeforeground=custom_button_colors["activeforeground"],
    activebackground=custom_button_colors["activebackground"],
    disabledforeground=custom_button_colors["disabledforeground"],
)
source_button.grid(
    row=0, column=0, columnspan=1, padx=5, pady=(5, 0), sticky=N + S + E + W
)

# source entry box
source_entry_box = Entry(
    source_frame,
    borderwidth=4,
    state=DISABLED,
    fg=custom_entry_colors["foreground"],
    bg=custom_entry_colors["background"],
    disabledforeground=custom_entry_colors["disabledforeground"],
    disabledbackground=custom_entry_colors["disabledbackground"],
    font=(set_fixed_font, set_font_size),
)
source_entry_box.grid(
    row=0, column=1, columnspan=2, padx=5, pady=(7, 0), sticky=E + W + N
)

# source info frame
source_info_frame = LabelFrame(
    source_frame,
    text="Info:",
    bd=0,
    font=(set_font, set_font_size),
    fg=custom_label_frame_colors["foreground"],
    bg=custom_label_frame_colors["background"],
)
source_info_frame.grid(
    row=1, column=0, columnspan=4, padx=5, pady=0, sticky=N + S + E + W
)
for s_i_f in range(4):
    source_info_frame.grid_columnconfigure(s_i_f, weight=1)
source_info_frame.grid_rowconfigure(0, weight=1)
source_info_frame.grid_rowconfigure(1, weight=1)

# source labels
source_label = Label(
    source_info_frame,
    text=" " * 100,
    bd=0,
    relief=SUNKEN,
    background=custom_label_colors["background"],
    fg=custom_label_colors["foreground"],
    font=(set_font, set_font_size - 2),
)
source_label.grid(column=0, row=0, columnspan=4, pady=3, padx=3, sticky=W)
source_hdr_label = Label(
    source_info_frame,
    text=" " * 100,
    bd=0,
    relief=SUNKEN,
    background=custom_label_colors["background"],
    fg=custom_label_colors["foreground"],
    font=(set_font, set_font_size - 2),
)
source_hdr_label.grid(column=0, row=1, columnspan=4, pady=3, padx=3, sticky=W)


# function to delete source entry
def delete_source_entry():
    source_entry_box.config(state=NORMAL)
    source_entry_box.delete(0, END)
    source_entry_box.config(state=DISABLED)
    source_label.config(text=" " * 100)
    source_hdr_label.config(text=" " * 100)
    source_file_path.set("")
    source_loaded.set("")
    delete_encode_entry()


reset_source_input = HoverButton(
    source_frame,
    text="X",
    command=delete_source_entry,
    borderwidth="3",
    width=3,
    foreground=custom_button_colors["foreground"],
    background=custom_button_colors["background"],
    activeforeground=custom_button_colors["activeforeground"],
    activebackground=custom_button_colors["activebackground"],
    disabledforeground=custom_button_colors["disabledforeground"],
)
reset_source_input.grid(
    row=0, column=3, columnspan=1, padx=5, pady=(5, 0), sticky=N + E + W
)

# encode --------------------------------------------------------------------------------------------------------------
encode_frame = LabelFrame(
    root,
    text=" Encode (*.mp4) ",
    labelanchor="nw",
    bd=3,
    font=(set_font, set_font_size + 1, "bold"),
    fg=custom_label_frame_colors["foreground"],
    bg=custom_label_frame_colors["background"],
)
encode_frame.grid(column=0, row=1, columnspan=4, padx=5, pady=(5, 3), sticky=E + W)

encode_frame.grid_rowconfigure(0, weight=1)
encode_frame.grid_rowconfigure(1, weight=1)
encode_frame.grid_columnconfigure(0, weight=10)
encode_frame.grid_columnconfigure(1, weight=100)
encode_frame.grid_columnconfigure(3, weight=0)

encode_frame.drop_target_register(DND_FILES)
encode_frame.dnd_bind("<<Drop>>", drop_function)


def manual_encode_input():
    # define parser
    manual_encode_parser = ConfigParser()
    manual_encode_parser.read(config_file)

    # check if last used folder exists
    if pathlib.Path(manual_encode_parser["last_used_folder"]["path"]).is_dir():
        manual_initial_enc_dir = pathlib.Path(
            manual_encode_parser["last_used_folder"]["path"]
        )
    else:
        manual_initial_enc_dir = "/"

    # get encode input
    encode_file_input = filedialog.askopenfilename(
        parent=root,
        title="Select Encode",
        initialdir=manual_initial_enc_dir,
        filetypes=[("Media Files", "*.*")],
    )
    if encode_file_input:
        encode_file_rename.set(False)
        encode_input_function(encode_file_input)


encode_button = HoverButton(
    encode_frame,
    text="Open",
    command=manual_encode_input,
    borderwidth="3",
    foreground=custom_button_colors["foreground"],
    background=custom_button_colors["background"],
    activeforeground=custom_button_colors["activeforeground"],
    activebackground=custom_button_colors["activebackground"],
    disabledforeground=custom_button_colors["disabledforeground"],
)
encode_button.grid(row=0, column=0, columnspan=1, padx=5, pady=(5, 0), sticky=N + E + W)

encode_entry_box = Entry(
    encode_frame,
    borderwidth=4,
    state=DISABLED,
    fg=custom_entry_colors["foreground"],
    bg=custom_entry_colors["background"],
    disabledforeground=custom_entry_colors["disabledforeground"],
    disabledbackground=custom_entry_colors["disabledbackground"],
    font=(set_fixed_font, set_font_size),
)
encode_entry_box.grid(
    row=0, column=1, columnspan=2, padx=5, pady=(7, 0), sticky=E + W + N
)

encode_info_frame = LabelFrame(
    encode_frame,
    text="Info:",
    bd=0,
    font=(set_font, set_font_size),
    fg=custom_label_frame_colors["foreground"],
    bg=custom_label_frame_colors["background"],
)
encode_info_frame.grid(
    row=1, column=0, columnspan=4, padx=5, pady=0, sticky=N + S + E + W
)
for s_i_f in range(4):
    encode_info_frame.grid_columnconfigure(s_i_f, weight=1)
encode_info_frame.grid_rowconfigure(0, weight=1)
encode_info_frame.grid_rowconfigure(1, weight=1)

encode_label = Label(
    encode_info_frame,
    text=" " * 100,
    bd=0,
    relief=SUNKEN,
    background=custom_label_colors["background"],
    fg=custom_label_colors["foreground"],
    font=(set_font, set_font_size - 2),
)
encode_label.grid(column=0, row=0, columnspan=1, pady=3, padx=3, sticky=W)
encode_hdr_label = Label(
    encode_info_frame,
    text=" " * 100,
    bd=0,
    relief=SUNKEN,
    background=custom_label_colors["background"],
    fg=custom_label_colors["foreground"],
    font=(set_font, set_font_size - 2),
)
encode_hdr_label.grid(column=0, row=1, columnspan=1, pady=3, padx=3, sticky=W)


def delete_encode_entry():
    encode_entry_box.config(state=NORMAL)
    encode_entry_box.delete(0, END)
    encode_entry_box.config(state=DISABLED)
    encode_label.config(text=" " * 100)
    encode_hdr_label.config(text=" " * 100)
    release_notes_scrolled.config(state=NORMAL)
    release_notes_scrolled.delete("1.0", END)
    release_notes_scrolled.config(state=DISABLED)
    disable_clear_all_checkbuttons()
    torrent_file_path.set("")
    open_torrent_window_button.config(state=DISABLED)
    generate_nfo_button.config(state=DISABLED)
    encode_file_path.set("")
    encode_file_resolution.set("")
    encode_media_info.set("")
    encode_file_audio.set("")
    encode_hdr_string.set("")


reset_encode_input = HoverButton(
    encode_frame,
    text="X",
    command=delete_encode_entry,
    borderwidth="3",
    width=3,
    foreground=custom_button_colors["foreground"],
    background=custom_button_colors["background"],
    activeforeground=custom_button_colors["activeforeground"],
    activebackground=custom_button_colors["activebackground"],
    disabledforeground=custom_button_colors["disabledforeground"],
)
reset_encode_input.grid(
    row=0, column=3, columnspan=1, padx=5, pady=(5, 0), sticky=N + E + W
)


# staxrip directory ---------------------------------------------------------------------------------------------------
def staxrip_working_directory(stax_dir_path):
    # get source and encode paths
    def get_source_and_encode_paths(log_path):
        # open log path file
        with open(pathlib.Path(log_path), "rt") as source_log:
            # load logfile into memory
            log_file_loaded = source_log.read()
            # check for script type
            if "- AviSynth Script -" in log_file_loaded:
                # get source path
                get_source_path = pathlib.Path(log_path.replace("_staxrip.log", ".avs"))
            elif "- VapourSynth Script -" in log_file_loaded:
                # get source path
                get_source_path = pathlib.Path(log_path.replace("_staxrip.log", ".vpy"))

                # if AviSynth or VapourSynth is not inside the log file
            else:
                messagebox.showerror(
                    parent=root,
                    title="Error",
                    message="Working directory does not contain the correct information needed."
                    "\n\nYou will need to manually input the source (encode.avs/vpy) script",
                )
                # restore transparency
                root.wm_attributes("-alpha", 1.0)
                # exit the function
                return

            # find encode file output path
            get_encode_path = re.search(r"Saving\s(.+\.mp4):", log_file_loaded)

        # if both paths are located load them into the program
        if get_source_path and get_encode_path:
            # restore transparency
            root.wm_attributes("-alpha", 1.0)
            # run source input function
            if pathlib.Path(get_source_path).is_file():
                run_source_func = source_input_function(get_source_path)
            else:
                messagebox.showinfo(
                    title="Info",
                    message="Could not load source script, please input this manually",
                )

            # if user cancels source_input_function code exit this function as well
            if not run_source_func:
                return  # exit this function

            try:
                if pathlib.Path(get_encode_path.group(1)).is_file():
                    encode_input_function(get_encode_path.group(1))
                else:
                    messagebox.showinfo(
                        title="Info",
                        message='Could not load encode "*BHDStudio.mp4", please input '
                        "this manually",
                    )
            except OSError:
                messagebox.showinfo(
                    title="Info",
                    message='Could not load encode "*BHDStudio.mp4", please input '
                    "this manually",
                )

        # if both paths are not located
        else:
            messagebox.showerror(
                title="Error",
                message="Could not locate source and/or encode path.\n\nLoad these manually.",
            )
            # restore transparency
            root.wm_attributes("-alpha", 1.0)
            return  # exit function

    # create empty dictionary
    dict_of_stax_logs = {}

    # check for log files with filters
    for log_file in pathlib.Path(stax_dir_path).glob("*.log"):
        if "720p" in log_file.name.lower() and "bhdstudio" in log_file.name.lower():
            dict_of_stax_logs.update(
                {str(pathlib.Path(log_file).name): str(pathlib.Path(log_file))}
            )
        if "1080p" in log_file.name.lower() and "bhdstudio" in log_file.name.lower():
            dict_of_stax_logs.update(
                {str(pathlib.Path(log_file).name): str(pathlib.Path(log_file))}
            )
        if "2160p" in log_file.name.lower() and "bhdstudio" in log_file.name.lower():
            dict_of_stax_logs.update(
                {str(pathlib.Path(log_file).name): str(pathlib.Path(log_file))}
            )

    # if "bhd" log files was not found remove filters and search again
    if not dict_of_stax_logs:
        for log_file in pathlib.Path(stax_dir_path).glob("*.log"):
            dict_of_stax_logs.update(
                {str(pathlib.Path(log_file).name): str(pathlib.Path(log_file))}
            )

    # check if any logs exist now...
    # if logs are not found
    if not dict_of_stax_logs:
        messagebox.showinfo(
            parent=root,
            title="Info",
            message="Unable to find any log files. Please manually "
            "open source and encode files.",
        )
        # restore transparency
        root.wm_attributes("-alpha", 1.0)
        return  # exit this function

    # if logs are found
    elif dict_of_stax_logs:
        # if there is more than 1 log file
        if len(dict_of_stax_logs) >= 2:
            stax_log_win = Toplevel()
            stax_log_win.configure(background=custom_window_bg_color)
            stax_log_win.title("Log Files")
            # Open on top left of root window
            stax_log_win.geometry(
                f'{480}x{160}+{str(int(root.geometry().split("+")[1]) + 108)}+'
                f'{str(int(root.geometry().split("+")[2]) + 80)}'
            )
            stax_log_win.resizable(False, False)  # makes window not resizable
            stax_log_win.grab_set()  # forces stax_log_win to stay on top of root
            stax_log_win.wm_overrideredirect(True)
            root.wm_attributes(
                "-alpha", 0.92
            )  # set main gui to be slightly transparent
            stax_log_win.grid_rowconfigure(0, weight=1)
            stax_log_win.grid_columnconfigure(0, weight=1)

            stax_frame = Frame(
                stax_log_win,
                highlightbackground=custom_frame_bg_colors["highlightcolor"],
                highlightthickness=2,
                bg=custom_frame_bg_colors["background"],
                highlightcolor=custom_frame_bg_colors["highlightcolor"],
            )
            stax_frame.grid(column=0, row=0, columnspan=3, sticky=N + S + E + W)
            for e_n_f in range(3):
                stax_frame.grid_columnconfigure(e_n_f, weight=1)
                stax_frame.grid_rowconfigure(e_n_f, weight=1)

            # create label
            stax_info_label = Label(
                stax_frame,
                text="Select logfile to parse information from:",
                background=custom_label_colors["background"],
                fg=custom_label_colors["foreground"],
                font=(set_font, set_font_size, "bold"),
            )
            stax_info_label.grid(
                row=0, column=0, columnspan=3, sticky=W + N, padx=5, pady=(2, 0)
            )

            # create menu
            log_pop_up_var = StringVar()
            log_pop_up_var.set(next(iter(reversed(dict_of_stax_logs))))
            log_pop_up_menu = OptionMenu(
                stax_frame, log_pop_up_var, *reversed(dict_of_stax_logs.keys())
            )
            log_pop_up_menu.config(
                highlightthickness=1,
                width=48,
                anchor="w",
                activebackground=custom_button_colors["activebackground"],
                activeforeground=custom_button_colors["activeforeground"],
                background=custom_button_colors["background"],
                foreground=custom_button_colors["foreground"],
            )
            log_pop_up_menu.grid(
                row=1, column=0, columnspan=3, padx=10, pady=6, sticky=N + W + E
            )
            log_pop_up_menu["menu"].configure(
                activebackground=custom_button_colors["activebackground"],
                activeforeground=custom_button_colors["activeforeground"],
                background=custom_button_colors["background"],
                foreground=custom_button_colors["foreground"],
            )

            # create 'OK' button
            def stax_ok_function():
                # close stax_log_window
                stax_log_win.destroy()
                # run function to parse log file
                get_source_and_encode_paths(dict_of_stax_logs[log_pop_up_var.get()])

            stax_okay_btn = HoverButton(
                stax_frame,
                text="OK",
                command=stax_ok_function,
                borderwidth="3",
                width=8,
                foreground=custom_button_colors["foreground"],
                background=custom_button_colors["background"],
                activeforeground=custom_button_colors["activeforeground"],
                activebackground=custom_button_colors["activebackground"],
                disabledforeground=custom_button_colors["disabledforeground"],
            )
            stax_okay_btn.grid(
                row=2, column=2, columnspan=1, padx=7, pady=5, sticky=S + E
            )

            # create 'Cancel' button
            def stax_cancel_function():
                # restore transparency
                root.wm_attributes("-alpha", 1.0)
                # close window
                stax_log_win.destroy()
                # reset main gui
                reset_gui()

            stax_cancel_btn = HoverButton(
                stax_frame,
                text="Cancel",
                command=stax_cancel_function,
                borderwidth="3",
                width=8,
                foreground=custom_button_colors["foreground"],
                background=custom_button_colors["background"],
                activeforeground=custom_button_colors["activeforeground"],
                activebackground=custom_button_colors["activebackground"],
                disabledforeground=custom_button_colors["disabledforeground"],
            )
            stax_cancel_btn.grid(
                row=2, column=0, columnspan=1, padx=7, pady=5, sticky=S + W
            )

            # wait for the window to be closed to do anything else
            stax_log_win.wait_window()

        # if there is only 1 log file
        else:
            # get the only value in the dictionary
            get_source_and_encode_paths(next(iter(dict_of_stax_logs.values())))


# staxrip manual open
def staxrip_manual_open():
    # open filedialog
    parse_stax_temp_dir = filedialog.askdirectory(
        parent=root, title="StaxRip Working Directory"
    )

    if parse_stax_temp_dir:
        staxrip_working_directory(parse_stax_temp_dir)


# release notes -------------------------------------------------------------------------------------------------------
release_notes_frame = LabelFrame(
    root,
    text=" Release Notes ",
    labelanchor="nw",
    bd=3,
    font=(set_font, set_font_size + 1, "bold"),
    fg=custom_label_frame_colors["foreground"],
    bg=custom_label_frame_colors["background"],
)
release_notes_frame.grid(
    column=0, row=2, columnspan=4, padx=5, pady=(5, 3), sticky=E + W
)

for rl_row in range(3):
    release_notes_frame.grid_rowconfigure(rl_row, weight=1)
for rl_f in range(3):
    release_notes_frame.grid_columnconfigure(rl_f, weight=1)


def update_forced_var():
    release_notes_scrolled.config(state=NORMAL)
    if forced_subtitles_burned_var.get() == "on":
        release_notes_scrolled.insert(
            END, "\n-Forced English subtitles embedded for non English dialogue"
        )
    elif forced_subtitles_burned_var.get() == "off":
        delete_forced = release_notes_scrolled.search(
            "-Forced English subtitles embedded for non English dialogue", "1.0", END
        )
        if delete_forced != "":
            release_notes_scrolled.delete(
                str(delete_forced), str(float(delete_forced) + 1.0)
            )
    release_notes_scrolled.config(state=DISABLED)


forced_subtitles_burned_var = StringVar()
forced_subtitles_burned = Checkbutton(
    release_notes_frame,
    text="Forced Subtitles",
    variable=forced_subtitles_burned_var,
    takefocus=False,
    onvalue="on",
    offvalue="off",
    command=update_forced_var,
    background=custom_window_bg_color,
    foreground=custom_button_colors["foreground"],
    activebackground=custom_window_bg_color,
    activeforeground=custom_button_colors["foreground"],
    selectcolor=custom_frame_bg_colors["specialbg"],
    font=(set_font, set_font_size + 1),
    state=DISABLED,
)
forced_subtitles_burned.grid(
    row=0, column=0, columnspan=1, rowspan=1, padx=5, pady=0, sticky=S + E + W + N
)
forced_subtitles_burned_var.set("off")


def update_balanced_borders():
    release_notes_scrolled.config(state=NORMAL)
    if balance_borders_var.get() == "on":
        release_notes_scrolled.insert(END, "\n-Cleaned dirty edges with BalanceBorders")
    elif balance_borders_var.get() == "off":
        delete_balanced_borders = release_notes_scrolled.search(
            "-Cleaned dirty edges with BalanceBorders", "1.0", END
        )
        if delete_balanced_borders != "":
            release_notes_scrolled.delete(
                str(delete_balanced_borders), str(float(delete_balanced_borders) + 1.0)
            )
    release_notes_scrolled.config(state=DISABLED)


balance_borders_var = StringVar()
balance_borders = Checkbutton(
    release_notes_frame,
    text="Balance Borders",
    variable=balance_borders_var,
    takefocus=False,
    onvalue="on",
    offvalue="off",
    command=update_balanced_borders,
    background=custom_window_bg_color,
    foreground=custom_button_colors["foreground"],
    activebackground=custom_window_bg_color,
    activeforeground=custom_button_colors["foreground"],
    selectcolor=custom_frame_bg_colors["specialbg"],
    font=(set_font, set_font_size + 1),
    state=DISABLED,
)
balance_borders.grid(
    row=0, column=1, columnspan=1, rowspan=1, padx=5, pady=0, sticky=S + E + W + N
)
balance_borders_var.set("off")


def update_fill_borders():
    release_notes_scrolled.config(state=NORMAL)
    if fill_borders_var.get() == "on":
        release_notes_scrolled.insert(END, "\n-Fill borders with FillBorders")
    elif fill_borders_var.get() == "off":
        delete_fill_borders = release_notes_scrolled.search(
            "-Fill borders with FillBorders", "1.0", END
        )
        if delete_fill_borders != "":
            release_notes_scrolled.delete(
                str(delete_fill_borders), str(float(delete_fill_borders) + 1.0)
            )
    release_notes_scrolled.config(state=DISABLED)


fill_borders_var = StringVar()
fill_borders = Checkbutton(
    release_notes_frame,
    text="Fill Borders",
    variable=fill_borders_var,
    takefocus=False,
    onvalue="on",
    offvalue="off",
    command=update_fill_borders,
    background=custom_window_bg_color,
    foreground=custom_button_colors["foreground"],
    activebackground=custom_window_bg_color,
    activeforeground=custom_button_colors["foreground"],
    selectcolor=custom_frame_bg_colors["specialbg"],
    font=(set_font, set_font_size + 1),
    state=DISABLED,
)
fill_borders.grid(
    row=0, column=2, columnspan=1, rowspan=1, padx=5, pady=0, sticky=S + E + W + N
)
fill_borders_var.set("off")

release_notes_scrolled = scrolledtextwidget.ScrolledText(
    release_notes_frame,
    height=5,
    bd=4,
    bg=custom_scrolled_text_widget_color["background"],
    fg=custom_scrolled_text_widget_color["foreground"],
    state=DISABLED,
    font=(set_fixed_font, set_font_size),
)
release_notes_scrolled.grid(
    row=1, column=0, columnspan=4, pady=(0, 2), padx=5, sticky=E + W
)

# Hover tip tool-tip
CustomTooltipLabel(
    anchor_widget=release_notes_scrolled,
    hover_delay=400,
    background=custom_window_bg_color,
    foreground=custom_label_frame_colors["foreground"],
    font=(set_fixed_font, set_font_size, "bold"),
    text="Right click for more options",
)


# right click menu for screenshot box
def popup_auto_e_b_menu(e):  # Function for mouse button 3 (right click) to pop up menu
    enable_edits_menu.tk_popup(e.x_root, e.y_root)  # This gets the position of 'e'


# pop up menu to enable/disable manual edits in release notes
enable_edits_menu = Menu(
    release_notes_scrolled,
    tearoff=False,
    font=(set_font, set_font_size + 1),
    background=custom_button_colors["background"],
    foreground=custom_button_colors["foreground"],
    activebackground=custom_button_colors["activebackground"],
    activeforeground=custom_button_colors["activeforeground"],
)  # Right click menu
enable_edits_menu.add_command(
    label="Enable Manual Edits",
    command=lambda: release_notes_scrolled.config(state=NORMAL),
)
enable_edits_menu.add_command(
    label="Disable Manual Edits",
    command=lambda: release_notes_scrolled.config(state=DISABLED),
)
enable_edits_menu.add_separator()
enable_edits_menu.add_command(
    label="Open Script In Default Viewer",
    command=lambda: open_script_in_viewer(pathlib.Path(input_script_path.get())),
)
release_notes_scrolled.bind(
    "<Button-3>", popup_auto_e_b_menu
)  # Uses mouse button 3 (right click) to open


def disable_clear_all_checkbuttons():
    forced_subtitles_burned.config(state=NORMAL)
    balance_borders.config(state=NORMAL)
    fill_borders.config(state=NORMAL)
    forced_subtitles_burned_var.set("off")
    balance_borders_var.set("off")
    fill_borders_var.set("off")
    forced_subtitles_burned.config(state=DISABLED)
    balance_borders.config(state=DISABLED)
    fill_borders.config(state=DISABLED)


def enable_clear_all_checkbuttons():
    forced_subtitles_burned.config(state=NORMAL)
    balance_borders.config(state=NORMAL)
    fill_borders.config(state=NORMAL)
    forced_subtitles_burned_var.set("off")
    balance_borders_var.set("off")
    fill_borders_var.set("off")


# screenshots ---------------------------------------------------------------------------------------------------------
screenshot_frame = LabelFrame(
    root,
    text=" Sreenshots ",
    labelanchor="nw",
    bd=3,
    font=(set_font, set_font_size + 1, "bold"),
    fg=custom_label_frame_colors["foreground"],
    bg=custom_label_frame_colors["background"],
)
screenshot_frame.grid(column=0, row=3, columnspan=4, padx=5, pady=(5, 3), sticky=E + W)

screenshot_frame.grid_rowconfigure(0, weight=1)
screenshot_frame.grid_columnconfigure(0, weight=1)

# Settings Notebook Frame -----------------------------------------------------------------------------------------
tabs = ttk.Notebook(screenshot_frame, height=150)
tabs.grid(row=0, column=0, columnspan=4, sticky=E + W + N + S, padx=0, pady=0)
tabs.grid_columnconfigure(0, weight=1)
tabs.grid_rowconfigure(0, weight=1)

# image input tab
image_tab = Frame(tabs, bg=custom_frame_bg_colors["specialbg"])
tabs.add(image_tab, text=" Images ")
image_tab.grid_rowconfigure(0, weight=1)
image_tab.grid_columnconfigure(0, weight=100)
image_tab.grid_columnconfigure(3, weight=1)

# image frame
image_frame = Frame(image_tab, bg=custom_frame_bg_colors["background"], bd=0)
image_frame.grid(column=0, columnspan=3, row=0, pady=4, padx=4, sticky=W + E + N + S)
image_frame.grid_columnconfigure(0, weight=1)
image_frame.grid_rowconfigure(0, weight=1)

# image listbox
image_right_scrollbar = Scrollbar(image_frame, orient=VERTICAL)  # scrollbar
image_bottom_scrollbar = Scrollbar(image_frame, orient=HORIZONTAL)  # scrollbar
image_listbox = Listbox(
    image_frame,
    bg=custom_listbox_color["background"],
    fg=custom_listbox_color["foreground"],
    selectbackground=custom_listbox_color["selectbackground"],
    selectforeground=custom_listbox_color["selectforeground"],
    disabledforeground=custom_listbox_color["foreground"],
    height=12,
    state=DISABLED,
    highlightthickness=0,
    yscrollcommand=image_right_scrollbar.set,
    selectmode=SINGLE,
    bd=4,
    activestyle="none",
    xscrollcommand=image_bottom_scrollbar.set,
)
image_listbox.grid(row=0, column=0, rowspan=1, sticky=N + E + S + W)
image_right_scrollbar.config(command=image_listbox.yview)
image_right_scrollbar.grid(row=0, column=1, rowspan=2, sticky=N + W + S)
image_bottom_scrollbar.config(command=image_listbox.xview)
image_bottom_scrollbar.grid(row=1, column=0, sticky=E + W + N)

# image button frame
image_btn_frame = Frame(image_tab, bg=custom_frame_bg_colors["specialbg"], bd=0)
image_btn_frame.grid(column=3, row=0, padx=5, pady=(5, 3), sticky=E + W + N + S)
image_btn_frame.grid_rowconfigure(0, weight=1)
image_btn_frame.grid_rowconfigure(1, weight=1)
image_btn_frame.grid_rowconfigure(2, weight=1)
image_btn_frame.grid_columnconfigure(0, weight=1)
image_btn_frame.grid_columnconfigure(1, weight=1)


# function to add images to listbox
def update_image_listbox(list_of_images):
    # check if source is loaded
    if source_loaded.get() == "":
        messagebox.showinfo(
            parent=root, title="Info", message="You must open a source file first"
        )
        return  # exit function

    # check if source is loaded
    if encode_file_path.get() == "":
        messagebox.showinfo(
            parent=root, title="Info", message="You must open a encode file first"
        )
        return  # exit function

    # check dropped data to ensure files are .png and correct size
    for dropped_files in list_of_images:
        # png check
        if pathlib.Path(dropped_files).suffix != ".png":
            messagebox.showerror(
                parent=root, title="Error", message="Can only drop .PNG files"
            )
            return  # exit this function
        # size check
        if os.stat(pathlib.Path(dropped_files)).st_size > 30000000:
            messagebox.showerror(
                parent=root, title="Error", message="File must be under 30MB"
            )
            return  # exit this function

    # check for resolution miss-match
    for opened_image_file in list_of_images:
        # get opened file resolution
        media_info = MediaInfo.parse(pathlib.Path(opened_image_file))
        image_track_width = media_info.image_tracks[0].width

        # check if both image files and encode resolution is 720p
        if image_track_width <= 1280:  # 720p
            if encode_file_resolution.get() != "720p":
                messagebox.showinfo(
                    parent=root,
                    title="Resolution Error",
                    message=f"Encode source resolution is {encode_file_resolution.get()}.\n\nYour "
                    f"screenshots should be the same resolution",
                )
                return  # exit this function

        # check if both image files and encode resolution is 1080p
        elif image_track_width <= 1920:  # 1080p
            if encode_file_resolution.get() != "1080p":
                messagebox.showinfo(
                    parent=root,
                    title="Resolution Error",
                    message=f"Encode source resolution is {encode_file_resolution.get()}.\n\nYour "
                    f"screenshots should be the same resolution",
                )
                return  # exit this function

        # check if both image files and encode resolution is 2160p
        elif image_track_width <= 3840:  # 2160p
            if encode_file_resolution.get() != "2160p":
                messagebox.showinfo(
                    parent=root,
                    title="Resolution Error",
                    message=f"Encode source resolution is {encode_file_resolution.get()}.\n\nYour "
                    f"screenshots should be the same resolution",
                )
                return  # exit this function

    # check that screenshots are in multiples of 2
    if not len(list_of_images) % 2 == 0:  # if not multiples of 2
        messagebox.showerror(
            parent=root, title="Error", message="Screen shots must be even numbers"
        )
        return  # exit this function

    # add images to the list box
    image_listbox.config(state=NORMAL)
    image_listbox.delete(0, END)
    for img_num, png_img in enumerate(list_of_images, start=1):
        image_listbox.insert(END, f"{img_num}) {png_img}")
    image_listbox.config(state=DISABLED)

    # enable upload button
    upload_ss_button.config(state=NORMAL)


# open screenshot directory function
def open_ss_directory():
    # file dialog to get directory of input files
    ss_dir = filedialog.askdirectory(parent=root, title="Select Directory")

    if ss_dir:
        # disable upload button
        upload_ss_button.config(state=DISABLED)

        # create empty list to be filled
        ss_dir_files_list = []

        # get all .png files from directory
        for ss_files in pathlib.Path(ss_dir).glob("*.png"):
            ss_dir_files_list.append(pathlib.Path(ss_files))

        # call update image listbox function
        update_image_listbox(ss_dir_files_list)


# open files function
def open_ss_files():
    # file dialog to get directory of input files
    ss_files_input = filedialog.askopenfilenames(
        parent=root, title="Select Files", filetypes=[("PNG", "*.png")]
    )

    # if user opens files
    if ss_files_input:
        # disable upload button
        upload_ss_button.config(state=DISABLED)

        # create empty list to be filled
        ss_files_input_files_list = []

        for ss_files in ss_files_input:
            ss_files_input_files_list.append(pathlib.Path(ss_files))

        # call update image listbox function
        update_image_listbox(ss_files_input_files_list)


# multiple input button and pop up menu
def input_popup_menu(*args):  # Menu for input button
    input_menu = Menu(
        image_btn_frame,
        tearoff=False,
        font=(set_font, set_font_size + 1),
        background=custom_button_colors["background"],
        foreground=custom_button_colors["foreground"],
        activebackground=custom_button_colors["activebackground"],
        activeforeground=custom_button_colors["activeforeground"],
    )  # Menu
    input_menu.add_command(label="Open Files", command=open_ss_files)
    input_menu.add_separator()
    input_menu.add_command(label="Open Directory", command=open_ss_directory)
    input_menu.tk_popup(input_button.winfo_rootx(), input_button.winfo_rooty() + 5)


input_button = HoverButton(
    image_btn_frame,
    text="Open...",
    command=input_popup_menu,
    borderwidth="3",
    width=12,
    foreground=custom_button_colors["foreground"],
    background=custom_button_colors["background"],
    activeforeground=custom_button_colors["activeforeground"],
    activebackground=custom_button_colors["activebackground"],
    disabledforeground=custom_button_colors["disabledforeground"],
)
input_button.grid(row=0, column=0, columnspan=1, padx=5, pady=(7, 0), sticky=N + W)
input_button.bind("<Button-3>", input_popup_menu)  # Right click to pop up menu in frame


# png and drop function for image list box
def png_file_drag_and_drop(event):
    # disable upload button
    upload_ss_button.config(state=DISABLED)

    # get dropped data
    png_file_dropped = [x for x in root.splitlist(event.data)]

    # call update image listbox function
    update_image_listbox(png_file_dropped)


# bind frame to drop images into listbox
image_frame.drop_target_register(DND_FILES)
image_frame.dnd_bind("<<Drop>>", png_file_drag_and_drop)


# clear button function
def clear_image_list():
    # remove everything from image listbox
    image_listbox.config(state=NORMAL)
    image_listbox.delete(0, END)
    image_listbox.config(state=DISABLED)
    # disable upload button
    upload_ss_button.config(state=DISABLED)


# clear button
clear_ss_win_btn = HoverButton(
    image_btn_frame,
    text="Clear",
    command=clear_image_list,
    borderwidth="3",
    width=12,
    foreground=custom_button_colors["foreground"],
    background=custom_button_colors["background"],
    activeforeground=custom_button_colors["activeforeground"],
    activebackground=custom_button_colors["activebackground"],
    disabledforeground=custom_button_colors["disabledforeground"],
)
clear_ss_win_btn.grid(row=0, column=1, columnspan=1, padx=5, pady=(7, 0), sticky=N + E)


def choose_indexer_func():
    # hide all top levels if they are opened
    hide_all_toplevels()

    # exit the window
    def exit_index_window():
        index_selection_win.destroy()  # close window
        advanced_root_deiconify()  # restore root

    # index selection window
    index_selection_win = Toplevel()
    index_selection_win.title("Index")
    index_selection_win.configure(background=custom_window_bg_color)
    index_selection_win.geometry(
        f'+{str(int(root.geometry().split("+")[1]) + 180)}+'
        f'{str(int(root.geometry().split("+")[2]) + 230)}'
    )
    index_selection_win.resizable(False, False)
    index_selection_win.grab_set()  # force this window on top of all others
    root.wm_withdraw()  # hide root
    index_selection_win.protocol("WM_DELETE_WINDOW", exit_index_window)
    index_selection_win.grid_rowconfigure(0, weight=1)
    index_selection_win.grid_columnconfigure(0, weight=1)

    # index select frame
    index_sel_frame = Frame(
        index_selection_win,
        highlightbackground=custom_frame_bg_colors["highlightcolor"],
        highlightthickness=2,
        bg=custom_frame_bg_colors["background"],
        highlightcolor=custom_frame_bg_colors["highlightcolor"],
    )
    index_sel_frame.grid(column=0, row=0, columnspan=3, sticky=N + S + E + W)

    # grid/column configure
    for e_n_f in range(3):
        index_sel_frame.grid_columnconfigure(e_n_f, weight=1)
    for e_n_r in range(5):
        index_sel_frame.grid_rowconfigure(e_n_r, weight=1)

    # create label
    index_label = Label(
        index_sel_frame,
        text="Select index method",
        background=custom_label_colors["background"],
        fg=custom_label_colors["foreground"],
        font=(set_font, set_font_size, "bold"),
    )
    index_label.grid(row=0, column=0, columnspan=3, sticky=W + N, padx=5, pady=(2, 0))

    # variable to be returned
    index_selection_var = ""

    # update variable to ffms
    def update_var_ffms():
        nonlocal index_selection_var
        index_selection_var = "ffms"
        index_selection_win.destroy()  # exit the window

    # create 'FFMS' button
    ffms_btn = HoverButton(
        index_sel_frame,
        text="FFMS",
        command=update_var_ffms,
        borderwidth="3",
        foreground=custom_button_colors["foreground"],
        background=custom_button_colors["background"],
        activeforeground=custom_button_colors["activeforeground"],
        activebackground=custom_button_colors["activebackground"],
        disabledforeground=custom_button_colors["disabledforeground"],
    )
    ffms_btn.grid(row=1, column=0, columnspan=3, padx=25, pady=0, sticky=E + W + S)

    # create ffms label
    ffms_label = Label(
        index_sel_frame,
        font=(set_fixed_font, set_font_size - 1),
        text="FFMS supports virtually all formats, however it's not 100% frame accurate. You may "
        "notice a miss-match frame between the source and encode in some occasions.",
        background=custom_label_colors["background"],
        fg=custom_label_colors["foreground"],
        wraplength=320,
        justify=CENTER,
    )
    ffms_label.grid(
        row=2, column=0, columnspan=3, sticky=E + W + N, padx=5, pady=(4, 0)
    )

    # update variable to lwlibav
    def update_var_lwlibav():
        nonlocal index_selection_var
        index_selection_var = "lwlibav"
        index_selection_win.destroy()  # exit the window

    # create 'LWLibavSource' button
    lwlibavsource_btn = HoverButton(
        index_sel_frame,
        text="LWLibavSource",
        command=update_var_lwlibav,
        borderwidth="3",
        foreground=custom_button_colors["foreground"],
        background=custom_button_colors["background"],
        activeforeground=custom_button_colors["activeforeground"],
        activebackground=custom_button_colors["activebackground"],
        disabledforeground=custom_button_colors["disabledforeground"],
    )
    lwlibavsource_btn.grid(
        row=3, column=0, columnspan=3, padx=25, pady=0, sticky=E + W + S
    )

    # create lwlibav label
    lwlibav_label = Label(
        index_sel_frame,
        font=(set_fixed_font, set_font_size - 1),
        text="LWLibavSource (L-Smash) is 100% frame accurate. However, it doesn't have full "
        "support for some video codecs and containers. If you notice black/grey "
        "images being generated with a specific source use FFMS. "
        "If your source is MKV/AVC this is the best option.",
        background=custom_label_colors["background"],
        fg=custom_label_colors["foreground"],
        wraplength=320,
        justify=CENTER,
    )
    lwlibav_label.grid(
        row=4, column=0, columnspan=3, sticky=W + N + E, padx=5, pady=(4, 0)
    )

    # create 'Cancel' button
    index_cancel_btn = HoverButton(
        index_sel_frame,
        text="Cancel",
        width=8,
        command=lambda: [index_selection_win.destroy(), advanced_root_deiconify()],
        borderwidth="3",
        foreground=custom_button_colors["foreground"],
        background=custom_button_colors["background"],
        activeforeground=custom_button_colors["activeforeground"],
        activebackground=custom_button_colors["activebackground"],
        disabledforeground=custom_button_colors["disabledforeground"],
    )
    index_cancel_btn.grid(row=5, column=2, columnspan=1, padx=7, pady=5, sticky=S + E)

    # disable/enable indexers depending on known sources
    if source_file_path.get().endswith(".m2ts"):
        ffms_btn.config(state=DISABLED)
        ffms_label.config(text="FFMS disabled for m2ts")
    if str(source_file_information["format"]).lower() == "vc-1":
        lwlibavsource_btn.config(state=DISABLED)
        lwlibav_label.config(text="LwLibavSource disabled for video codec VC-1")

    index_selection_win.wait_window()  # wait for window to be closed
    open_all_toplevels()  # re-open all top levels if they exist

    # return index variable
    return index_selection_var


# function to check crop
def check_crop_values():
    # exit the window
    def exit_index_window():
        check_crop_win.destroy()  # close window
        advanced_root_deiconify()  # restore root

    # index selection window
    check_crop_win = Toplevel()
    check_crop_win.title("Check Crop")
    check_crop_win.configure(background=custom_window_bg_color)
    check_crop_win.geometry(
        f'{350}x{180}+{str(int(root.geometry().split("+")[1]) + 180)}+'
        f'{str(int(root.geometry().split("+")[2]) + 230)}'
    )
    check_crop_win.resizable(False, False)
    check_crop_win.grab_set()  # force this window on top of all others
    root.wm_withdraw()  # hide root
    check_crop_win.protocol("WM_DELETE_WINDOW", exit_index_window)
    check_crop_win.grid_rowconfigure(0, weight=1)
    check_crop_win.grid_columnconfigure(0, weight=1)

    # index select frame
    check_crop_frame = LabelFrame(
        check_crop_win,
        text=" Crop: ",
        bd=0,
        font=(set_font, set_font_size + 1, "bold"),
        fg=custom_label_frame_colors["foreground"],
        bg=custom_label_frame_colors["background"],
    )
    check_crop_frame.grid(column=0, row=0, columnspan=4, sticky=N + S + E + W)

    # grid/column configure
    # for c_c_f in range(4):
    #     check_crop_frame.grid_columnconfigure(c_c_f, weight=1)
    check_crop_frame.grid_columnconfigure(0, weight=1)
    check_crop_frame.grid_columnconfigure(1, weight=1000)
    check_crop_frame.grid_columnconfigure(2, weight=1000)
    check_crop_frame.grid_columnconfigure(3, weight=1)

    for c_cc_f in range(3):
        check_crop_frame.grid_rowconfigure(c_cc_f, weight=1)

    # variable to be returned
    crop_var = {}

    # update variable for crop
    def update_crop_var():
        nonlocal crop_var
        crop_var.update(
            {
                "crop": {
                    "left": left_entry_box.get().strip(),
                    "right": right_entry_box.get().strip(),
                    "top": top_entry_box.get().strip(),
                    "bottom": bottom_entry_box.get().strip(),
                }
            }
        )

        # ensure all values are only numbers
        try:
            int(left_entry_box.get().strip())
            int(right_entry_box.get().strip())
            int(top_entry_box.get().strip())
            int(bottom_entry_box.get().strip())
        except ValueError:
            messagebox.showerror(
                parent=check_crop_win,
                title="Error",
                message="Values can only be numbers!\n\n"
                "If crop is nothing leave this at 0",
            )
            return  # exit the function

        if left_entry_box.get().strip() == "" or left_entry_box.get().strip() == "0":
            dict_left_crop = "0"
        else:
            dict_left_crop = left_entry_box.get().strip()

        if right_entry_box.get().strip() == "" or right_entry_box.get().strip() == "0":
            dict_right_crop = "0"
        else:
            dict_right_crop = right_entry_box.get().strip()

        if top_entry_box.get().strip() == "" or top_entry_box.get().strip() == "0":
            dict_top_crop = "0"
        else:
            dict_top_crop = top_entry_box.get().strip()

        if (
            bottom_entry_box.get().strip() == ""
            or bottom_entry_box.get().strip() == "0"
        ):
            dict_bottom_crop = "0"
        else:
            dict_bottom_crop = bottom_entry_box.get().strip()

        # update dictionary crop info
        source_file_information.update(
            {
                "crop": {
                    "left": dict_left_crop,
                    "right": dict_right_crop,
                    "top": dict_top_crop,
                    "bottom": dict_bottom_crop,
                }
            }
        )

        check_crop_win.destroy()  # exit the window

    # left crop label
    left_label = Label(
        check_crop_frame,
        font=(set_fixed_font, set_font_size - 1),
        text="Left:",
        background=custom_label_colors["background"],
        fg=custom_label_colors["foreground"],
    )
    left_label.grid(row=0, column=0, sticky=W + S, padx=5, pady=(7, 10))

    # left entry box
    left_entry_box = Entry(
        check_crop_frame,
        borderwidth=4,
        width=8,
        fg=custom_entry_colors["foreground"],
        bg=custom_entry_colors["background"],
        disabledforeground=custom_entry_colors["disabledforeground"],
        disabledbackground=custom_entry_colors["disabledbackground"],
        font=(set_fixed_font, set_font_size),
    )
    left_entry_box.grid(row=0, column=1, padx=5, pady=(7, 10), sticky=W + S)

    # right crop label
    right_label = Label(
        check_crop_frame,
        font=(set_fixed_font, set_font_size - 1),
        text="Right:",
        background=custom_label_colors["background"],
        fg=custom_label_colors["foreground"],
    )
    right_label.grid(row=0, column=2, sticky=E + S, padx=5, pady=(7, 10))

    # right entry box
    right_entry_box = Entry(
        check_crop_frame,
        borderwidth=4,
        width=8,
        fg=custom_entry_colors["foreground"],
        bg=custom_entry_colors["background"],
        disabledforeground=custom_entry_colors["disabledforeground"],
        disabledbackground=custom_entry_colors["disabledbackground"],
        font=(set_fixed_font, set_font_size),
    )
    right_entry_box.grid(row=0, column=3, padx=5, pady=(7, 10), sticky=E + S)

    # top crop label
    top_label = Label(
        check_crop_frame,
        font=(set_fixed_font, set_font_size - 1),
        text="Top:",
        background=custom_label_colors["background"],
        fg=custom_label_colors["foreground"],
    )
    top_label.grid(row=1, column=0, sticky=W + N, padx=5, pady=(16, 0))

    # top entry box
    top_entry_box = Entry(
        check_crop_frame,
        borderwidth=4,
        width=8,
        fg=custom_entry_colors["foreground"],
        bg=custom_entry_colors["background"],
        disabledforeground=custom_entry_colors["disabledforeground"],
        disabledbackground=custom_entry_colors["disabledbackground"],
        font=(set_fixed_font, set_font_size),
    )
    top_entry_box.grid(row=1, column=1, padx=5, pady=(7, 0), sticky=W + N)

    # bottom crop label
    bottom_label = Label(
        check_crop_frame,
        font=(set_fixed_font, set_font_size - 1),
        text="Bottom:",
        background=custom_label_colors["background"],
        fg=custom_label_colors["foreground"],
    )
    bottom_label.grid(row=1, column=2, sticky=E + N, padx=5, pady=(16, 0))

    # bottom entry box
    bottom_entry_box = Entry(
        check_crop_frame,
        borderwidth=4,
        width=8,
        fg=custom_entry_colors["foreground"],
        bg=custom_entry_colors["background"],
        disabledforeground=custom_entry_colors["disabledforeground"],
        disabledbackground=custom_entry_colors["disabledbackground"],
        font=(set_fixed_font, set_font_size),
    )
    bottom_entry_box.grid(row=1, column=3, padx=5, pady=(7, 0), sticky=E + N)

    # create button frame
    crop_btn_frame = Frame(check_crop_frame, bg=custom_frame_bg_colors["background"])
    crop_btn_frame.grid(column=0, row=2, columnspan=4, sticky=N + S + E + W)
    for c_b_f in range(3):
        crop_btn_frame.grid_columnconfigure(c_b_f, weight=1)
    crop_btn_frame.grid_rowconfigure(0, weight=1)

    # create 'Cancel' button
    crop_cancel_btn = HoverButton(
        crop_btn_frame,
        text="Cancel",
        width=8,
        command=lambda: [check_crop_win.destroy(), advanced_root_deiconify()],
        borderwidth="3",
        foreground=custom_button_colors["foreground"],
        background=custom_button_colors["background"],
        activeforeground=custom_button_colors["activeforeground"],
        activebackground=custom_button_colors["activebackground"],
        disabledforeground=custom_button_colors["disabledforeground"],
    )
    crop_cancel_btn.grid(row=0, column=0, padx=7, pady=5, sticky=S + W)

    # create 'view script' button
    view_script = HoverButton(
        crop_btn_frame,
        text="View Script",
        width=8,
        command=lambda: open_script_in_viewer(pathlib.Path(input_script_path.get())),
        borderwidth="3",
        foreground=custom_button_colors["foreground"],
        background=custom_button_colors["background"],
        activeforeground=custom_button_colors["activeforeground"],
        activebackground=custom_button_colors["activebackground"],
        disabledforeground=custom_button_colors["disabledforeground"],
    )
    view_script.grid(row=0, column=1, padx=7, pady=5, sticky=W + E + S)

    # create 'Accept' button
    accept_btn = HoverButton(
        crop_btn_frame,
        text="Accept",
        width=8,
        command=update_crop_var,
        borderwidth="3",
        foreground=custom_button_colors["foreground"],
        background=custom_button_colors["background"],
        activeforeground=custom_button_colors["activeforeground"],
        activebackground=custom_button_colors["activebackground"],
        disabledforeground=custom_button_colors["disabledforeground"],
    )
    accept_btn.grid(row=0, column=2, padx=7, pady=5, sticky=S + E)

    # update all the crop values to be displayed in the window
    if source_file_information["crop"] != "None":
        # left crop
        if source_file_information["crop"]["left"] == "":
            left_entry_box.insert(0, "0")
        else:
            left_entry_box.insert(0, source_file_information["crop"]["left"])
        # right crop
        if source_file_information["crop"]["right"] == "":
            right_entry_box.insert(0, "0")
        else:
            right_entry_box.insert(0, source_file_information["crop"]["right"])
        # top crop
        if source_file_information["crop"]["top"] == "":
            top_entry_box.insert(0, "0")
        else:
            top_entry_box.insert(0, source_file_information["crop"]["top"])
        # bottom crop
        if source_file_information["crop"]["bottom"] == "":
            bottom_entry_box.insert(0, "0")
        else:
            bottom_entry_box.insert(0, source_file_information["crop"]["bottom"])

    # if there was no crop fill the window with 0's
    else:
        left_entry_box.insert(0, "0")
        right_entry_box.insert(0, "0")
        top_entry_box.insert(0, "0")
        bottom_entry_box.insert(0, "0")

    check_crop_win.wait_window()  # wait for window to be closed

    # return index variable
    return crop_var


def auto_screen_shot_status_window(re_sync=0, operator=None):
    """auto screenshot function"""

    # define parser
    img_path_parser = ConfigParser()
    img_path_parser.read(config_file)

    # select desired amount of screenshots
    screen_amount_check = screen_shot_count_spinbox()

    if screen_amount_check == "":
        return  # exit this function

    # check crop
    if source_file_information["crop"] != "None":
        checking_crop = check_crop_values()

        if not checking_crop:
            return  # exit this function

    # choose indexer
    get_indexer = choose_indexer_func()

    if get_indexer == "":
        return  # exit this function

    # start a queue for multi-threaded communication
    ss_status_queue = Queue()

    # screenshot status window
    screenshot_status_window = Toplevel()
    screenshot_status_window.configure(background=custom_window_bg_color)
    screenshot_status_window.title("Screenshot Status")
    screenshot_status_window.geometry(
        f'+{str(int(root.geometry().split("+")[1]) + 126)}+'
        f'{str(int(root.geometry().split("+")[2]) + 230)}'
    )
    screenshot_status_window.resizable(False, False)
    root.wm_withdraw()  # hide root
    screenshot_status_window.grid_rowconfigure(0, weight=1)
    screenshot_status_window.grid_columnconfigure(0, weight=1)

    # screenshot output frame
    ss_output_frame = Frame(
        screenshot_status_window,
        highlightbackground=custom_frame_bg_colors["highlightcolor"],
        highlightthickness=2,
        bg=custom_frame_bg_colors["background"],
        highlightcolor=custom_frame_bg_colors["highlightcolor"],
    )
    ss_output_frame.grid(column=0, row=0, columnspan=3, sticky=N + S + E + W)
    for e_n_f in range(3):
        ss_output_frame.grid_columnconfigure(e_n_f, weight=1)
        ss_output_frame.grid_rowconfigure(e_n_f, weight=1)

    # create scrolled text widget
    ss_status_info = scrolledtextwidget.ScrolledText(
        ss_output_frame,
        height=18,
        bg=custom_scrolled_text_widget_color["background"],
        fg=custom_scrolled_text_widget_color["foreground"],
        bd=4,
        wrap=WORD,
        state=DISABLED,
        font=(set_fixed_font, set_font_size - 1),
    )
    ss_status_info.grid(
        row=0, column=0, columnspan=3, pady=(2, 0), padx=5, sticky=E + W
    )

    def screenshot_close_button():
        """exit the status window"""
        check_exit = messagebox.askyesno(
            parent=screenshot_status_window,
            title="Close?",
            message="Are you sure you want to end the process?\nNote: This will kill the entire program!",
        )
        if check_exit:
            root.destroy()

    # create 'Close' button
    ss_close_btn = HoverButton(
        ss_output_frame,
        text="Close",
        command=screenshot_close_button,
        borderwidth="3",
        width=8,
        foreground=custom_button_colors["foreground"],
        background=custom_button_colors["background"],
        activeforeground=custom_button_colors["activeforeground"],
        activebackground=custom_button_colors["activebackground"],
        disabledforeground=custom_button_colors["disabledforeground"],
    )
    ss_close_btn.grid(row=2, column=2, columnspan=1, padx=7, pady=5, sticky=E)
    screenshot_status_window.protocol("WM_DELETE_WINDOW", screenshot_close_button)

    def semi_automatic_screenshots(ss_queue):
        """threaded function to index and generate screenshots"""

        # define config parser
        semi_auto_img_parser = ConfigParser()
        semi_auto_img_parser.read(config_file)

        # define vs core
        core = vs.core

        # load needed plugins
        try:
            core.std.LoadPlugin("runtime/apps/image_comparison/SubText.dll")
        except vs.Error:
            pass
        try:
            core.std.LoadPlugin("runtime/apps/image_comparison/libimwri.dll")
        except vs.Error:
            pass
        try:
            core.std.LoadPlugin("runtime/apps/image_comparison/libvslsmashsource.dll")
        except vs.Error:
            pass
        try:
            core.std.LoadPlugin("runtime/apps/image_comparison/libfpng.dll")
        except vs.Error:
            pass
        try:
            core.std.LoadPlugin("runtime/apps/image_comparison/ffms2.dll")
        except vs.Error:
            pass

        # update queue with information
        ss_queue.put(
            f"Indexing {str(pathlib.Path(source_file_path.get()).name)} and  "
            f"{str(pathlib.Path(encode_file_path.get()).name)} with {get_indexer}. "
            f"\n\nThis could take a while depending on your systems storage speed...\n\n"
        )

        # index the source file with lwlibavsource
        if get_indexer == "lwlibav":
            # update queue with information
            ss_queue.put("Indexing source...")

            # index source file
            # if index is found in the staxrip temp working directory, attempt to use it
            if (
                pathlib.Path(
                    str(pathlib.Path(source_file_path.get()).with_suffix("")) + "_temp/"
                ).is_dir()
                and pathlib.Path(
                    str(pathlib.Path(source_file_path.get()).with_suffix(""))
                    + "_temp/temp.lwi"
                ).is_file()
            ):

                # update queue with information
                ss_queue.put("\nIndex found in staxrip temp, attempting to use...")

                # define cache path
                lwi_cache_path = pathlib.Path(
                    str(pathlib.Path(source_file_path.get()).with_suffix(""))
                    + "_temp/temp.lwi"
                )

                # try to use index on source file with the cache path
                try:
                    source_file = core.lsmas.LWLibavSource(
                        source=source_file_path.get(), cachefile=lwi_cache_path
                    )

                # if index cannot be used
                except vs.Error:

                    # update queue with information
                    ss_queue.put(
                        "\nL-Smash version miss-match, indexing source again..."
                    )

                    # index source file
                    source_file = core.lsmas.LWLibavSource(source_file_path.get())

            # if no existing index is found index source file
            else:
                try:
                    # create index
                    source_file = core.lsmas.LWLibavSource(source_file_path.get())
                except vs.Error:
                    # delete index
                    pathlib.Path(source_file_path.get() + ".lwi").unlink(
                        missing_ok=True
                    )
                    # create index
                    source_file = core.lsmas.LWLibavSource(source_file_path.get())

            # update queue with information
            ss_queue.put(" Done!\nIndexing encode...")

            # index encode file
            try:
                # create index
                encode_file = core.lsmas.LWLibavSource(encode_file_path.get())
            except vs.Error:
                # delete index
                pathlib.Path(encode_file_path.get() + ".lwi").unlink(missing_ok=True)
                # create index
                encode_file = core.lsmas.LWLibavSource(encode_file_path.get())

        # index the source file with ffms
        elif get_indexer == "ffms":
            # update queue with information
            ss_queue.put("Indexing source...")

            # index source file
            # if index is found in the staxrip temp working directory, attempt to use it
            if (
                pathlib.Path(
                    str(pathlib.Path(source_file_path.get()).with_suffix("")) + "_temp/"
                ).is_dir()
                and pathlib.Path(
                    str(pathlib.Path(source_file_path.get()).with_suffix(""))
                    + "_temp/temp.ffindex"
                ).is_file()
            ):

                # update queue with information
                ss_queue.put("\nIndex found in staxrip temp, attempting to use...")

                # define cache path
                ffindex_cache_path = pathlib.Path(
                    str(pathlib.Path(source_file_path.get()).with_suffix(""))
                    + "_temp/temp.ffindex"
                )

                # try to use index on source file with the cache path
                try:
                    source_file = core.ffms2.Source(
                        source=source_file_path.get(), cachefile=ffindex_cache_path
                    )

                # if index cannot be used
                except vs.Error:

                    # update queue with information
                    ss_queue.put(
                        "\nFFINDEX version miss-match, indexing source again..."
                    )

                    # index source file
                    source_file = core.ffms2.Source(source_file_path.get())

            # if no existing index is found index source file
            else:
                try:
                    # create index
                    source_file = core.ffms2.Source(source_file_path.get())
                except vs.Error:
                    # delete index
                    pathlib.Path(source_file_path.get() + ".ffindex").unlink(
                        missing_ok=True
                    )
                    # create index
                    source_file = core.ffms2.Source(source_file_path.get())

            # update queue with information
            ss_queue.put(" Done!\nIndexing encode...")

            # index encode file
            try:
                # create index
                encode_file = core.ffms2.Source(encode_file_path.get())
            except vs.Error:
                # delete index
                pathlib.Path(encode_file_path.get() + ".ffindex").unlink(
                    missing_ok=True
                )
                # create index
                encode_file = core.ffms2.Source(encode_file_path.get())

        # update queue with information
        ss_queue.put(" Done!")

        # get the total number of frames from source file
        num_source_frames = len(source_file)

        # Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic,
        # Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL,
        # MarginR, MarginV,

        # set subtitle scale style
        selected_sub_style = (
            "Segoe UI,16,&H000ac7f5,&H00000000,&H00000000,&H00000000,"
            "1,0,0,0,100,100,0,0,1,1,0,7,5,0,0,1"
        )

        # check for custom user image amount
        if semi_auto_img_parser["screenshot_settings"]["semi_auto_count"] != "":
            comparison_img_count = int(
                semi_auto_img_parser["screenshot_settings"]["semi_auto_count"]
            )
        else:
            comparison_img_count = 20

        # update queue with information
        ss_queue.put(
            f"\n\nCollecting {str(comparison_img_count)} 'B' frames to generate "
            "comparison images from..."
        )

        # detect b frames from encode to generate a list
        b_frames = (
            linspace(
                int(num_source_frames * 0.15),
                int(num_source_frames * 0.75),
                int(comparison_img_count),
            )
            .astype(int)
            .tolist()
        )
        for i, frame in enumerate(b_frames):
            while encode_file.get_frame(frame).props["_PictType"].decode() != "B":
                frame += 1
            b_frames[i] = frame

        # update queue with information
        ss_queue.put(
            f" Completed!\n\nGenerating {str(comparison_img_count)} sets of comparisons... "
            f"This depends on system storage speed..."
        )

        # make new temporary image folder
        image_output_dir = None
        if (
            img_path_parser["image_generation_folder"]["path"] != ""
            and pathlib.Path(
                img_path_parser["image_generation_folder"]["path"]
            ).is_dir()
        ):
            image_output_dir = pathlib.Path(
                pathlib.Path(img_path_parser["image_generation_folder"]["path"])
                / f"{pathlib.Path(encode_file_path.get()).stem}_images"
            )
        else:
            image_output_dir = pathlib.Path(
                pathlib.Path(encode_file_path.get()).parent
                / f"{pathlib.Path(encode_file_path.get()).stem}_images"
            )

        # check if temp image dir exists, if so delete it!
        if image_output_dir.exists():
            shutil.rmtree(image_output_dir, ignore_errors=True)

        # create main image dir
        image_output_dir.mkdir(exist_ok=True)

        # create comparison image directory and define it as variable
        pathlib.Path(pathlib.Path(image_output_dir) / "img_comparison").mkdir(
            exist_ok=True
        )
        screenshot_comparison_var.set(
            str(pathlib.Path(pathlib.Path(image_output_dir) / "img_comparison"))
        )

        # create selected image directory and define it as variable
        pathlib.Path(pathlib.Path(image_output_dir) / "img_selected").mkdir(
            exist_ok=True
        )
        screenshot_selected_var.set(
            str(pathlib.Path(pathlib.Path(image_output_dir) / "img_selected"))
        )

        # create sync image directory and define it as variable
        pathlib.Path(pathlib.Path(image_output_dir) / "img_sync").mkdir(exist_ok=True)
        screenshot_sync_var.set(
            str(pathlib.Path(pathlib.Path(image_output_dir) / "img_sync"))
        )

        # create sub directories
        pathlib.Path(pathlib.Path(image_output_dir) / "img_sync/sync1").mkdir(
            exist_ok=True
        )

        pathlib.Path(pathlib.Path(image_output_dir) / "img_sync/sync2").mkdir(
            exist_ok=True
        )

        # crop
        if str(source_file_information["crop"]) != "None":
            source_file = core.std.Crop(
                source_file,
                left=int(source_file_information["crop"]["left"]),
                right=int(source_file_information["crop"]["right"]),
                top=int(source_file_information["crop"]["top"]),
                bottom=int(source_file_information["crop"]["bottom"]),
            )

        # if resolutions are not the same, resize the source to match encode resolution
        if (
            source_file.width != encode_file.width
            and source_file.height != encode_file.height
        ):
            source_file = core.resize.Spline36(
                source_file,
                width=int(encode_file.width),
                height=int(encode_file.height),
                dither_type="error_diffusion",
            )

        # hdr tone-map
        if source_file_information["hdr"] == "True":
            source_file = awsmfunc.DynamicTonemap(clip=source_file)
            encode_file = awsmfunc.DynamicTonemap(clip=encode_file)

        # define the subtitle/frame info for source and encode
        vs_source_info = core.sub.Subtitle(
            clip=source_file, text="Source", style=selected_sub_style
        )
        vs_encode_info = awsmfunc.FrameInfo(
            clip=encode_file, title="BHDStudio", style=selected_sub_style
        )

        ss_queue.put("\n\nGenerating Screenshots, please wait...\n")

        def screen_gen_callback(sg_call_back):
            """define callback function for screen gen"""
            ss_queue.put("\n" + str(sg_call_back).replace("ScreenGen: ", ""))

        # change b_frames with rsync offset
        sync_frames = []
        if re_sync:
            for x_frames in b_frames:
                if operator == "+":
                    sync_frames.append(int(x_frames) + re_sync)
                elif operator == "-":
                    sync_frames.append(int(x_frames) - re_sync)
        else:
            sync_frames = b_frames

        # generate source images
        awsmfunc.ScreenGen(
            vs_source_info,
            frame_numbers=sync_frames,
            fpng_compression=2,
            folder=screenshot_comparison_var.get(),
            suffix="a_source__%d",
            callback=screen_gen_callback,
        )

        # generate encode images
        awsmfunc.ScreenGen(
            vs_encode_info,
            frame_numbers=b_frames,
            fpng_compression=2,
            folder=screenshot_comparison_var.get(),
            suffix="b_encode__%d",
            callback=screen_gen_callback,
        )

        # generate some sync frames
        ss_queue.put("\n\nGenerating a few sync frames...\n\n")

        # select two frames randomly from list
        sync_1 = choice(b_frames)
        remove_sync1 = b_frames.copy()
        remove_sync1.remove(sync_1)
        sync_2 = choice(remove_sync1)

        # reference subs
        reference_sub_style = (
            "Segoe UI,26,&H000ac7f5,&H00000000,&H00000000,&H00000000,"
            "1,0,0,0,100,100,0,0,1,1,0,7,5,0,0,1"
        )
        vs_source_ref_info = core.sub.Subtitle(
            clip=source_file, text="Sync", style=reference_sub_style
        )
        vs_encode_ref_info = core.sub.Subtitle(
            clip=encode_file, text="Reference", style=reference_sub_style
        )

        # generate screens for the two reference frames
        awsmfunc.ScreenGen(
            vs_encode_ref_info,
            frame_numbers=[sync_1, sync_2],
            fpng_compression=2,
            folder=screenshot_sync_var.get(),
            suffix="b_encode__%d",
            callback=screen_gen_callback,
        )

        # generate 10 source frames around those reference frames
        awsmfunc.ScreenGen(
            vs_source_ref_info,
            frame_numbers=[
                sync_1 - 4,
                sync_1 - 3,
                sync_1 - 2,
                sync_1 - 1,
                sync_1,
                sync_1 + 1,
                sync_1 + 2,
                sync_1 + 3,
                sync_1 + 4,
            ],
            fpng_compression=2,
            folder=pathlib.Path(pathlib.Path(screenshot_sync_var.get()) / "sync1"),
            suffix="a_source__%d",
            callback=screen_gen_callback,
        )

        awsmfunc.ScreenGen(
            vs_source_ref_info,
            frame_numbers=[
                sync_2 - 4,
                sync_2 - 3,
                sync_2 - 2,
                sync_2 - 1,
                sync_2,
                sync_2 + 1,
                sync_2 + 2,
                sync_2 + 3,
                sync_2 + 4,
            ],
            fpng_compression=2,
            folder=pathlib.Path(pathlib.Path(screenshot_sync_var.get()) / "sync2"),
            suffix="a_source__%d",
            callback=screen_gen_callback,
        )

        # update queue with information
        ss_queue.put("Completed")

    def update_status(text):
        """function to update status window with text"""
        ss_status_info.config(state=NORMAL)
        ss_status_info.insert(END, str(text))
        ss_status_info.config(state=DISABLED)
        ss_status_info.see(END)

    def gui_loop_checker():
        """loop to constantly check queue and update program depending on the output"""

        # check if queue has any ss_queue_data in it
        try:
            ss_queue_data = ss_status_queue.get_nowait()
        # if it is empty set variable to None
        except Empty:
            ss_queue_data = None

        # if ss_queue_data is not empty update status
        if ss_queue_data is not None:

            # if ss_queue_data is 'Completed' close the window and continue
            if ss_queue_data == "Completed":
                # send task done and clean up queue
                ss_status_queue.task_done()
                ss_status_queue.join()

                # close screenshot status window
                screenshot_status_window.destroy()

                # root withdraw/top-levels
                hide_all_toplevels()
                root.wm_withdraw()

                # open automatic screenshot generator window
                selected_images = ImageViewer(
                    custom_window_bg_color,
                    custom_frame_bg_colors,
                    set_font,
                    set_font_size,
                    custom_label_frame_colors,
                    custom_label_colors,
                    custom_button_colors,
                    custom_listbox_color,
                    set_fixed_font,
                    screenshot_selected_var.get(),
                    screenshot_comparison_var.get(),
                    screenshot_sync_var.get(),
                )

                image_viewer_output = selected_images.get_dict()

                if not image_viewer_output["synced"]:
                    auto_screen_shot_status_window(
                        re_sync=image_viewer_output["offset"],
                        operator=image_viewer_output["operator"],
                    )
                    return

                # re-open windows/root
                advanced_root_deiconify()
                open_all_toplevels()

                # update image list box with returned output from ImageViewer class
                update_image_listbox(image_viewer_output["images"])

                # exit this loop
                return

            # If there is an error print the error to the message box and exit this loop
            elif "Error" in ss_queue_data:
                # update screenshot status window
                update_status(ss_queue_data)

                # call queue done
                ss_status_queue.task_done()

                # exit this loop
                return

            # if ss_queue_data is anything other than "Completed" or "Error"
            else:
                # update screenshot status window
                update_status(ss_queue_data)

                # call queue done
                ss_status_queue.task_done()

        # loop every millisecond to check the queue
        root.after(1, gui_loop_checker)

    # define thread
    ss_gen_thread = threading.Thread(
        target=semi_automatic_screenshots, args=(ss_status_queue,), daemon=True
    )

    # start ss queue checker
    gui_loop_checker()

    # start thread
    ss_gen_thread.start()


# auto generate button
auto_screens_multi_btn = HoverButton(
    image_btn_frame,
    text="Generate IMGs",
    command=auto_screen_shot_status_window,
    borderwidth="3",
    state=DISABLED,
    width=12,
    foreground=custom_button_colors["foreground"],
    background=custom_button_colors["background"],
    activeforeground=custom_button_colors["activeforeground"],
    activebackground=custom_button_colors["activebackground"],
    disabledforeground=custom_button_colors["disabledforeground"],
)
auto_screens_multi_btn.grid(
    row=1, column=0, rowspan=2, padx=5, pady=(7, 7), sticky=S + W
)


def upload_to_beyond_hd_co_window():
    """upload pictures to beyond.co and return medium linked images"""

    # create queue instance
    upload_to_bhdco_queue = Queue()

    # define upload error variable
    upload_error = BooleanVar()

    def manipulate_ss_upload_window(update_string):
        """manipulate scrolled text box to reduce code"""
        try:
            upload_ss_info.config(state=NORMAL)
            upload_ss_info.delete("1.0", END)
            upload_ss_info.insert(END, update_string)
            upload_ss_info.config(state=DISABLED)
        except TclError:
            return  # exit the function

    def upload_to_beyond_hd_co(upload_bhdco_queue):
        """threaded function to upload to beyond hd"""

        # create empty list
        list_of_pngs = []

        # use regex to get only the filename
        for loaded_images in image_listbox.get(0, END):
            img = re.search(r"[\d{1,3}]\)\s(.+)", loaded_images)
            list_of_pngs.append(str(pathlib.Path(img.group(1))))

        # sort list
        list_of_pngs.sort()

        # check if status window is closed
        if upload_error.get():
            return  # exit function

        # login to beyondhd image host
        # start requests session
        session = requests.session()

        # check if status window is closed
        if upload_error.get():
            return  # exit function

        # get raw text of web page
        upload_bhdco_queue.put("Getting auth token from beyondhd.co\n\n")
        try:
            auth_raw = session.get("https://beyondhd.co/login", timeout=60).text
        except requests.exceptions.ConnectionError:
            upload_bhdco_queue.put("No internet connection")
            return  # exit the function

        # check if status window is closed
        if upload_error.get():
            return  # exit function

        # if web page didn't return a response
        if not auth_raw:
            upload_bhdco_queue.put("Could not access beyondhd.co")
            return  # exit the function

        # split auth token out of raw web page for later use
        auth_code = (
            auth_raw.split("PF.obj.config.auth_token = ")[1]
            .split(";")[0]
            .replace('"', "")
        )
        upload_bhdco_queue.put("Auth token found")
        if not auth_code:
            upload_bhdco_queue.put("Could not find auth token")
            return  # exit the function

        # login payload
        login_payload = {
            "login-subject": decode_user,
            "password": decode_pass,
            "auth_token": auth_code,
        }

        # check if status window is closed
        if upload_error.get():
            return  # exit function

        # login post
        upload_bhdco_queue.put(
            f"Logging in to beyondhd.co as {login_payload['login-subject']}"
        )
        try:
            login_post = session.post(
                "https://beyondhd.co/login", data=login_payload, timeout=60
            )
        except requests.exceptions.ConnectionError:
            upload_bhdco_queue.put("No internet connection")
            return  # exit the function

        # check if status window is closed
        if upload_error.get():
            return  # exit function

        # find user info from login post
        confirm_login = re.search(
            r"CHV.obj.logged_user =(.+);", login_post.text, re.MULTILINE
        )
        upload_bhdco_queue.put(f"Successfully logged in as {decode_user}")

        # if post confirm_login is none
        if not confirm_login:
            upload_bhdco_queue.put("Incorrect username or password")
            return  # exit the function

        # generate album name
        # use regex to find the movie name
        movie_name = re.finditer(
            r"\d{4}(?!p)", pathlib.Path(encode_file_path.get()).stem, re.IGNORECASE
        )
        movie_name_extraction = []  # create empty list
        for match in movie_name:  # get the "span" from the movie name
            movie_name_extraction.append(match.span())
        # extract the full movie name (removing anything that is not needed from the filename)
        try:
            full_movie_name = (
                pathlib.Path(encode_file_path.get())
                .stem[0 : int(movie_name_extraction[-1][-1])]
                .replace(".", " ")
                .strip()
            )
            generated_album_name = f"{encode_file_resolution.get()} | {full_movie_name}"
        # if for some reason there is an index error just generate a generic album name based off of the encoded input
        except IndexError:
            generated_album_name = str(
                pathlib.Path(pathlib.Path(encode_file_path.get()).name).with_suffix("")
            )

        # create album payload
        album_payload = {
            "auth_token": auth_code,
            "action": "create-album",
            "type": "album",
            "album[name]": generated_album_name,
            "album[description]": main_root_title,
            "album[password]": "",
            "album[new]": "true",
        }

        # check if status window is closed
        if upload_error.get():
            return  # exit function

        # create album post
        upload_bhdco_queue.put(f"Creating album:\n{generated_album_name}")
        try:
            album_post = session.post(
                "https://beyondhd.co/json", data=album_payload, timeout=60
            )
        except requests.exceptions.ConnectionError:
            upload_bhdco_queue.put("No internet connection")
            return  # exit the function
        upload_bhdco_queue.put(f"{generated_album_name} album was created")

        # check for success message
        if not album_post.json()["success"]["message"] == "Content added to album":
            upload_bhdco_queue.put(album_post.json()["success"]["message"])
            return  # exit the function

        # get album_id for later use
        posted_album_id = album_post.json()["album"]["id_encoded"]

        # upload files to new album with the album id
        upload_files_payload = {
            "type": "file",
            "action": "upload",
            "auth_token": auth_code,
            "nsfw": 0,
            "album_id": posted_album_id,
        }

        # create empty list to convert png to bytes
        bytes_converter_png_list = []

        # convert list of png files to bytes and append them to the above list
        for png_file in list_of_pngs:
            with open(str(png_file), "rb") as f:
                bytes_converter_png_list.append(
                    {"source": (str(pathlib.Path(png_file).name), f.read())}
                )

        # get length of list
        images_len = len(bytes_converter_png_list)

        # set empty string to update
        description_info = ""

        # clear screenshot info window
        upload_bhdco_queue.put("")

        # upload image 1 at a time
        for (png_num, current_image) in enumerate(bytes_converter_png_list, start=1):
            if not upload_error.get():
                upload_bhdco_queue.put(f"Uploading image {png_num}/{images_len}\n")
                # upload files
                try:
                    upload_file_post = session.post(
                        "https://beyondhd.co/json",
                        files=current_image,
                        data=upload_files_payload,
                    )
                except requests.exceptions.ConnectionError:  # if there is a connection error show an error
                    upload_bhdco_queue.put("Upload connection error")
                    upload_error.set(True)  # set error to True
                    return  # exit the function

                # if upload file returns an 'ok' status
                if upload_file_post.ok:
                    # add uploaded image and returned url to description info string
                    description_info += (
                        f"[url={upload_file_post.json()['image']['url_viewer']}]"
                        f"[img]{upload_file_post.json()['image']['medium']['url']}[/img][/url]\n"
                    )

                    # upload status was a success
                    if (
                        upload_file_post.json()["success"]["message"]
                        != "image uploaded"
                    ):
                        upload_error.set(True)  # set error to True

                else:
                    upload_error.set(True)  # set error to True
                    upload_bhdco_queue.put(
                        f"Error code from beyondhd.co {str(upload_file_post.status_code)}"
                    )
                    return  # exit the function

        # if images are uploaded/returned
        if not upload_error.get():
            # send completed to kill the polling loop
            upload_bhdco_queue.put("Completed!")
            screenshot_final_func(description_info, generated_album_name)

    def screenshot_final_func(description_info, generated_album_name):
        """change tabs to 'URLs' and insert the image description string"""

        # clear screenshot box
        screenshot_scrolledtext.delete("1.0", END)

        # add description string to screenshot box
        screenshot_scrolledtext.insert(END, description_info)

        # swap tab
        tabs.select(url_tab)

        # add success message to upload status window
        manipulate_ss_upload_window(
            f"Upload is successful!\n\nImages are upload to album:\n"
            f"{generated_album_name}\n\nClick OK to continue"
        )

    def upload_ss_exit_func():
        """function to exit the screenshot upload window"""

        # exit function at next chance
        upload_error.set(True)

        # close window
        upload_ss_status.destroy()

        # re-open root window
        advanced_root_deiconify()

    # upload status window
    upload_ss_status = Toplevel()
    upload_ss_status.configure(background=custom_window_bg_color)
    upload_ss_status.title("Upload Status")
    upload_ss_status.geometry(
        f'{460}x{240}+{str(int(root.geometry().split("+")[1]) + 138)}+'
        f'{str(int(root.geometry().split("+")[2]) + 230)}'
    )
    upload_ss_status.resizable(False, False)
    upload_ss_status.grab_set()  # force this window on top
    upload_ss_status.wm_protocol("WM_DELETE_WINDOW", upload_ss_exit_func)
    root.wm_withdraw()  # hide root
    upload_ss_status.grid_rowconfigure(0, weight=1)
    upload_ss_status.grid_columnconfigure(0, weight=1)

    # encoder name frame
    upload_ss_frame = Frame(
        upload_ss_status,
        highlightbackground=custom_frame_bg_colors["highlightcolor"],
        highlightthickness=2,
        bg=custom_frame_bg_colors["background"],
        highlightcolor=custom_frame_bg_colors["highlightcolor"],
    )
    upload_ss_frame.grid(column=0, row=0, columnspan=3, sticky=N + S + E + W)
    upload_ss_frame.grid_columnconfigure(0, weight=1)
    upload_ss_frame.grid_columnconfigure(1, weight=1)
    upload_ss_frame.grid_columnconfigure(2, weight=1)
    upload_ss_frame.grid_rowconfigure(0, weight=200)
    upload_ss_frame.grid_rowconfigure(1, weight=1)

    # create scrolled window
    upload_ss_info = scrolledtextwidget.ScrolledText(
        upload_ss_frame,
        height=1,
        width=1,
        state=DISABLED,
        bd=4,
        wrap=WORD,
        bg=custom_scrolled_text_widget_color["background"],
        fg=custom_scrolled_text_widget_color["foreground"],
    )
    upload_ss_info.grid(
        row=0, column=0, columnspan=3, pady=(2, 0), padx=5, sticky=E + W + N + S
    )

    # create 'OK' button
    ss_okay_btn = HoverButton(
        upload_ss_frame,
        text="OK",
        command=upload_ss_exit_func,
        borderwidth="3",
        width=8,
        foreground=custom_button_colors["foreground"],
        background=custom_button_colors["background"],
        activeforeground=custom_button_colors["activeforeground"],
        activebackground=custom_button_colors["activebackground"],
        disabledforeground=custom_button_colors["disabledforeground"],
    )
    ss_okay_btn.grid(row=1, column=2, padx=7, pady=5, sticky=E)

    # ensure error is set to False
    upload_error.set(False)

    # if user and pass bin exists
    if (
        pathlib.Path("runtime/user.bin").is_file()
        and pathlib.Path("runtime/pass.bin").is_file()
    ):
        # start fernet instance to convert stored username and password files
        pass_user_decoder = Fernet(crypto_key)

        # open both user and pass bin files
        with open("runtime/user.bin", "rb") as user_file, open(
            "runtime/pass.bin", "rb"
        ) as pass_file:
            # decode and insert user name
            decode_user = pass_user_decoder.decrypt(user_file.read()).decode("utf-8")
            # decode and insert password
            decode_pass = pass_user_decoder.decrypt(pass_file.read()).decode("utf-8")

        # if username or password equals nothing send error
        if decode_user == "" or decode_pass == "":
            missing_info = messagebox.askyesno(
                parent=upload_ss_status,
                title="Missing credentials",
                message="Missing user name and password for beyondhd.co\n\nWould "
                "you like to add these now?",
            )
            # if user selects yes
            if missing_info:
                # open login window
                bhd_co_login_window()
                # update login variables
                pass_user_decoder = Fernet(crypto_key)
                with open("runtime/user.bin", "rb") as user_file, open(
                    "runtime/pass.bin", "rb"
                ) as pass_file:
                    decode_user = pass_user_decoder.decrypt(user_file.read()).decode(
                        "utf-8"
                    )
                    decode_pass = pass_user_decoder.decrypt(pass_file.read()).decode(
                        "utf-8"
                    )
            else:  # if user selects no
                manipulate_ss_upload_window(
                    "Missing username and/or password. Cannot continue..."
                )
                return  # exit function
    else:  # if user or path bins do not exist
        missing_info = messagebox.askyesno(
            parent=upload_ss_status,
            title="Missing credentials",
            message="Missing user name and password for beyondhd.co\n\nWould you "
            "like to add these now?",
        )
        # if user selects yes
        if missing_info:
            # open login window
            bhd_co_login_window()
            # update login variables
            pass_user_decoder = Fernet(crypto_key)
            with open("runtime/user.bin", "rb") as user_file, open(
                "runtime/pass.bin", "rb"
            ) as pass_file:
                decode_user = pass_user_decoder.decrypt(user_file.read()).decode(
                    "utf-8"
                )
                decode_pass = pass_user_decoder.decrypt(pass_file.read()).decode(
                    "utf-8"
                )
        else:  # if user selects no
            manipulate_ss_upload_window(
                "Missing username and/or password. Cannot continue..."
            )
            return  # exit function

    def beyond_hd_co_queue_loop():
        """constantly check the bhdco queue data for updates"""

        # if there is data set it to a variable
        try:
            bhd_co_data = upload_to_bhdco_queue.get_nowait()
        except Empty:
            bhd_co_data = None

        # if data is not equal to None
        if bhd_co_data is not None:
            # if the data is anything other than "Completed!"
            if str(bhd_co_data) != "Completed!":
                # send task_done to queue
                upload_to_bhdco_queue.task_done()

                # update screenshot status window
                manipulate_ss_upload_window(bhd_co_data)

            # if queue is "Completed!" exit the loop
            elif str(bhd_co_data) == "Completed!":
                # send task_done to queue
                upload_to_bhdco_queue.task_done()

                # exit the queue
                upload_to_bhdco_queue.join()

                # exit the loop
                return

        # keep polling loop going
        root.after(1, beyond_hd_co_queue_loop)

    # define upload in another thread
    bhdco_thread = threading.Thread(
        target=upload_to_beyond_hd_co, args=(upload_to_bhdco_queue,), daemon=True
    )

    # start thread polling loop
    root.after(500, beyond_hd_co_queue_loop)

    # start thread
    bhdco_thread.start()


# upload button
upload_ss_button = HoverButton(
    image_btn_frame,
    text="Upload IMGs",
    state=DISABLED,
    command=upload_to_beyond_hd_co_window,
    borderwidth="3",
    width=12,
    foreground=custom_button_colors["foreground"],
    background=custom_button_colors["background"],
    activeforeground=custom_button_colors["activeforeground"],
    activebackground=custom_button_colors["activebackground"],
    disabledforeground=custom_button_colors["disabledforeground"],
)
upload_ss_button.grid(row=1, column=1, rowspan=2, padx=5, pady=(7, 7), sticky=S + E)

# screen shot url tab
url_tab = Frame(tabs, bg=custom_frame_bg_colors["specialbg"])
tabs.add(url_tab, text=" URLs ")
url_tab.grid_rowconfigure(0, weight=1)
url_tab.grid_columnconfigure(0, weight=20)
url_tab.grid_columnconfigure(1, weight=20)
url_tab.grid_columnconfigure(2, weight=20)
url_tab.grid_columnconfigure(3, weight=1)

# screenshot textbox
screenshot_scrolledtext = scrolledtextwidget.ScrolledText(
    url_tab,
    height=6,
    bg=custom_scrolled_text_widget_color["background"],
    fg=custom_scrolled_text_widget_color["foreground"],
    bd=4,
)
screenshot_scrolledtext.grid(
    row=0, column=0, columnspan=3, pady=(6, 6), padx=4, sticky=E + W
)

# clear screenshot box
reset_screenshot_box = HoverButton(
    url_tab,
    text="X",
    command=lambda: screenshot_scrolledtext.delete("1.0", END),
    borderwidth="3",
    width=4,
    foreground=custom_button_colors["foreground"],
    background=custom_button_colors["background"],
    activeforeground=custom_button_colors["activeforeground"],
    activebackground=custom_button_colors["activebackground"],
    disabledforeground=custom_button_colors["disabledforeground"],
)
reset_screenshot_box.grid(
    row=0, column=3, columnspan=1, padx=5, pady=18, sticky=N + E + W
)


def popup_auto_e_b_menu(e):  # Function for mouse button 3 (right click) to pop up menu
    screen_shot_right_click_menu.tk_popup(
        e.x_root, e.y_root
    )  # This gets the position of 'e'


# pop up menu to enable/disable manual edits in release notes
screen_shot_right_click_menu = Menu(
    release_notes_scrolled,
    tearoff=False,
    font=(set_font, set_font_size + 1),
    background=custom_button_colors["background"],
    foreground=custom_button_colors["foreground"],
    activebackground=custom_button_colors["activebackground"],
    activeforeground=custom_button_colors["activeforeground"],
)  # Right click menu


# right click menu cut
def text_cut():
    if screenshot_scrolledtext.selection_get():
        # Grab selected text from text box
        selected_text_cut = screenshot_scrolledtext.selection_get()
        # Delete Selected Text from text box
        screenshot_scrolledtext.delete("sel.first", "sel.last")
        # Clear the clipboard then append
        screenshot_scrolledtext.clipboard_clear()
        screenshot_scrolledtext.clipboard_append(selected_text_cut)


screen_shot_right_click_menu.add_command(label="Cut", command=text_cut)


# right click menu copy
def text_copy():
    if screenshot_scrolledtext.selection_get():
        # Grab selected text from text box
        selected_text_copy = screenshot_scrolledtext.selection_get()
        # Clear the clipboard then append
        screenshot_scrolledtext.clipboard_clear()
        screenshot_scrolledtext.clipboard_append(selected_text_copy)


screen_shot_right_click_menu.add_command(label="Copy", command=text_copy)


# right click menu paste
def text_paste():
    screenshot_scrolledtext.delete("1.0", END)
    screenshot_scrolledtext.insert(END, screenshot_scrolledtext.clipboard_get())


screen_shot_right_click_menu.add_command(label="Paste", command=text_paste)


# right click menu clear
def text_delete():
    screenshot_scrolledtext.delete("1.0", END)


screen_shot_right_click_menu.add_command(label="Clear", command=text_delete)

screenshot_scrolledtext.bind(
    "<Button-3>", popup_auto_e_b_menu
)  # Uses mouse button 3 (right click) to open


# check/return screenshots
def parse_screen_shots():
    # if screenshot textbox is not empty
    if screenshot_scrolledtext.compare("end-1c", "!=", "1.0"):
        new_screenshots = screenshot_scrolledtext.get(1.0, END).split("[/url]")
        fresh_list = [str(i).strip() for i in new_screenshots]
        if "" in fresh_list:
            fresh_list.remove("")

        if int(len(fresh_list)) % 2 == 0:
            sorted_screenshots = ""
            iterate_list = iter(fresh_list)
            for x in iterate_list:
                sorted_screenshots += x + "[/url]"
                sorted_screenshots += "  "
                sorted_screenshots += str(next(iterate_list)) + "[/url]"
                sorted_screenshots += "\n"
                sorted_screenshots += "\n"
            return sorted_screenshots
        else:
            return False


# manual workflow frame
manual_workflow = LabelFrame(
    root,
    text=" Manual Workflow ",
    labelanchor="nw",
    bd=3,
    font=(set_font, set_font_size + 1, "bold"),
    fg=custom_label_frame_colors["foreground"],
    bg=custom_label_frame_colors["background"],
)
manual_workflow.grid(column=0, row=4, columnspan=2, padx=5, pady=(5, 3), sticky=W)

manual_workflow.grid_rowconfigure(0, weight=1)
manual_workflow.grid_columnconfigure(0, weight=1)
manual_workflow.grid_columnconfigure(1, weight=1)
manual_workflow.grid_columnconfigure(2, weight=1)


# generate nfo
def open_nfo_viewer():
    global nfo_pad, nfo_pad_text_box, nfo

    # nfo pad parser
    nfo_pad_parser = ConfigParser()
    nfo_pad_parser.read(config_file)

    if not pathlib.Path(source_file_path.get()).is_file():
        messagebox.showerror(
            parent=root, title="Error!", message="Source file is missing!"
        )
        return
    if not pathlib.Path(encode_file_path.get()).is_file():
        messagebox.showerror(
            parent=root, title="Error!", message="Encode file is missing!"
        )
        return
    parse_screenshots = parse_screen_shots()
    if not parse_screenshots:
        messagebox.showerror(
            parent=root,
            title="Error!",
            message="Missing or incorrectly formatted screenshots\n\n"
            "Screen shots need to be in multiples of 2",
        )
        return

    # nfo formatter
    def run_nfo_formatter():
        # noinspection SpellCheckingInspection
        nfo_b64 = """
        W2NvbG9yPSNmNWM3MGFdUkVMRUFTRSBJTkZPWy9jb2xvcl0KClNvdXJjZSAgICAgICAgICAgICAgICAgIDoge2JsdXJheV9zb3VyY2V9IChUaG
        Fua3MhKQpDaGFwdGVycyAgICAgICAgICAgICAgICA6IHtjaGFwdGVyX3R5cGV9CkZpbGUgU2l6ZSAgICAgICAgICAgICAgIDoge2VuY29kZV9ma
        WxlX3NpemV9CkR1cmF0aW9uICAgICAgICAgICAgICAgIDoge2VuY29kZV9maWxlX2R1cmF0aW9ufQpWaWRlbyAgICAgICAgICAgICAgICAgICA6
        IHtjb250YWluZXJfZm9ybWF0fSB7dl9jb2RlY30gVmlkZW8gLyB7dl9iaXRyYXRlfSBrYnBzIC8ge3ZfZnBzfSAvIHt2X2Zvcm1hdF9wcm9maWx
        lfQpSZXNvbHV0aW9uICAgICAgICAgICAgICA6IHt2X3dpZHRofSB4IHt2X2hlaWdodH0gKHt2X2FzcGVjdF9yYXRpb30pCkF1ZGlvICAgICAgIC
        AgICAgICAgICAgIDoge2FfbG5nfSAvIHthX2NvbW1lcmNpYWx9IEF1ZGlvIC8ge2FfY2hubF9zfSAvIHthX2ZyZXF9IC8ge2FfYml0cmF0ZX0ga
        2JwcyB7b3B0aW9uYWxfc3ViX3N0cmluZ30KRW5jb2RlciAgICAgICAgICAgICAgICAgOiBbY29sb3I9I2Y1YzcwYV17ZW5jb2RlZF9ieX1bL2Nv
        bG9yXQoKW2NvbG9yPSNmNWM3MGFdUkVMRUFTRSBOT1RFU1svY29sb3JdCgp7bmZvX3JlbGVhc2Vfbm90ZXN9CgpbY29sb3I9I2Y1YzcwYV1TQ1J
        FRU5TSE9UU1svY29sb3JdCltjZW50ZXJdCltjb2xvcj0jZjVjNzBhXVNPVVJDRVsvY29sb3JdPDw8PDw8PDw8PDw8PDw8PDwtLS0tLS0tLS0tLS
        0tLS0tLS0tW2NvbG9yPSNmNWM3MGFdVlNbL2NvbG9yXS0tLS0tLS0tLS0tLS0tLS0tLS0+Pj4+Pj4+Pj4+Pj4+Pj4+Pltjb2xvcj0jZjVjNzBhX
        UVOQ09ERVsvY29sb3JdCntuZm9fc2NyZWVuX3Nob3RzfQpbL2NlbnRlcl0KW2NvbG9yPSNmNWM3MGFdR1JFRVRaWy9jb2xvcl0KCkFsbCB0aG9z
        ZSB3aG8gc3VwcG9ydCBvdXIgZ3JvdXAsIG91ciBlbmNvZGVycywgYW5kIG91ciBjb21tdW5pdHkuIAoKW2NvbG9yPSNmNWM3MGFdR1JPVVAgTk9
        URVNbL2NvbG9yXQoKRW5qb3khCgpXZSBhcmUgY3VycmVudGx5IGxvb2tpbmcgZm9yIG5vdGhpbmcgaW4gcGFydGljdWxhci4gSWYgeW91IGZlZW
        wgeW91IGhhdmUgc29tZXRoaW5nIHRvIG9mZmVyLCBjb250YWN0IHVzIQoKW2NlbnRlcl1baW1nXWh0dHBzOi8vYmV5b25kaGQuY28vaW1hZ2VzL
        zIwMjEvMDMvMzAvNjJiY2E4ZDU4N2I3MTczMTIxMDA4ODg3ZWJlMDVhNDIucG5nWy9pbWddWy9jZW50ZXJdCgo=
        """

        decoded_nfo = base64.b64decode(nfo_b64).decode("utf-8")

        # parse encoded file
        media_info_encode = MediaInfo.parse(pathlib.Path(encode_file_path.get()))
        encode_general_track = media_info_encode.general_tracks[0]
        encode_chapter = media_info_encode.menu_tracks[0].to_data()
        encode_video_track = media_info_encode.video_tracks[0]
        encode_audio_track = media_info_encode.audio_tracks[0]

        # bluray source
        bluray_source = pathlib.Path(source_file_path.get()).stem

        # chapter information
        try:
            # check for numbered chapters
            chapters_start_numbered = re.search(
                r"chapter\s*(\d+)", str(list(encode_chapter.values())), re.IGNORECASE
            ).group(1)
            chapters_end_numbered = re.search(
                r"chapter\s*(\d+)",
                str(list(reversed(encode_chapter.values()))),
                re.IGNORECASE,
            ).group(1)
            chapter_type = f'Numbered ({chapters_start_numbered.lstrip("0")}-{chapters_end_numbered.lstrip("0")})'

        # if chapters are not numbered assume Named (since we check for tagged chapters on dropped encode input)
        except AttributeError:
            chapter_type = "Named"

        # file size
        encode_file_size = encode_general_track.other_file_size[0]

        # duration
        encode_file_duration = encode_video_track.other_duration[0]

        # video container format
        container_format = encode_general_track.commercial_name

        # video codec
        v_codec = encode_video_track.commercial_name

        # video bitrate
        v_bitrate = round(
            (float(encode_video_track.stream_size) / 1000)
            / ((float(encode_video_track.duration) / 60000) * 0.0075)
            / 1000
        )

        # video fps
        v_fps = f"{encode_video_track.frame_rate} fps"

        # video format profile
        v_format_profile = ""
        if encode_video_track.format_profile == "High@L4.1":
            v_format_profile = "High Profile 4.1"
        elif encode_video_track.format_profile == "Main 10@L5.1@Main":
            hdr_type = str(encode_video_track.hdr_format_compatibility)
            if "HDR10+" in hdr_type:
                hdr_string = " / HDR10+"
            elif "HDR10" in hdr_type:
                hdr_string = " / HDR10"
            else:
                hdr_string = ""
            v_format_profile = f"Main 10 @ Level 5.1 @ Main / 4:2:0{hdr_string}"

        # video width
        v_width = encode_video_track.width

        # video height
        v_height = encode_video_track.height

        # video aspect ratio
        v_aspect_ratio = encode_video_track.other_display_aspect_ratio[0]

        # audio language
        a_lng = ""
        check_audio_language = encode_audio_track.other_language
        if check_audio_language:
            a_lng = encode_audio_track.other_language[0]
        if not check_audio_language:
            a_lng = "English"

        # audio commercial name
        a_commercial = encode_audio_track.commercial_name

        # audio channels
        if encode_audio_track.channel_s == 1:
            a_chnl_s = "1.0"
        elif encode_audio_track.channel_s == 2:
            a_chnl_s = "2.0"
        elif encode_audio_track.channel_s == 6:
            a_chnl_s = "5.1"
        else:
            a_chnl_s = encode_audio_track.channel_s

        # audio frequency
        a_freq = encode_audio_track.other_sampling_rate[0]

        # audio bitrate
        a_bitrate = (
            str(encode_audio_track.other_bit_rate[0]).replace("kb/s", "").strip()
        )

        # optional sub string
        optional_sub_string = ""
        if forced_subtitles_burned_var.get() == "on":
            optional_sub_string = "\nSubtitles               : English (Forced)"

        # encoder name
        encoded_by = ""
        encoder_sig = nfo_pad_parser["encoder_name"]["name"].strip()
        if encoder_sig == "":
            encoded_by = "Anonymous"
        elif encoder_sig != "":
            encoded_by = nfo_pad_parser["encoder_name"]["name"].strip()

        # release notes
        nfo_release_notes = release_notes_scrolled.get("1.0", END).strip()

        # screen shots
        nfo_screen_shots = parse_screenshots

        formatted_nfo = decoded_nfo.format(
            bluray_source=bluray_source,
            chapter_type=chapter_type,
            encode_file_size=encode_file_size,
            encode_file_duration=encode_file_duration,
            container_format=container_format,
            v_codec=v_codec,
            v_bitrate=v_bitrate,
            v_fps=v_fps,
            v_format_profile=v_format_profile,
            v_width=v_width,
            v_height=v_height,
            v_aspect_ratio=v_aspect_ratio,
            a_lng=a_lng,
            a_commercial=a_commercial,
            a_chnl_s=a_chnl_s,
            a_freq=a_freq,
            a_bitrate=a_bitrate,
            optional_sub_string=optional_sub_string,
            encoded_by=encoded_by,
            nfo_release_notes=nfo_release_notes,
            nfo_screen_shots=nfo_screen_shots,
        )
        return formatted_nfo

    try:  # if window is already opened
        if nfo_pad.winfo_exists():
            nfo = run_nfo_formatter()
            nfo_pad_text_box.delete("1.0", END)
            nfo_pad_text_box.insert(END, nfo)
            return
    except NameError:  # if window is not opened
        pass

    def nfo_pad_exit_function():
        # nfo pad exit parser
        nfo_pad_exit_parser = ConfigParser()
        nfo_pad_exit_parser.read(config_file)

        # save nfo pad position if different
        if nfo_pad.wm_state() == "normal":
            if (
                nfo_pad_exit_parser["save_window_locations"]["nfo_pad"]
                != nfo_pad.geometry()
            ):
                nfo_pad_exit_parser.set(
                    "save_window_locations", "nfo_pad", nfo_pad.geometry()
                )
                with open(config_file, "w") as nfo_configfile:
                    nfo_pad_exit_parser.write(nfo_configfile)

        # update nfo var
        nfo_info_var.set(nfo_pad_text_box.get("1.0", "end-1c"))

        if not automatic_workflow_boolean.get():
            nfo_pad.destroy()  # destroy nfo window
            open_all_toplevels()  # open all top levels that was open
            advanced_root_deiconify()  # re-open root
        if automatic_workflow_boolean.get():
            nfo_pad.destroy()  # destroy nfo window

    nfo_pad = Toplevel()
    nfo_pad.title("BHDStudioUploadTool - NFO Pad")
    nfo_pad.config(bg=custom_window_bg_color)
    if nfo_pad_parser["save_window_locations"]["nfo_pad"] != "":
        nfo_pad.geometry(nfo_pad_parser["save_window_locations"]["nfo_pad"])
    nfo_pad.protocol(
        "WM_DELETE_WINDOW",
        lambda: [automatic_workflow_boolean.set(False), nfo_pad_exit_function()],
    )

    nfo_pad.grid_columnconfigure(0, weight=1)
    nfo_pad.grid_columnconfigure(1, weight=1)
    nfo_pad.grid_rowconfigure(0, weight=1000)
    nfo_pad.grid_rowconfigure(1, weight=1)
    nfo_pad.grid_rowconfigure(2, weight=1)

    # Set variable for open file name
    global open_status_name
    open_status_name = False

    global selected
    selected = False

    # Create New File Function
    def new_file():
        # Delete previous text
        nfo_pad_text_box.delete("1.0", END)
        # Update status bars
        nfo_pad.title("New File - TextPad!")
        status_bar.config(text="New File")

        global open_status_name
        open_status_name = False

    # Open Files
    def open_file():
        # Delete previous text
        nfo_pad_text_box.delete("1.0", END)

        # define parser
        nfo_dir_parser = ConfigParser()
        nfo_dir_parser.read(config_file)

        # check if last used folder exists
        if pathlib.Path(nfo_dir_parser["last_used_folder"]["path"]).is_dir():
            nfo_initial_dir = pathlib.Path(nfo_dir_parser["last_used_folder"]["path"])
        else:
            nfo_initial_dir = "/"

        # Grab Filename
        text_file = filedialog.askopenfilename(
            parent=nfo_pad,
            initialdir=nfo_initial_dir,
            title="Open File",
            filetypes=[("Text Files, NFO Files", ".txt .nfo")],
        )

        # Check to see if there is a file name
        if text_file:
            # Make filename global so we can access it later
            global open_status_name
            open_status_name = text_file

        # Update Status bars
        name = text_file
        status_bar.config(text=f"{name}")
        nfo_pad.title(f"{name} - NFO Pad!")

        # Open the file
        text_file = open(text_file, "r")
        stuff = text_file.read()
        # Add file to textbox
        nfo_pad_text_box.insert(END, stuff)
        # Close the opened file
        text_file.close()

    # save as file
    def nfo_pad_save():
        # define parser
        nfo_save_parser = ConfigParser()
        nfo_save_parser.read(config_file)

        # check if last used folder exists
        if pathlib.Path(nfo_save_parser["last_used_folder"]["path"]).is_dir():
            nfo_save_initial_dir = pathlib.Path(
                nfo_save_parser["last_used_folder"]["path"]
            )
        else:
            nfo_save_initial_dir = "/"

        # get save output
        text_file = filedialog.asksaveasfilename(
            parent=nfo_pad,
            defaultextension=".nfo",
            initialdir=nfo_save_initial_dir,
            title="Save File",
            filetypes=[("NFO File", "*.nfo")],
        )
        if text_file:
            # update status bars
            name = text_file
            status_bar.config(text=f"Saved: {name}")
            nfo_pad.title(f"{name} - NFO Pad")

            # save the file
            text_file = open(text_file, "w")
            text_file.write(nfo_pad_text_box.get("1.0", "end-1c"))

            # Close the file
            text_file.close()
            nfo_pad_exit_function()

    # Cut Text
    def cut_text(e):
        global selected
        # Check to see if keyboard shortcut used
        if e:
            selected = nfo_pad.clipboard_get()
        else:
            if nfo_pad_text_box.selection_get():
                # Grab selected text from text box
                selected = nfo_pad_text_box.selection_get()
                # Delete Selected Text from text box
                nfo_pad_text_box.delete("sel.first", "sel.last")
                # Clear the clipboard then append
                nfo_pad.clipboard_clear()
                nfo_pad.clipboard_append(selected)

    # Copy Text
    def copy_text(e):
        global selected
        # check to see if we used keyboard shortcuts
        if e:
            selected = nfo_pad.clipboard_get()

        if nfo_pad_text_box.selection_get():
            # Grab selected text from text box
            selected = nfo_pad_text_box.selection_get()
            # Clear the clipboard then append
            nfo_pad.clipboard_clear()
            nfo_pad.clipboard_append(selected)

    # Paste Text
    def paste_text(e):
        global selected
        # Check to see if keyboard shortcut used
        if e:
            selected = nfo_pad.clipboard_get()
        else:
            if selected:
                position = nfo_pad_text_box.index(INSERT)
                nfo_pad_text_box.insert(position, str(selected))

    # change bg color
    def bg_color():
        my_color = colorchooser.askcolor(parent=nfo_pad)[1]
        if my_color:
            nfo_pad_text_box.config(bg=my_color)

            # save scheme to config
            bg_parser = ConfigParser()
            bg_parser.read(config_file)
            bg_parser.set("nfo_pad_color_settings", "background", my_color)
            with open(config_file, "w") as bg_config:
                bg_parser.write(bg_config)

    # change all text color
    def all_text_color():
        my_color = colorchooser.askcolor(parent=nfo_pad)[1]
        if my_color:
            nfo_pad_text_box.config(fg=my_color)

            # save scheme to config
            txt_parser = ConfigParser()
            txt_parser.read(config_file)
            txt_parser.set("nfo_pad_color_settings", "text", my_color)
            with open(config_file, "w") as bg_config:
                txt_parser.write(bg_config)

    # select all text
    def select_all(e):
        # Add sel tag to select all text
        nfo_pad_text_box.tag_add("sel", "1.0", "end")

    # clear all text
    def clear_all():
        nfo_pad_text_box.delete(1.0, END)

    # fixed font chooser
    fixed_font_chooser_opened = BooleanVar()

    # reset nfo pad color scheme
    def reset_colors():
        # define parser and clear
        nfo_reset_parser = ConfigParser()
        nfo_reset_parser.read(config_file)
        nfo_reset_parser.set("nfo_pad_color_settings", "background", "")
        nfo_reset_parser.set("nfo_pad_color_settings", "text", "")
        with open(config_file, "w") as nfo_cf_reset:
            nfo_reset_parser.write(nfo_cf_reset)

        # set default colors
        nfo_pad_text_box.config(bg="#c0c0c0", fg="black")

    def fixed_font_chooser(*e):
        # check if window is already opened
        if fixed_font_chooser_opened.get():
            return  # if opened exit the function
        else:  # if not opened set to opened
            fixed_font_chooser_opened.set(True)

        # font parser
        font_parser = ConfigParser()
        font_parser.read(config_file)

        font_chooser_win = Toplevel()
        font_chooser_win.title("BHDStudio Upload Tool - Font")
        font_chooser_win.configure(background=custom_window_bg_color)
        font_chooser_win.geometry(
            f'{700}x{320}+{str(int(nfo_pad.geometry().split("+")[1]) + 108)}+'
            f'{str(int(nfo_pad.geometry().split("+")[2]) + 80)}'
        )
        font_chooser_win.grab_set()  # grab set

        font_chooser_win.rowconfigure(0, weight=1)
        font_chooser_win.rowconfigure(1, weight=60)
        font_chooser_win.rowconfigure(2, weight=1)
        font_chooser_win.rowconfigure(3, weight=1)
        font_chooser_win.columnconfigure(0, weight=1)
        font_chooser_win.columnconfigure(1, weight=1)

        # start font instance
        font_instance = font.Font()
        available_fonts = font.families()

        # create a list of fixed fonts only
        mono_spaced_fonts = []
        for fonts in available_fonts:
            get_fixed_fonts = font.Font(family=fonts)
            if get_fixed_fonts.metrics("fixed"):
                mono_spaced_fonts.append(fonts)

        # some needed font variables
        default_font_size = font_instance.actual().get("size")  # get default font size
        define_font_type = font.nametofont(
            "TkFixedFont"
        )  # get default font value into Font object
        default_font_name = define_font_type.actual().get("family")  # get font name
        # default_style = font_instance.cget("weight")  # get weight as a variable

        # get index of default mono font name
        if font_parser["nfo_pad_font_settings"]["font"].strip() != "":
            get_font_index = mono_spaced_fonts.index(
                font_parser["nfo_pad_font_settings"]["font"].strip()
            )
        else:
            get_font_index = mono_spaced_fonts.index(default_font_name)

        # fonts frame
        fonts_frame = LabelFrame(
            font_chooser_win,
            text=" Fonts ",
            labelanchor="nw",
            bd=3,
            font=(set_font, set_font_size + 1, "bold"),
            fg=custom_label_frame_colors["foreground"],
            bg=custom_label_frame_colors["background"],
        )
        fonts_frame.grid(
            column=0, row=0, rowspan=3, pady=5, padx=5, sticky=W + E + N + S
        )
        fonts_frame.grid_columnconfigure(0, weight=1)
        for f_f in range(3):
            fonts_frame.grid_rowconfigure(f_f, weight=1)

        # fonts listbox
        fonts_right_scrollbar = Scrollbar(fonts_frame, orient=VERTICAL)  # scrollbar
        fonts_listbox = Listbox(
            fonts_frame,
            exportselection=False,
            yscrollcommand=fonts_right_scrollbar.set,
            selectmode=SINGLE,
            bd=2,
            activestyle="none",
            width=20,
            height=12,
            bg=custom_listbox_color["background"],
            fg=custom_listbox_color["foreground"],
            selectbackground=custom_listbox_color["selectbackground"],
            selectforeground=custom_listbox_color["selectforeground"],
        )
        fonts_listbox.grid(row=0, column=0, rowspan=3, sticky=N + E + S + W)
        fonts_right_scrollbar.config(command=fonts_listbox.yview)
        fonts_right_scrollbar.grid(row=0, column=1, rowspan=3, sticky=N + W + S)

        # add fixed fonts to list box
        for fixed_fonts in mono_spaced_fonts:
            fonts_listbox.insert(END, fixed_fonts)

        # select current default font
        fonts_listbox.selection_set(get_font_index)

        # fonts frame
        style_frame = LabelFrame(
            font_chooser_win,
            text=" Style ",
            labelanchor="nw",
            bd=3,
            font=(set_font, set_font_size + 1, "bold"),
            fg=custom_label_frame_colors["foreground"],
            bg=custom_label_frame_colors["background"],
        )
        style_frame.grid(column=1, row=0, pady=5, padx=5, sticky=E + W + N)
        style_frame.grid_columnconfigure(0, weight=1)
        style_frame.grid_rowconfigure(0, weight=1)

        # style combo box
        style_combo_box = ttk.Combobox(
            style_frame,
            values=["Normal", "Bold", "Italic", "Roman", "Underline", "Overstrike"],
            state="readonly",
        )
        style_combo_box.grid(column=0, row=0, padx=2, pady=2, sticky=E + W)

        # set weight
        if font_parser["nfo_pad_font_settings"]["style"].strip() != "":
            style_combo_box.set(font_parser["nfo_pad_font_settings"]["style"].strip())
        else:
            style_combo_box.set("Normal")

        # set size list
        values_list = []
        for x in range(8, 74, 2):
            values_list.append(x)

        # fonts frame
        size_frame = LabelFrame(
            font_chooser_win,
            text=" Size ",
            labelanchor="nw",
            bd=3,
            font=(set_font, set_font_size + 1, "bold"),
            fg=custom_label_frame_colors["foreground"],
            bg=custom_label_frame_colors["background"],
        )
        size_frame.grid(column=1, row=1, pady=5, padx=5, sticky=E + W + N)
        size_frame.grid_columnconfigure(0, weight=1)
        size_frame.grid_rowconfigure(0, weight=1)

        # size combo box
        size_combo_box = ttk.Combobox(size_frame, values=values_list)
        size_combo_box.grid(column=0, row=0, padx=2, pady=2, sticky=E + W)

        # set size
        if font_parser["nfo_pad_font_settings"]["size"].strip() != "":
            size_combo_box.set(nfo_pad_parser["nfo_pad_font_settings"]["size"].strip())
        else:
            size_combo_box.set(default_font_size)

        # sample label
        sample_label = Label(
            font_chooser_win,
            text="Aa",
            background=custom_label_colors["background"],
            fg=custom_label_colors["foreground"],
        )
        sample_label.grid(column=1, row=2, pady=5, padx=5, sticky=E + W + N + S)

        # constant loop to update the sample label
        def sample_label_loop():
            sample_label.config(
                font=(
                    mono_spaced_fonts[fonts_listbox.curselection()[0]],
                    size_combo_box.get(),
                    str(style_combo_box.get()).lower(),
                )
            )
            font_chooser_win.after(30, sample_label_loop)

        # start sample label loop
        sample_label_loop()

        # font chooser button frame
        font_button_frame = Frame(
            font_chooser_win, bg=custom_frame_bg_colors["background"], bd=0
        )
        font_button_frame.grid(
            column=0, row=3, columnspan=2, padx=5, pady=(5, 3), sticky=E + W
        )
        font_button_frame.grid_rowconfigure(0, weight=1)
        font_button_frame.grid_columnconfigure(0, weight=1)
        font_button_frame.grid_columnconfigure(1, weight=60)
        font_button_frame.grid_columnconfigure(2, weight=1)

        # reset command
        def reset_font_to_default():
            # define parser
            nfo_reset_parser = ConfigParser()
            nfo_reset_parser.read(config_file)

            # define settings
            nfo_reset_parser.set("nfo_pad_font_settings", "font", "")
            nfo_reset_parser.set("nfo_pad_font_settings", "style", "")
            nfo_reset_parser.set("nfo_pad_font_settings", "size", "")
            with open(config_file, "w") as font_configfile_reset:
                nfo_reset_parser.write(font_configfile_reset)

            # apply settings to nfo pad
            nfo_pad_text_box.config(font=(set_fixed_font, set_font_size + 1))

            # reset all the selections in the font chooser window
            fonts_listbox.selection_clear(0, END)  # clear selection
            fonts_listbox.selection_set(
                mono_spaced_fonts.index(default_font_name)
            )  # set default value
            style_combo_box.set("Normal")  # set default value
            size_combo_box.set(default_font_size)  # set default value

        # once function is exited set starting boolean to false
        fixed_font_chooser_opened.set(False)

        # reset button
        font_reset_button = HoverButton(
            font_button_frame,
            text="Reset",
            command=reset_font_to_default,
            borderwidth="3",
            width=8,
            foreground=custom_button_colors["foreground"],
            background=custom_button_colors["background"],
            activeforeground=custom_button_colors["activeforeground"],
            activebackground=custom_button_colors["activebackground"],
            disabledforeground=custom_button_colors["disabledforeground"],
        )
        font_reset_button.grid(row=0, column=0, columnspan=1, padx=3, pady=5, sticky=W)

        # cancel button
        font_cancel_button = HoverButton(
            font_button_frame,
            text="Close",
            command=font_chooser_win.destroy,
            borderwidth="3",
            width=8,
            foreground=custom_button_colors["foreground"],
            background=custom_button_colors["background"],
            activeforeground=custom_button_colors["activeforeground"],
            activebackground=custom_button_colors["activebackground"],
            disabledforeground=custom_button_colors["disabledforeground"],
        )
        font_cancel_button.grid(row=0, column=1, columnspan=1, padx=3, pady=5, sticky=E)

        # change the font for the nfo pad
        def apply_command():
            # define parser
            nfo_apply_parser = ConfigParser()
            nfo_apply_parser.read(config_file)

            # define settings
            nfo_apply_parser.set(
                "nfo_pad_font_settings",
                "font",
                mono_spaced_fonts[fonts_listbox.curselection()[0]],
            )
            nfo_apply_parser.set(
                "nfo_pad_font_settings", "size", str(size_combo_box.get())
            )
            nfo_apply_parser.set(
                "nfo_pad_font_settings", "style", str(style_combo_box.get())
            )
            with open(config_file, "w") as font_configfile_apply:
                nfo_apply_parser.write(font_configfile_apply)

            # apply settings to nfo pad
            nfo_pad_text_box.config(
                font=(
                    mono_spaced_fonts[fonts_listbox.curselection()[0]],
                    size_combo_box.get(),
                    str(style_combo_box.get()).lower(),
                )
            )

        # apply button
        font_apply_button = HoverButton(
            font_button_frame,
            text="Apply",
            command=apply_command,
            borderwidth="3",
            width=8,
            foreground=custom_button_colors["foreground"],
            background=custom_button_colors["background"],
            activeforeground=custom_button_colors["activeforeground"],
            activebackground=custom_button_colors["activebackground"],
            disabledforeground=custom_button_colors["disabledforeground"],
        )
        font_apply_button.grid(row=0, column=2, columnspan=1, padx=3, pady=5, sticky=E)

    # create main frame
    nfo_frame = Frame(nfo_pad, bg=custom_frame_bg_colors["background"])
    nfo_frame.grid(
        column=0, columnspan=2, row=0, pady=(5, 0), padx=5, sticky=N + S + E + W
    )
    nfo_frame.grid_columnconfigure(0, weight=1)
    nfo_frame.grid_rowconfigure(0, weight=1)

    # scroll bars
    right_scrollbar = Scrollbar(nfo_frame, orient=VERTICAL)  # scrollbars
    bottom_scrollbar = Scrollbar(nfo_frame, orient=HORIZONTAL)

    # create text box
    nfo_pad_text_box = Text(
        nfo_frame,
        undo=True,
        yscrollcommand=right_scrollbar.set,
        wrap="none",
        xscrollcommand=bottom_scrollbar.set,
        background="#c0c0c0",
        font=(set_fixed_font, set_font_size + 1),
    )
    nfo_pad_text_box.grid(column=0, row=0, sticky=N + S + E + W)

    if nfo_pad_parser["nfo_pad_color_settings"]["background"] != "":
        nfo_pad_text_box.config(
            bg=nfo_pad_parser["nfo_pad_color_settings"]["background"]
        )
    if nfo_pad_parser["nfo_pad_color_settings"]["text"] != "":
        nfo_pad_text_box.config(fg=nfo_pad_parser["nfo_pad_color_settings"]["text"])

    # add scrollbars to the textbox
    right_scrollbar.config(command=nfo_pad_text_box.yview)
    right_scrollbar.grid(row=0, column=1, sticky=N + W + S)
    bottom_scrollbar.config(command=nfo_pad_text_box.xview)
    bottom_scrollbar.grid(row=1, column=0, sticky=W + E + N)

    # define starting font
    if (
        nfo_pad_parser["nfo_pad_font_settings"]["font"].strip() != ""
        and nfo_pad_parser["nfo_pad_font_settings"]["style"].strip() != ""
        and nfo_pad_parser["nfo_pad_font_settings"]["size"].strip() != ""
    ):
        nfo_pad_text_box.config(
            font=(
                nfo_pad_parser["nfo_pad_font_settings"]["font"].strip(),
                int(nfo_pad_parser["nfo_pad_font_settings"]["size"].strip()),
                nfo_pad_parser["nfo_pad_font_settings"]["style"].strip().lower(),
            )
        )

    # Create Menu
    nfo_main_menu = Menu(nfo_pad)
    nfo_pad.config(menu=nfo_main_menu)

    # Add File Menu
    nfo_menu = Menu(nfo_main_menu, tearoff=False)
    nfo_main_menu.add_cascade(label="File", menu=nfo_menu)
    nfo_menu.add_command(label="New", command=new_file)
    nfo_menu.add_command(label="Open", command=open_file)
    nfo_menu.add_command(label="Save", command=nfo_pad_save)
    nfo_menu.add_command(label="Save Internally", command=nfo_pad_exit_function)
    nfo_menu.add_separator()
    nfo_menu.add_command(
        label="Exit",
        command=lambda: [
            automatic_workflow_boolean.set(False),
            nfo_pad_exit_function(),
        ],
    )

    # Add Edit Menu
    edit_menu = Menu(nfo_main_menu, tearoff=False)
    nfo_main_menu.add_cascade(label="Edit", menu=edit_menu)
    edit_menu.add_command(
        label="Cut", command=lambda: cut_text(False), accelerator="(Ctrl+x)"
    )
    edit_menu.add_command(
        label="Copy", command=lambda: copy_text(False), accelerator="(Ctrl+c)"
    )
    edit_menu.add_command(
        label="Paste             ",
        command=lambda: paste_text(False),
        accelerator="(Ctrl+v)",
    )
    edit_menu.add_separator()
    edit_menu.add_command(
        label="Undo", command=nfo_pad_text_box.edit_undo, accelerator="(Ctrl+z)"
    )
    edit_menu.add_command(
        label="Redo", command=nfo_pad_text_box.edit_redo, accelerator="(Ctrl+y)"
    )
    edit_menu.add_separator()
    edit_menu.add_command(
        label="Select All", command=lambda: select_all(True), accelerator="(Ctrl+a)"
    )
    edit_menu.add_command(label="Clear", command=clear_all)

    # add options menu
    options_menu = Menu(nfo_main_menu, tearoff=False)
    nfo_main_menu.add_cascade(label="Options", menu=options_menu)
    options_menu.add_command(
        label="Font Settings", command=fixed_font_chooser, accelerator="(Ctrl+o)"
    )

    # Add Color Menu
    color_menu = Menu(nfo_main_menu, tearoff=False)
    nfo_main_menu.add_cascade(label="Colors", menu=color_menu)
    color_menu.add_command(label="Text Color", command=all_text_color)
    color_menu.add_command(label="Background", command=bg_color)
    color_menu.add_separator()
    color_menu.add_command(label="Reset", command=reset_colors)

    # Add Status Bar To Bottom Of App
    status_bar = Label(
        nfo_pad,
        text="Ready",
        anchor=E,
        bg=custom_entry_colors["disabledbackground"],
        fg=custom_entry_colors["foreground"],
        relief=SUNKEN,
    )
    status_bar.grid(column=0, columnspan=2, row=2, pady=1, padx=1, sticky=E + W)

    # edit bindings
    nfo_pad.bind("<Control-Key-x>", cut_text)
    nfo_pad.bind("<Control-Key-c>", copy_text)
    nfo_pad.bind("<Control-Key-v>", paste_text)
    nfo_pad.bind("<Control-Key-o>", fixed_font_chooser)
    # select binding
    nfo_pad.bind("<Control-A>", select_all)
    nfo_pad.bind("<Control-a>", select_all)

    # format nfo via function
    nfo = run_nfo_formatter()

    # if information was not returned correctly
    if not nfo:
        return  # exit this function

    # delete any text (shouldn't be any)
    nfo_pad_text_box.delete("1.0", END)

    # insert new nfo
    nfo_pad_text_box.insert(END, nfo)

    # if program is in automatic workflow mode
    if automatic_workflow_boolean.get():
        workflow_frame = Frame(nfo_pad, bg=custom_frame_bg_colors["background"])
        workflow_frame.grid(
            row=1, column=0, columnspan=2, padx=0, pady=0, sticky=N + S + E + W
        )
        workflow_frame.grid_columnconfigure(0, weight=1)
        workflow_frame.grid_columnconfigure(1, weight=1)
        workflow_frame.grid_rowconfigure(0, weight=1)

        continue_button = HoverButton(
            workflow_frame,
            text="Continue",
            command=lambda: [
                automatic_workflow_boolean.set(True),
                nfo_pad_exit_function(),
            ],
            borderwidth="3",
            width=10,
            foreground=custom_button_colors["foreground"],
            background=custom_button_colors["background"],
            activeforeground=custom_button_colors["activeforeground"],
            activebackground=custom_button_colors["activebackground"],
            disabledforeground=custom_button_colors["disabledforeground"],
        )
        continue_button.grid(
            row=0, column=1, columnspan=1, padx=7, pady=(3, 0), sticky=N + S + E
        )

        cancel_workflow_button = HoverButton(
            workflow_frame,
            text="Cancel",
            width=10,
            command=lambda: [
                automatic_workflow_boolean.set(False),
                nfo_pad_exit_function(),
            ],
            borderwidth="3",
            foreground=custom_button_colors["foreground"],
            background=custom_button_colors["background"],
            activeforeground=custom_button_colors["activeforeground"],
            activebackground=custom_button_colors["activebackground"],
            disabledforeground=custom_button_colors["disabledforeground"],
        )
        cancel_workflow_button.grid(
            row=0, column=0, columnspan=1, padx=7, pady=(3, 0), sticky=N + S + W
        )
        status_bar.config(
            text="(Saving is optional)   Cancel / Closing NFO Pad will stop the automatic workflow  |  "
            "Click continue to proceed..."
        )
        nfo_pad.wait_window()


generate_nfo_button = HoverButton(
    manual_workflow,
    text="Generate NFO",
    command=open_nfo_viewer,
    borderwidth="3",
    width=15,
    foreground=custom_button_colors["foreground"],
    background=custom_button_colors["background"],
    activeforeground=custom_button_colors["activeforeground"],
    activebackground=custom_button_colors["activebackground"],
    disabledforeground=custom_button_colors["disabledforeground"],
)
generate_nfo_button.grid(row=0, column=1, columnspan=1, padx=5, pady=1, sticky=E + W)


# torrent creation ----------------------------------------------------------------------------------------------------
def torrent_function_window():
    # main torrent parser
    torrent_config = ConfigParser()
    torrent_config.read(config_file)

    # torrent window exit function
    def torrent_window_exit_function():
        # exit torrent parser
        torrent_parser = ConfigParser()
        torrent_parser.read(config_file)

        # save announce url if it's correct
        if "/announce" in torrent_tracker_url_entry_box.get().strip():
            torrent_parser.set(
                "torrent_settings",
                "tracker_url",
                torrent_tracker_url_entry_box.get().strip(),
            )
            with open(config_file, "w") as torrent_configfile:
                torrent_parser.write(torrent_configfile)

        # save torrent window position/geometry
        if torrent_window.wm_state() == "normal":
            if (
                torrent_parser["save_window_locations"]["torrent_window"]
                != torrent_window.geometry()
            ):
                torrent_parser.set(
                    "save_window_locations",
                    "torrent_window",
                    torrent_window.geometry(),
                )
                with open(config_file, "w") as torrent_configfile:
                    torrent_parser.write(torrent_configfile)

        if not automatic_workflow_boolean.get():
            torrent_window.destroy()  # destroy torrent window
            open_all_toplevels()  # open all top levels that was open
            advanced_root_deiconify()  # re-open root
        if automatic_workflow_boolean.get():
            torrent_window.destroy()  # destroy torrent window

    hide_all_toplevels()  # hide all top levels
    root.withdraw()  # hide root

    # create new toplevel window
    torrent_window = Toplevel()
    torrent_window.configure(background=custom_window_bg_color)
    torrent_window.title("BHDStudio Torrent Creator")
    if torrent_config["save_window_locations"]["torrent_window"] != "":
        torrent_window.geometry(
            torrent_config["save_window_locations"]["torrent_window"]
        )
    torrent_window.protocol(
        "WM_DELETE_WINDOW",
        lambda: [automatic_workflow_boolean.set(False), torrent_window_exit_function()],
    )

    # row and column configure
    for t_w in range(10):
        torrent_window.grid_columnconfigure(t_w, weight=1)
    for t_w in range(10):
        torrent_window.grid_rowconfigure(t_w, weight=1)

    # torrent path frame
    general_path_frame = LabelFrame(
        torrent_window,
        text=" Path ",
        labelanchor="nw",
        bd=3,
        font=(set_font, set_font_size, "bold"),
        fg=custom_label_frame_colors["foreground"],
        bg=custom_label_frame_colors["background"],
    )
    general_path_frame.grid(
        column=0, row=0, columnspan=10, padx=5, pady=(0, 3), sticky=E + W + N + S
    )

    general_path_frame.grid_rowconfigure(0, weight=1)
    for t_f in range(10):
        general_path_frame.grid_columnconfigure(t_f, weight=1)

    # re-define torrent output if the user wants
    def torrent_save_output():
        torrent_file_input = filedialog.asksaveasfilename(
            parent=root,
            title="Save Torrent",
            initialdir=pathlib.Path(torrent_file_path.get()).parent,
            initialfile=pathlib.Path(torrent_file_path.get()).name,
            filetypes=[("Torrent Files", "*.torrent")],
        )
        if torrent_file_input:
            torrent_entry_box.config(state=NORMAL)
            torrent_entry_box.delete(0, END)
            torrent_entry_box.insert(
                END, pathlib.Path(torrent_file_input).with_suffix(".torrent")
            )
            torrent_file_path.set(
                pathlib.Path(torrent_file_input).with_suffix(".torrent")
            )
            torrent_entry_box.config(state=DISABLED)
            return True
        if not torrent_file_input:
            return False

    # torrent set path button
    torrent_button = HoverButton(
        general_path_frame,
        text="Set",
        command=torrent_save_output,
        borderwidth="3",
        foreground=custom_button_colors["foreground"],
        background=custom_button_colors["background"],
        activeforeground=custom_button_colors["activeforeground"],
        activebackground=custom_button_colors["activebackground"],
        disabledforeground=custom_button_colors["disabledforeground"],
    )
    torrent_button.grid(
        row=0,
        column=0,
        columnspan=1,
        ipadx=5,
        padx=5,
        pady=(7, 5),
        sticky=N + S + E + W,
    )

    # torrent path entry box
    torrent_entry_box = Entry(
        general_path_frame,
        borderwidth=4,
        fg=custom_entry_colors["foreground"],
        bg=custom_entry_colors["background"],
        disabledforeground=custom_entry_colors["disabledforeground"],
        disabledbackground=custom_entry_colors["disabledbackground"],
        width=60,
        font=(set_fixed_font, set_font_size),
    )
    torrent_entry_box.grid(
        row=0, column=1, columnspan=9, padx=5, pady=(5, 5), sticky=N + S + E + W
    )
    torrent_entry_box.insert(END, pathlib.Path(torrent_file_path.get()))
    torrent_entry_box.config(state=DISABLED)

    # torrent piece frame
    torrent_piece_frame = LabelFrame(
        torrent_window,
        text=" Settings ",
        labelanchor="nw",
        bd=3,
        font=(set_font, set_font_size, "bold"),
        fg=custom_label_frame_colors["foreground"],
        bg=custom_label_frame_colors["background"],
    )
    torrent_piece_frame.grid(
        column=0, row=1, columnspan=10, padx=5, pady=(0, 3), sticky=E + W + N + S
    )

    torrent_piece_frame.grid_columnconfigure(0, weight=1)
    torrent_piece_frame.grid_columnconfigure(1, weight=200)
    torrent_piece_frame.grid_columnconfigure(2, weight=2000)
    torrent_piece_frame.grid_columnconfigure(3, weight=200000)
    torrent_piece_frame.grid_rowconfigure(0, weight=1)
    torrent_piece_frame.grid_rowconfigure(1, weight=1)

    # calculate piece size for 'piece_size_info_label2'
    def set_piece_size(*args):
        # get size of file with os.stat()
        file = float(os.stat(pathlib.Path(encode_file_path.get())).st_size)
        # if torrent is auto use torf.Torrent() to generate piece size
        if torrent_piece.get() == "Auto":
            calculate_pieces = math.ceil(
                file / float(Torrent.calculate_piece_size(file))
            )
        # if any other setting manually calculate it
        else:
            calculate_pieces = math.ceil(
                float(os.stat(pathlib.Path(encode_file_path.get())).st_size)
                / float(torrent_piece_choices[torrent_piece.get()])
            )

        # update label with piece size
        piece_size_label2.config(text=str(calculate_pieces))

    # piece size info label
    piece_size_info_label = Label(
        torrent_piece_frame,
        text="Piece Size:",
        bd=0,
        relief=SUNKEN,
        background=custom_label_colors["background"],
        fg=custom_label_colors["foreground"],
        font=(set_font, set_font_size + 1),
    )
    piece_size_info_label.grid(
        column=0, row=0, columnspan=1, pady=(5, 0), padx=(5, 0), sticky=W
    )

    # piece size menu
    torrent_piece_choices = {
        "Auto": None,
        "16 KiB": 16384,
        "32 KiB": 32768,
        "64 KiB": 65536,
        "128 KiB": 131072,
        "256 KiB": 262144,
        "512 KiB": 524288,
        "1 MiB": 1048576,
        "2 MiB": 2097152,
        "4 MiB": 4194304,
        "8 MiB": 8388608,
        "16 MiB": 16777216,
        "32 MiB": 33554432,
    }
    torrent_piece = StringVar()
    torrent_piece.set("Auto")
    torrent_piece_menu = OptionMenu(
        torrent_piece_frame,
        torrent_piece,
        *torrent_piece_choices.keys(),
        command=set_piece_size,
    )
    torrent_piece_menu.config(
        highlightthickness=1,
        width=7,
        activebackground=custom_button_colors["activebackground"],
        activeforeground=custom_button_colors["activeforeground"],
        background=custom_button_colors["background"],
        foreground=custom_button_colors["foreground"],
        font=(set_font, set_font_size - 1),
    )
    torrent_piece_menu.grid(
        row=0, column=1, columnspan=1, pady=(7, 5), padx=(10, 5), sticky=W
    )
    torrent_piece_menu["menu"].configure(
        activebackground=custom_button_colors["activebackground"],
        activeforeground=custom_button_colors["activeforeground"],
        background=custom_button_colors["background"],
        foreground=custom_button_colors["foreground"],
        font=(set_font, set_font_size - 2),
    )

    # piece size label
    piece_size_label = Label(
        torrent_piece_frame,
        text="Total Pieces:",
        bd=0,
        relief=SUNKEN,
        background=custom_label_colors["background"],
        fg=custom_label_colors["foreground"],
        font=(set_font, set_font_size + 1),
    )
    piece_size_label.grid(
        column=2, row=0, columnspan=1, pady=(5, 0), padx=(20, 0), sticky=W
    )

    # piece size label 2
    piece_size_label2 = Label(
        torrent_piece_frame,
        text="",
        bd=0,
        relief=SUNKEN,
        background=custom_label_colors["background"],
        fg=custom_label_colors["foreground"],
        font=(set_font, set_font_size),
    )
    piece_size_label2.grid(
        column=3, row=0, columnspan=1, pady=(7, 0), padx=(5, 5), sticky=W
    )

    # set piece size information
    set_piece_size()

    # torrent entry frame
    torrent_entry_frame = LabelFrame(
        torrent_window,
        text=" Fields ",
        labelanchor="nw",
        bd=3,
        font=(set_font, set_font_size, "bold"),
        fg=custom_label_frame_colors["foreground"],
        bg=custom_label_frame_colors["background"],
    )
    torrent_entry_frame.grid(
        column=0, row=2, columnspan=10, padx=5, pady=(0, 3), sticky=E + W + N + S
    )

    torrent_entry_frame.grid_columnconfigure(0, weight=1)
    torrent_entry_frame.grid_columnconfigure(1, weight=200)
    torrent_entry_frame.grid_columnconfigure(2, weight=2000)
    torrent_entry_frame.grid_columnconfigure(3, weight=200000)
    torrent_entry_frame.grid_rowconfigure(0, weight=1)
    torrent_entry_frame.grid_rowconfigure(1, weight=1)

    # tracker url label
    torrent_tracker_label = Label(
        torrent_entry_frame,
        text="Tracker URL:",
        bd=0,
        relief=SUNKEN,
        background=custom_label_colors["background"],
        fg=custom_label_colors["foreground"],
        font=(set_font, set_font_size),
    )
    torrent_tracker_label.grid(
        row=0, column=0, columnspan=1, pady=(5, 0), padx=(5, 0), sticky=W
    )

    # tracker url entry box
    torrent_tracker_url_entry_box = Entry(
        torrent_entry_frame,
        borderwidth=4,
        show="*",
        fg=custom_entry_colors["foreground"],
        bg=custom_entry_colors["background"],
        disabledforeground=custom_entry_colors["disabledforeground"],
        disabledbackground=custom_entry_colors["disabledbackground"],
        font=(set_fixed_font, set_font_size),
    )
    torrent_tracker_url_entry_box.grid(
        row=0, column=1, columnspan=7, padx=(2, 5), pady=(5, 0), sticky=N + S + E + W
    )
    torrent_tracker_url_entry_box.bind(
        "<Enter>", lambda event: torrent_tracker_url_entry_box.config(show="")
    )
    torrent_tracker_url_entry_box.bind(
        "<Leave>", lambda event: torrent_tracker_url_entry_box.config(show="*")
    )

    # if tracker url from config.ini is not empty, set it
    if config["torrent_settings"]["tracker_url"] != "":
        torrent_tracker_url_entry_box.insert(
            END, config["torrent_settings"]["tracker_url"]
        )

    # torrent source label
    torrent_source_label = Label(
        torrent_entry_frame,
        text="Source:",
        bd=0,
        relief=SUNKEN,
        background=custom_label_colors["background"],
        fg=custom_label_colors["foreground"],
        font=(set_font, set_font_size),
    )
    torrent_source_label.grid(
        row=1, column=0, columnspan=1, pady=(5, 0), padx=(5, 0), sticky=W
    )

    # torrent source entry box
    torrent_source_entry_box = Entry(
        torrent_entry_frame,
        borderwidth=4,
        fg=custom_entry_colors["foreground"],
        bg=custom_entry_colors["background"],
        disabledforeground=custom_entry_colors["disabledforeground"],
        disabledbackground=custom_entry_colors["disabledbackground"],
        font=(set_fixed_font, set_font_size),
    )
    torrent_source_entry_box.grid(
        row=1, column=1, columnspan=5, padx=(2, 5), pady=5, sticky=N + S + E + W
    )

    # insert string 'BHD' into source
    torrent_source_entry_box.insert(END, "BHD")

    # create queue instance
    torrent_queue = Queue()

    # variable to update if there is an error and to cancel torrent generation safely
    torrent_error = BooleanVar()

    def create_torrent(tor_queue):
        nonlocal torrent_error
        """create torrent in a separate thread"""

        torrent_error.set(False)  # set temporary torrent_error variable
        try:
            build_torrent = Torrent(
                path=pathlib.Path(encode_file_path.get()),
                trackers=str(torrent_tracker_url_entry_box.get()).strip(),
                private=True,
                source=torrent_source_entry_box.get().strip(),
                piece_size=torrent_piece_choices[torrent_piece.get()],
            )
        except torf.URLError:  # if tracker url is invalid
            tor_queue.put("Error Tracker URL is invalid, exiting")
            torrent_error.set(True)  # set torrent_error to true
        except torf.PathError:  # if path to encoded file is invalid
            tor_queue.put("Error Path to encoded file is invalid, exiting")
            torrent_error.set(True)  # set torrent_error to true
        except torf.PieceSizeError:  # if piece size is incorrect
            tor_queue.put("Error Piece size is incorrect, exiting")
            torrent_error.set(True)  # set torrent_error to true

        if torrent_error.get():  # if torrent_error is true
            return  # exit the function

        class WaitForTorrent:
            """class to wait for torrent creation"""

            def __init__(self):
                self.wait_counter = 0

            def wait_for_torrent_output(self):
                """check for torrent file output, if not found check after 1 second or until timed out"""
                if self.wait_counter < 10:
                    if not pathlib.Path(torrent_file_path.get()).is_file():
                        self.wait_counter += 1
                        root.after(1000, self.wait_for_torrent_output)
                    else:
                        tor_queue.put("Complete")
                else:
                    raise ValueError("Cannot locate saved torrent file")

        def torrent_progress(torrent, filepath, pieces_done, pieces_total):
            """call back method to read/abort progress"""

            # update progress bar
            tor_queue.put(f"Progress {pieces_done / pieces_total * 100:3.0f}")

            # if pieces are done and torrent file is present send "Complete" to the Queue
            if pieces_done == pieces_total:
                check_for_tor = WaitForTorrent()
                check_for_tor.wait_for_torrent_output()

            if torrent_error.get():
                return "exit!"

        # if callback torrent_progress returns anything other than None, exit the function
        if not build_torrent.generate(callback=torrent_progress):
            return  # exit function

        # once hash is completed build torrent file, overwrite automatically
        build_torrent.write(pathlib.Path(torrent_file_path.get()), overwrite=True)

    # progress bar
    app_progress_bar = ttk.Progressbar(
        torrent_window,
        orient=HORIZONTAL,
        mode="determinate",
        style="text.Horizontal.TProgressbar",
    )
    app_progress_bar.grid(row=3, column=0, columnspan=10, sticky=W + E, pady=5, padx=5)

    # set text to progress bar every time window opens to ""
    custom_style.configure("text.Horizontal.TProgressbar", text="")

    def torrent_queue_loop():
        """constantly check the torrent queue data for updates"""
        nonlocal torrent_thread

        # if there is data set it to a variables
        try:
            torrent_queue_data = torrent_queue.get_nowait()
        except Empty:
            torrent_queue_data = None

        # if data is not equal to None
        if torrent_queue_data is not None:
            # if the data has Error in the beginning of the string, use this to spawn message box's
            if str(torrent_queue_data).split()[0] == "Error":
                messagebox.showerror(
                    parent=torrent_window,
                    title="Error",
                    message=f"{str(torrent_queue_data).replace('Error ', '')}",
                )

                # call task done and exit queue
                torrent_queue.task_done()
                torrent_queue.join()

                # exit this loop
                return

            # if the data has Progress in the beginning of the string, use this to update the progress bar
            elif str(torrent_queue_data).split()[0].strip() == "Progress":
                try:
                    app_progress_bar["value"] = int(
                        str(torrent_queue_data).split()[1].strip()
                    )
                    custom_style.configure(
                        "text.Horizontal.TProgressbar",
                        text=f"{str(torrent_queue_data).split()[1].strip()}",
                    )

                    # call task_done() on the queue
                    torrent_queue.task_done()

                except TclError:
                    # call task done and exit queue
                    torrent_queue.task_done()
                    torrent_queue.join()

                    # exit this function
                    return

            # if the data has Complete sent to it, confirm that the torrent file is there and call the exit function
            elif str(torrent_queue_data) == "Complete":

                # check if thread is alive and then join it
                if torrent_thread.is_alive():
                    torrent_thread.join()

                # in case user hits cancel after torrent internally "Completes" empty queue
                while torrent_queue.qsize() > 0:
                    try:
                        torrent_queue.task_done()
                    except ValueError:
                        torrent_queue.join()
                        break

                # call the torrent window exit function
                torrent_window_exit_function()

                # exit this loop
                return

            # if cancel is selected
            elif str(torrent_queue_data) == "Cancel":

                # check if thread is alive and then join it
                if torrent_thread.is_alive():
                    torrent_thread.join()

                # in case user hits cancel after torrent internally "Completes" empty queue
                while torrent_queue.qsize() > 0:
                    try:
                        torrent_queue.task_done()
                    except ValueError:
                        torrent_queue.join()
                        break

                # reset progressbar
                app_progress_bar["value"] = 0
                custom_style.configure(
                    "text.Horizontal.TProgressbar",
                    text="",
                )

                # re-enable torrent create button
                create_torrent_button.config(state=NORMAL)

                # exit this loop
                return

        # keep polling data every millisecond
        root.after(1, torrent_queue_loop)

    # create a non-local variable to kill the thread if canceled is pressed
    torrent_thread = threading.Thread()

    def create_torrent_btn_func():
        """function ran when create torrent is selected"""
        nonlocal torrent_thread

        # if file already exists
        if pathlib.Path(torrent_file_path.get()).is_file():
            # ask user if they would like to use the existing torrent file
            use_existing_file = messagebox.askyesno(
                parent=root,
                title="Use Existing File?",
                message=f'"{pathlib.Path(torrent_file_path.get()).name}"\n\n'
                f"File already exists.\n\nWould you like to use "
                f"existing file?",
            )
            # if user presses yes
            if use_existing_file:
                torrent_window_exit_function()
                return

            # if user press no
            if not use_existing_file:
                # ask user if they would like to overwrite
                check_overwrite = messagebox.askyesno(
                    parent=root,
                    title="Overwrite File?",
                    message="Would you like to overwrite file?",
                )
                # if user does not want to overwrite file
                if not check_overwrite:
                    # call the torrent_save_output() function
                    save_new_file = torrent_save_output()
                    # if user press cancel in the torrent_save_output() window
                    if not save_new_file:
                        return  # exit this function

        # after 500 milliseconds start the torrent queue loop
        root.after(50, torrent_queue_loop)

        # disable create torrent button once program starts
        create_torrent_button.config(state=DISABLED)

        # define a torrent thread
        torrent_thread = threading.Thread(
            target=create_torrent, args=(torrent_queue,), daemon=True
        )

        # start the torrent thread
        torrent_thread.start()

    # create torrent button
    create_torrent_button = HoverButton(
        torrent_window,
        text="Create",
        command=create_torrent_btn_func,
        borderwidth="3",
        width=12,
        foreground=custom_button_colors["foreground"],
        background=custom_button_colors["background"],
        activeforeground=custom_button_colors["activeforeground"],
        activebackground=custom_button_colors["activebackground"],
        disabledforeground=custom_button_colors["disabledforeground"],
    )
    create_torrent_button.grid(
        row=4, column=9, columnspan=1, padx=5, pady=(5, 0), sticky=E + S + N
    )

    # cancel torrent button
    cancel_torrent_button = HoverButton(
        torrent_window,
        text="Cancel",
        command=lambda: [
            automatic_workflow_boolean.set(False),
            torrent_queue.put("Cancel"),
            torrent_error.set(True),
        ],
        borderwidth="3",
        width=12,
        foreground=custom_button_colors["foreground"],
        background=custom_button_colors["background"],
        activeforeground=custom_button_colors["activeforeground"],
        activebackground=custom_button_colors["activebackground"],
        disabledforeground=custom_button_colors["disabledforeground"],
    )
    cancel_torrent_button.grid(
        row=4, column=0, columnspan=1, padx=5, pady=(5, 0), sticky=W + S + N
    )

    # if program is in automatic workflow mode
    if automatic_workflow_boolean.get():
        torrent_window.wait_window()


# open torrent window button
open_torrent_window_button = HoverButton(
    manual_workflow,
    text="Create Torrent",
    command=torrent_function_window,
    borderwidth="3",
    width=15,
    state=DISABLED,
    foreground=custom_button_colors["foreground"],
    background=custom_button_colors["background"],
    activeforeground=custom_button_colors["activeforeground"],
    activebackground=custom_button_colors["activebackground"],
    disabledforeground=custom_button_colors["disabledforeground"],
)
open_torrent_window_button.grid(
    row=0, column=0, columnspan=1, padx=(10, 5), pady=1, sticky=E + W
)

# view loaded script button
view_loaded_script = HoverButton(
    root,
    text="View Script",
    state=DISABLED,
    command=lambda: open_script_in_viewer(pathlib.Path(input_script_path.get())),
    borderwidth="3",
    width=10,
    foreground=custom_button_colors["foreground"],
    background=custom_button_colors["background"],
    activeforeground=custom_button_colors["activeforeground"],
    activebackground=custom_button_colors["activebackground"],
    disabledforeground=custom_button_colors["disabledforeground"],
)
view_loaded_script.grid(
    row=4, column=2, columnspan=1, padx=(20, 5), pady=(23, 3), sticky=E + W
)

# automatic workflow frame
automatic_workflow = LabelFrame(
    root,
    text=" Automatic Workflow ",
    labelanchor="nw",
    bd=3,
    font=(set_font, set_font_size, "bold"),
    fg=custom_label_frame_colors["foreground"],
    bg=custom_label_frame_colors["background"],
)
automatic_workflow.grid(column=3, row=4, columnspan=1, padx=5, pady=(5, 3), sticky=E)

automatic_workflow.grid_rowconfigure(0, weight=1)
automatic_workflow.grid_columnconfigure(0, weight=1)


# uploader window
def open_uploader_window(job_mode):
    # uploader window config parser
    uploader_window_config_parser = ConfigParser()
    uploader_window_config_parser.read(config_file)

    # if key is not found in the config.ini file
    if uploader_window_config_parser["bhd_upload_api"]["key"] == "":
        api_checkpoint = messagebox.askyesno(
            parent=root,
            title="Missing API Key",
            message="You are missing your BHD API Key\n\nWould you like to add "
            "this key now?\n\nNote: You can do this manually in "
            '"Options > Api Key"',
        )
        # if user presses yes
        if api_checkpoint:
            # open a new custom window to obtain and save the key to config.ini
            custom_input_prompt(
                root, "BHD Upload Key:", "bhd_upload_api", "key", "hide"
            )
            # define temp parser
            api_temp_parser = ConfigParser()
            api_temp_parser.read(config_file)
            # if bhd key is still nothing, set workflow to False, re-open root and top levels, then exit this function
            if api_temp_parser["bhd_upload_api"]["key"] == "":
                automatic_workflow_boolean.set(0)
                advanced_root_deiconify()
                open_all_toplevels()
                return
        # if user presses no, set workflow to False, re-open root and top levels, then exit this function
        if not api_checkpoint:
            automatic_workflow_boolean.set(0)
            advanced_root_deiconify()
            open_all_toplevels()
            return

    # check job type, if auto or manual, clear some variables
    if job_mode == "auto" or job_mode == "manual":
        movie_search_var.set("")
        tmdb_id_var.set("")
        imdb_id_var.set("")
        release_date_var.set("")
        rating_var.set("")

    # update id variables
    try:
        tmdb_id_var.set(source_file_information["tmdb_id"])
        imdb_id_var.set(source_file_information["imdb_id"])
    except KeyError:
        pass

    # uploader window exit function
    def upload_window_exit_function():
        # uploader exit parser
        uploader_exit_parser = ConfigParser()
        uploader_exit_parser.read(config_file)

        # save window position/geometry
        if upload_window.wm_state() == "normal":
            if (
                uploader_exit_parser["save_window_locations"]["uploader"]
                != upload_window.geometry()
            ):
                uploader_exit_parser.set(
                    "save_window_locations", "uploader", upload_window.geometry()
                )
                with open(config_file, "w") as uploader_exit_config_file:
                    uploader_exit_parser.write(uploader_exit_config_file)

        # close window, re-open root, re-open all top level windows if they exist
        upload_window.destroy()
        advanced_root_deiconify()
        open_all_toplevels()

    # hide all top levels and main GUI
    hide_all_toplevels()
    root.withdraw()

    # upload window
    upload_window = Toplevel()
    upload_window.title("BHDStudio - Uploader")
    upload_window.iconphoto(True, PhotoImage(data=base_64_icon))
    upload_window.configure(background=custom_window_bg_color)
    if uploader_window_config_parser["save_window_locations"]["uploader"] != "":
        upload_window.geometry(
            uploader_window_config_parser["save_window_locations"]["uploader"]
        )
    upload_window.protocol("WM_DELETE_WINDOW", upload_window_exit_function)

    # row and column configures
    for u_w_c in range(4):
        upload_window.grid_columnconfigure(u_w_c, weight=1)
    for u_w_r in range(7):
        upload_window.grid_rowconfigure(u_w_r, weight=1)

    # upload torrent options frame
    torrent_options_frame = LabelFrame(
        upload_window,
        text=" Torrent Input ",
        labelanchor="nw",
        bd=3,
        font=(set_font, set_font_size, "bold"),
        fg=custom_label_frame_colors["foreground"],
        bg=custom_label_frame_colors["background"],
    )
    torrent_options_frame.grid(
        column=0, row=0, columnspan=4, padx=5, pady=(5, 3), sticky=E + W
    )

    torrent_options_frame.grid_rowconfigure(0, weight=1)
    torrent_options_frame.grid_columnconfigure(0, weight=1)
    torrent_options_frame.grid_columnconfigure(1, weight=20)

    # torrent drag and drop function for torrent file
    def torrent_drop_function(event):
        torrent_file_input = [x for x in root.splitlist(event.data)][0]
        # ensure dropped file is a *.torrent file
        if pathlib.Path(torrent_file_input).suffix == ".torrent":
            torrent_file_path.set(str(pathlib.Path(torrent_file_input)))
        else:
            messagebox.showinfo(
                parent=upload_window,
                title="Info",
                message="Only .torrent files can be opened",
            )

    # bind frame to drop torrent file
    torrent_options_frame.drop_target_register(DND_FILES)
    torrent_options_frame.dnd_bind("<<Drop>>", torrent_drop_function)

    # manual torrent file selection
    def open_torrent_file():
        # define parser
        torrent_input_parser = ConfigParser()
        torrent_input_parser.read(config_file)

        # check if last used folder exists
        if pathlib.Path(torrent_input_parser["last_used_folder"]["path"]).is_dir():
            torrent_save_dir = pathlib.Path(
                torrent_input_parser["last_used_folder"]["path"]
            )
        else:
            torrent_save_dir = "/"

        # get torrent input
        torrent_input = filedialog.askopenfilename(
            parent=upload_window,
            title="Select Torrent",
            initialdir=torrent_save_dir,
            filetypes=[("Torrent Files", "*.torrent")],
        )
        if torrent_input:
            torrent_file_path.set(str(pathlib.Path(torrent_input)))

    torrent_input_button = HoverButton(
        torrent_options_frame,
        text="Open",
        command=open_torrent_file,
        borderwidth="3",
        foreground=custom_button_colors["foreground"],
        background=custom_button_colors["background"],
        activeforeground=custom_button_colors["activeforeground"],
        activebackground=custom_button_colors["activebackground"],
        disabledforeground=custom_button_colors["disabledforeground"],
    )
    torrent_input_button.grid(
        row=0, column=0, columnspan=1, padx=5, pady=(7, 0), sticky=N + S + E + W
    )

    torrent_input_entry_box = Entry(
        torrent_options_frame,
        borderwidth=4,
        state=DISABLED,
        textvariable=torrent_file_path,
        fg=custom_entry_colors["foreground"],
        bg=custom_entry_colors["background"],
        disabledforeground=custom_entry_colors["disabledforeground"],
        disabledbackground=custom_entry_colors["disabledbackground"],
        font=(set_fixed_font, set_font_size),
    )
    torrent_input_entry_box.grid(
        row=0, column=1, columnspan=3, padx=5, pady=(5, 0), sticky=E + W
    )

    title_options_frame = LabelFrame(
        upload_window,
        text=" Title ",
        labelanchor="nw",
        bd=3,
        font=(set_font, set_font_size, "bold"),
        fg=custom_label_frame_colors["foreground"],
        bg=custom_label_frame_colors["background"],
    )
    title_options_frame.grid(
        column=0, row=3, columnspan=4, padx=5, pady=(5, 3), sticky=E + W
    )

    title_options_frame.grid_rowconfigure(0, weight=1)
    title_options_frame.grid_columnconfigure(0, weight=1)

    title_input_entry_box = Entry(
        title_options_frame,
        borderwidth=4,
        fg=custom_entry_colors["foreground"],
        bg=custom_entry_colors["background"],
        disabledforeground=custom_entry_colors["disabledforeground"],
        disabledbackground=custom_entry_colors["disabledbackground"],
        font=(set_fixed_font, set_font_size),
    )
    title_input_entry_box.grid(
        row=0, column=0, columnspan=4, padx=5, pady=(5, 3), sticky=E + W
    )

    # automatically insert corrected bhdstudio name into the title box
    if encode_file_path.get() != "":
        title_input_entry_box.insert(
            END,
            str(pathlib.Path(pathlib.Path(encode_file_path.get()).name).with_suffix(""))
            .replace(".", " ")
            .replace("DD 1 0", "DD1.0")
            .replace("DD 2 0", "DD2.0")
            .replace("DD 5 1", "DD5.1")
            .strip(),
        )

    upload_options_frame = LabelFrame(
        upload_window,
        text=" Options ",
        labelanchor="nw",
        bd=3,
        font=(set_font, set_font_size, "bold"),
        fg=custom_label_frame_colors["foreground"],
        bg=custom_label_frame_colors["background"],
    )
    upload_options_frame.grid(
        column=0, row=1, columnspan=4, padx=5, pady=(5, 3), sticky=E + W
    )

    upload_options_frame.grid_rowconfigure(0, weight=1)
    upload_options_frame.grid_rowconfigure(1, weight=1)
    for u_o_f in range(6):
        upload_options_frame.grid_columnconfigure(u_o_f, weight=300)

    type_label = Label(
        upload_options_frame,
        text="Type",
        bd=0,
        relief=SUNKEN,
        background=custom_label_colors["background"],
        fg=custom_label_colors["foreground"],
        font=(set_font, set_font_size + 1),
    )
    type_label.grid(column=0, row=0, columnspan=1, pady=(5, 0), padx=(5, 10), sticky=E)

    # resolution menu
    type_choices = {"720p": "720p", "1080p": "1080p", "2160p": "2160p"}
    type_var = StringVar()
    type_var_menu = OptionMenu(
        upload_options_frame, type_var, *type_choices.keys(), command=None
    )
    type_var_menu.config(
        highlightthickness=1,
        width=12,
        activebackground=custom_button_colors["activebackground"],
        activeforeground=custom_button_colors["activeforeground"],
        background=custom_button_colors["background"],
        foreground=custom_button_colors["foreground"],
    )
    type_var_menu.grid(
        row=0, column=1, columnspan=1, pady=(7, 5), padx=(0, 5), sticky=W
    )
    type_var_menu["menu"].configure(
        activebackground=custom_button_colors["activebackground"],
        activeforeground=custom_button_colors["activeforeground"],
        background=custom_button_colors["background"],
        foreground=custom_button_colors["foreground"],
    )
    if (
        encode_file_path.get().strip() != ""
        and pathlib.Path(encode_file_path.get().strip()).is_file()
    ):
        type_var.set(encode_file_resolution.get().strip())

    # Blu-ray selection menu (only Blu-ray for BHD)
    upload_source_label = Label(
        upload_options_frame,
        text="Source",
        bd=0,
        relief=SUNKEN,
        background=custom_label_colors["background"],
        fg=custom_label_colors["foreground"],
        font=(set_font, set_font_size + 1),
    )
    upload_source_label.grid(
        column=2, row=0, columnspan=1, pady=(5, 0), padx=(5, 5), sticky=E
    )

    source_choices = {"Blu-Ray": "Blu-ray"}
    source_var = StringVar()
    source_var_menu = OptionMenu(
        upload_options_frame, source_var, *source_choices.keys(), command=None
    )
    source_var_menu.config(
        highlightthickness=1,
        width=12,
        activebackground=custom_button_colors["activebackground"],
        activeforeground=custom_button_colors["activeforeground"],
        background=custom_button_colors["background"],
        foreground=custom_button_colors["foreground"],
    )
    source_var_menu.grid(
        row=0, column=3, columnspan=1, pady=(7, 5), padx=(2, 5), sticky=W
    )
    source_var_menu["menu"].configure(
        activebackground=custom_button_colors["activebackground"],
        activeforeground=custom_button_colors["activeforeground"],
        background=custom_button_colors["background"],
        foreground=custom_button_colors["foreground"],
    )
    source_var.set("Blu-Ray")  # set var to Blu-Ray

    # select edition menu
    edition_label = Label(
        upload_options_frame,
        text="Edition\n(Optional)",
        bd=0,
        relief=SUNKEN,
        background=custom_label_colors["background"],
        fg=custom_label_colors["foreground"],
        font=(set_font, set_font_size + 1),
    )
    edition_label.grid(column=4, row=0, columnspan=1, pady=(5, 0), padx=5, sticky=E)

    edition_choices = {
        "N/A": "",
        "Director's Cut": "Director",
        "Extended Cut": "Extended",
        "Theatrical Cut": "Theatrical",
        "Unrated": "Unrated",
    }
    edition_var = StringVar()
    edition_var.set("N/A")
    edition_var_menu = OptionMenu(
        upload_options_frame, edition_var, *edition_choices.keys(), command=None
    )
    edition_var_menu.config(
        highlightthickness=1,
        width=12,
        activebackground=custom_button_colors["activebackground"],
        activeforeground=custom_button_colors["activeforeground"],
        background=custom_button_colors["background"],
        foreground=custom_button_colors["foreground"],
    )
    edition_var_menu.grid(
        row=0, column=5, columnspan=1, pady=(7, 5), padx=(0, 5), sticky=E
    )
    edition_var_menu["menu"].configure(
        activebackground=custom_button_colors["activebackground"],
        activeforeground=custom_button_colors["activeforeground"],
        background=custom_button_colors["background"],
        foreground=custom_button_colors["foreground"],
    )

    # function to automatically grab edition based off of file name
    def check_edition_function():
        if (
            encode_file_path.get().strip() != ""
            and pathlib.Path(encode_file_path.get()).is_file()
        ):
            edition_check = edition_title_extractor(
                str(pathlib.Path(encode_file_path.get()).name)
            )[0]

            if edition_check:
                if "director" in str(edition_check).lower():
                    edition_var.set("Director's Cut")
                elif "extended" in str(edition_check).lower():
                    edition_var.set("Extended Cut")
                elif "theatrical" in str(edition_check).lower():
                    edition_var.set("Theatrical Cut")
                elif "unrated" in str(edition_check).lower():
                    edition_var.set("Unrated")

    check_edition_function()  # run function to check edition upon opening the window automatically

    # IMDB and TMDB frame
    imdb_tmdb_frame = LabelFrame(
        upload_window,
        text=" IMDB / TMDB ",
        labelanchor="nw",
        bd=3,
        font=(set_font, set_font_size, "bold"),
        fg=custom_label_frame_colors["foreground"],
        bg=custom_label_frame_colors["background"],
    )
    imdb_tmdb_frame.grid(
        column=0, row=2, columnspan=8, padx=5, pady=(5, 3), sticky=E + W
    )
    imdb_tmdb_frame.configure(
        fg=custom_label_frame_colors["foreground"],
        bg=custom_label_frame_colors["background"],
        bd=3,
        font=(set_font, set_font_size + 1, "bold"),
    )
    imdb_tmdb_frame.grid_rowconfigure(0, weight=1)
    imdb_tmdb_frame.grid_rowconfigure(1, weight=1)
    imdb_tmdb_frame.grid_columnconfigure(0, weight=1)
    imdb_tmdb_frame.grid_columnconfigure(1, weight=300)
    imdb_tmdb_frame.grid_columnconfigure(7, weight=1)

    # search frame inside the IMDB and TMDB frame
    imdb_tmdb_search_frame = LabelFrame(
        imdb_tmdb_frame,
        text=" Search ",
        labelanchor="n",
        bd=3,
        font=(set_font, set_font_size, "bold"),
        fg=custom_label_frame_colors["foreground"],
        bg=custom_label_frame_colors["background"],
    )
    imdb_tmdb_search_frame.grid(
        column=0, row=0, columnspan=8, padx=5, pady=(5, 3), sticky=E + W
    )

    imdb_tmdb_search_frame.grid_rowconfigure(0, weight=1)
    imdb_tmdb_search_frame.grid_columnconfigure(0, weight=1)

    # search entry box
    search_entry_box = Entry(
        imdb_tmdb_search_frame,
        borderwidth=4,
        textvariable=movie_search_var,
        fg=custom_entry_colors["foreground"],
        bg=custom_entry_colors["background"],
        disabledforeground=custom_entry_colors["disabledforeground"],
        disabledbackground=custom_entry_colors["disabledbackground"],
        font=(set_fixed_font, set_font_size),
    )
    search_entry_box.grid(
        row=0, column=0, columnspan=3, padx=5, pady=(5, 0), sticky=E + W
    )

    # if encode file is loaded, parse the name of the file to get autoload it into the search box for the user
    if pathlib.Path(encode_file_path.get()) != "":
        # clear the search box
        search_entry_box.delete(0, END)

        # run function to get movie name
        encode_movie_str = edition_title_extractor(
            str(pathlib.Path(encode_file_path.get()).name)
        )[1]

        # insert movie name into search box
        search_entry_box.insert(END, encode_movie_str)

    # # function to search tmdb for information
    def call_search_command(*enter_args):
        if search_entry_box.get().strip() != "":
            upload_window.wm_withdraw()
            search_movie_global_function(search_entry_box.get().strip())
            upload_window.wm_deiconify()

    # search button and bind to use command from "Enter" key
    search_entry_box.bind("<Return>", call_search_command)
    search_button = HoverButton(
        imdb_tmdb_search_frame,
        text="Search",
        command=call_search_command,
        borderwidth="3",
        width=12,
        foreground=custom_button_colors["foreground"],
        background=custom_button_colors["background"],
        activeforeground=custom_button_colors["activeforeground"],
        activebackground=custom_button_colors["activebackground"],
        disabledforeground=custom_button_colors["disabledforeground"],
    )
    search_button.grid(
        row=0, column=3, columnspan=1, padx=5, pady=(5, 0), sticky=E + S + N
    )

    # imdb label
    imdb_label = Label(
        imdb_tmdb_frame,
        text="IMDB ID\n(Required)",
        background=custom_label_colors["background"],
        fg=custom_label_colors["foreground"],
        font=(set_font, set_font_size + 1),
    )
    imdb_label.grid(column=0, row=1, columnspan=1, pady=(5, 0), padx=5, sticky=W)

    # imdb entry box
    imdb_entry_box = Entry(
        imdb_tmdb_frame,
        borderwidth=4,
        textvariable=imdb_id_var,
        fg=custom_entry_colors["foreground"],
        bg=custom_entry_colors["background"],
        disabledforeground=custom_entry_colors["disabledforeground"],
        disabledbackground=custom_entry_colors["disabledbackground"],
        font=(set_fixed_font, set_font_size),
    )
    imdb_entry_box.grid(
        row=1, column=1, columnspan=6, padx=5, pady=(5, 0), sticky=E + W
    )

    # decode imdb img for use with the buttons
    decode_resize_imdb_image = Image.open(BytesIO(base64.b64decode(imdb_icon))).resize(
        (35, 35)
    )
    imdb_img = ImageTk.PhotoImage(decode_resize_imdb_image)

    # upload window imdb button with decoded image
    imdb_button = Button(
        imdb_tmdb_frame,
        image=imdb_img,
        borderwidth=0,
        cursor="hand2",
        bg=custom_window_bg_color,
        activebackground=custom_window_bg_color,
        command=open_imdb_link,
    )
    imdb_button.grid(row=1, column=7, columnspan=1, padx=5, pady=(5, 0), sticky=W)
    imdb_button.photo = imdb_img

    # tmdb label
    tmdb_label = Label(
        imdb_tmdb_frame,
        text="TMDB ID\n(Required)",
        background=custom_label_colors["background"],
        fg=custom_label_colors["foreground"],
        font=(set_font, set_font_size + 1),
    )
    tmdb_label.grid(column=0, row=2, columnspan=1, pady=(5, 0), padx=5, sticky=W)

    # tmdb upload window entry box
    tmdb_entry_box = Entry(
        imdb_tmdb_frame,
        borderwidth=4,
        textvariable=tmdb_id_var,
        fg=custom_entry_colors["foreground"],
        bg=custom_entry_colors["background"],
        disabledforeground=custom_entry_colors["disabledforeground"],
        disabledbackground=custom_entry_colors["disabledbackground"],
        font=(set_fixed_font, set_font_size),
    )
    tmdb_entry_box.grid(
        row=2, column=1, columnspan=6, padx=5, pady=(5, 0), sticky=E + W
    )

    # decode tmdb img for use with the buttons
    decode_resize_tmdb_image = Image.open(BytesIO(base64.b64decode(tmdb_icon))).resize(
        (35, 35)
    )
    tmdb_img = ImageTk.PhotoImage(decode_resize_tmdb_image)

    # tmdb clickable icon button in upload window with decoded image
    tmdb_button = Button(
        imdb_tmdb_frame,
        image=tmdb_img,
        borderwidth=0,
        cursor="hand2",
        bg=custom_window_bg_color,
        activebackground=custom_window_bg_color,
        command=open_tmdb_link,
    )
    tmdb_button.grid(row=2, column=7, columnspan=1, padx=5, pady=(5, 0), sticky=W)
    tmdb_button.photo = tmdb_img

    # info frame
    info_frame = LabelFrame(
        upload_window,
        text=" Info ",
        labelanchor="nw",
        bd=3,
        font=(set_font, set_font_size + 1, "bold"),
        fg=custom_label_frame_colors["foreground"],
        bg=custom_label_frame_colors["background"],
    )
    info_frame.grid(column=0, row=4, columnspan=4, padx=5, pady=(5, 3), sticky=E + W)

    info_frame.grid_rowconfigure(0, weight=1)
    info_frame.grid_columnconfigure(0, weight=1)
    info_frame.grid_columnconfigure(1, weight=100)
    info_frame.grid_columnconfigure(2, weight=1)
    info_frame.grid_columnconfigure(3, weight=100)

    # function when media info video file is dropped/opened, it's given a variable when called
    def update_media_info_function(m_i_input):
        # if input is *.txt
        if pathlib.Path(m_i_input).suffix == ".txt":
            # open file and set variable
            with open(pathlib.Path(m_i_input), mode="rt", encoding="utf-8") as m_i_file:
                encode_media_info.set(m_i_file.read())
        # if input is *.mp4
        elif pathlib.Path(m_i_input).suffix == ".mp4":
            # parse file with mediainfo to txt and set variable
            m_i_dropped = MediaInfo.parse(
                pathlib.Path(m_i_input), full=False, output=""
            )  # parse mediainfo
            encode_media_info.set(m_i_dropped)
        media_info_entry.config(state=NORMAL)  # enable entry box
        media_info_entry.delete(0, END)  # clear entry box
        media_info_entry.insert(END, "MediaInfo loaded from file")  # insert string
        media_info_entry.config(state=DISABLED)  # disable entry box

    # function for dropped/open nfo input from txt/nfo file
    def update_nfo_desc_function(nfo_desc_input):
        # open nfo file and set it as variable
        with open(
            pathlib.Path(nfo_desc_input), mode="rt", encoding="utf-8"
        ) as nfo_file_open:
            nfo_info_var.set(nfo_file_open.read())
        nfo_desc_entry.config(state=NORMAL)  # enable entry box
        nfo_desc_entry.delete(0, END)  # clear entry box
        nfo_desc_entry.insert(END, "NFO loaded from file")  # insert string
        nfo_desc_entry.config(state=DISABLED)  # disable entry box

    # torrent drag and drop function for media info and torrent files
    def media_info_nfo_drop_function(event):
        m_i_nfo_drop = [x for x in root.splitlist(event.data)][
            0
        ]  # dropped path to file
        # if file is *.mp4, call update media info func
        if pathlib.Path(m_i_nfo_drop).suffix == ".mp4":
            update_media_info_function(m_i_nfo_drop)
        # if file is *.nfo or *.txt, call update nfo func
        elif (
            pathlib.Path(m_i_nfo_drop).suffix == ".nfo"
            or pathlib.Path(m_i_nfo_drop).suffix == ".txt"
        ):
            update_nfo_desc_function(m_i_nfo_drop)

    # bind frame to drop media info and torrent files
    info_frame.drop_target_register(DND_FILES)
    info_frame.dnd_bind("<<Drop>>", media_info_nfo_drop_function)

    # manual media info dialog, this accepts txt and .mp4
    def open_media_info_text():
        # define parser
        mediainfo_input_parser = ConfigParser()
        mediainfo_input_parser.read(config_file)

        # check if last used folder exists
        if pathlib.Path(mediainfo_input_parser["last_used_folder"]["path"]).is_dir():
            mi_save_dir = pathlib.Path(
                mediainfo_input_parser["last_used_folder"]["path"]
            )
        else:
            mi_save_dir = "/"

        # get media info input
        m_i_t = filedialog.askopenfilename(
            parent=upload_window,
            title="Select Mediainfo File",
            initialdir=mi_save_dir,
            filetypes=[("Text, MP4", "*.txt *.mp4")],
        )
        if m_i_t:  # if selection is made, run the media info function
            update_media_info_function(m_i_t)

    # media info button
    media_info_button = HoverButton(
        info_frame,
        text="MediaInfo",
        command=open_media_info_text,
        borderwidth="3",
        width=15,
        foreground=custom_button_colors["foreground"],
        background=custom_button_colors["background"],
        activeforeground=custom_button_colors["activeforeground"],
        activebackground=custom_button_colors["activebackground"],
        disabledforeground=custom_button_colors["disabledforeground"],
    )
    media_info_button.grid(
        row=0, column=0, columnspan=1, padx=5, pady=(5, 0), sticky=W + S + N
    )

    # media info entry box
    media_info_entry = Entry(
        info_frame,
        borderwidth=4,
        state=DISABLED,
        fg=custom_entry_colors["foreground"],
        bg=custom_entry_colors["background"],
        disabledforeground=custom_entry_colors["disabledforeground"],
        disabledbackground=custom_entry_colors["disabledbackground"],
        font=(set_fixed_font, set_font_size),
    )
    media_info_entry.grid(
        row=0, column=1, columnspan=1, padx=5, pady=(5, 0), sticky=E + W
    )
    # if automatic work flow is set and encode media info is not blank, assume it's been automatically loaded
    if automatic_workflow_boolean and encode_media_info.get() != "":
        media_info_entry.config(state=NORMAL)  # enable entry box
        media_info_entry.delete(0, END)  # clear entry box
        media_info_entry.insert(END, "MediaInfo Loaded Internally")  # insert string
        media_info_entry.config(state=DISABLED)  # disable entry box

    # manual nfo open dialog, this accepts *.txt and *.nfo files
    def open_nfo_info_text_nfo():
        # define parser
        open_nfo_parser = ConfigParser()
        open_nfo_parser.read(config_file)

        # check if last used folder exists
        if pathlib.Path(open_nfo_parser["last_used_folder"]["path"]).is_dir():
            nfo_initial_save_dir = pathlib.Path(
                open_nfo_parser["last_used_folder"]["path"]
            )
        else:
            nfo_initial_save_dir = "/"

        # nfo/description open prompt
        nfo_desc = filedialog.askopenfilename(
            parent=upload_window,
            title="Select NFO",
            initialdir=nfo_initial_save_dir,
            filetypes=[("NFO, Text", "*.txt *.nfo")],
        )
        if nfo_desc:  # if selection is made, run the nfo function
            update_nfo_desc_function(nfo_desc)

    # nfo load button
    nfo_desc_button = HoverButton(
        info_frame,
        text="NFO / Description",
        command=open_nfo_info_text_nfo,
        borderwidth="3",
        width=15,
        foreground=custom_button_colors["foreground"],
        background=custom_button_colors["background"],
        activeforeground=custom_button_colors["activeforeground"],
        activebackground=custom_button_colors["activebackground"],
        disabledforeground=custom_button_colors["disabledforeground"],
    )
    nfo_desc_button.grid(
        row=0, column=2, columnspan=1, padx=5, pady=(5, 0), sticky=E + S + N
    )

    # nfo entry
    nfo_desc_entry = Entry(
        info_frame,
        borderwidth=4,
        state=DISABLED,
        fg=custom_entry_colors["foreground"],
        bg=custom_entry_colors["background"],
        disabledforeground=custom_entry_colors["disabledforeground"],
        disabledbackground=custom_entry_colors["disabledbackground"],
        font=(set_fixed_font, set_font_size),
    )
    nfo_desc_entry.grid(
        row=0, column=3, columnspan=1, padx=5, pady=(5, 0), sticky=E + W
    )
    # if automatic work flow is set and nfo info is not blank, assume it's been automatically loaded
    if automatic_workflow_boolean and nfo_info_var.get() != "":
        nfo_desc_entry.config(state=NORMAL)
        nfo_desc_entry.insert(END, "NFO Loaded Internally")
        nfo_desc_entry.config(state=DISABLED)

    # misc options frame
    misc_options_frame = LabelFrame(
        upload_window,
        text=" Upload Options ",
        labelanchor="nw",
        bd=3,
        font=(set_font, set_font_size + 1, "bold"),
        fg=custom_label_frame_colors["foreground"],
        bg=custom_label_frame_colors["background"],
    )
    misc_options_frame.grid(
        column=0, row=5, columnspan=3, padx=5, pady=(5, 3), sticky=E + W
    )

    misc_options_frame.grid_rowconfigure(0, weight=1)
    for m_o_f in range(3):
        misc_options_frame.grid_columnconfigure(m_o_f, weight=1)

    # live checkbox, set to on, this is a permanent choice
    def update_checkbutton_info():
        chk_button_parser = ConfigParser()
        chk_button_parser.read(config_file)
        if live_boolean.get():
            save_checkbutton = 1
        elif not live_boolean.get():
            save_checkbutton = 0
        chk_button_parser.set("live_release", "value", str(save_checkbutton))
        with open(config_file, "w") as c_b_config:
            chk_button_parser.write(c_b_config)

    live_checkbox = Checkbutton(
        misc_options_frame,
        text="Send to Drafts",
        variable=live_boolean,
        state=DISABLED,
        onvalue=0,
        offvalue=1,
        command=update_checkbutton_info,
    )
    live_checkbox.grid(row=0, column=0, padx=5, pady=(5, 3), sticky=E + W)
    live_checkbox.configure(
        background=custom_window_bg_color,
        foreground=custom_button_colors["foreground"],
        activebackground=custom_window_bg_color,
        activeforeground=custom_button_colors["foreground"],
        selectcolor=custom_window_bg_color,
        font=(set_font, set_font_size + 1),
    )
    live_boolean.set(0)

    # parser to check for password and remember settings if enabled
    live_temp_parser = ConfigParser()
    live_temp_parser.read(config_file)
    # if sticky gives users the password to live release
    if live_temp_parser["live_release"]["password"] == "StickySaidSo":
        live_checkbox.config(state=NORMAL)  # enable check button
        try:  # try to set check button based off of config
            live_boolean.set(int(live_temp_parser["live_release"]["value"]))
        except ValueError:  # if check button is blank or value error
            live_boolean.set(0)  # set it to the default 0

    anonymous_checkbox = Checkbutton(
        misc_options_frame,
        text="Anonymous",
        variable=anonymous_boolean,
        onvalue=1,
        offvalue=0,
    )
    anonymous_checkbox.grid(row=0, column=1, padx=5, pady=(5, 3), sticky=W)
    anonymous_checkbox.configure(
        background=custom_window_bg_color,
        foreground=custom_button_colors["foreground"],
        activebackground=custom_window_bg_color,
        activeforeground=custom_button_colors["foreground"],
        selectcolor=custom_window_bg_color,
        font=(set_font, set_font_size + 1),
    )
    anonymous_boolean.set(0)

    # upload to beyond hd api function
    def upload_to_api():
        # set config parser
        api_parser = ConfigParser()
        api_parser.read(config_file)

        # upload status window
        upload_status_window = Toplevel()
        upload_status_window.configure(background=custom_window_bg_color)
        upload_status_window.geometry(
            f'+{str(int(upload_window.geometry().split("+")[1]) + 10)}+'
            f'{str(int(upload_window.geometry().split("+")[2]) + 180)}'
        )
        upload_status_window.resizable(False, False)
        upload_status_window.grab_set()
        upload_status_window.wm_overrideredirect(True)
        upload_window.wm_attributes(
            "-alpha", 0.90
        )  # set parent window to be slightly transparent
        upload_status_window.grid_rowconfigure(0, weight=1)
        upload_status_window.grid_columnconfigure(0, weight=1)

        # encoder name frame
        upload_output_frame = Frame(
            upload_status_window,
            highlightbackground=custom_frame_bg_colors["highlightcolor"],
            highlightthickness=2,
            bg=custom_frame_bg_colors["background"],
            highlightcolor=custom_frame_bg_colors["highlightcolor"],
        )
        upload_output_frame.grid(column=0, row=0, columnspan=3, sticky=N + S + E + W)

        for e_n_f in range(3):
            upload_output_frame.grid_columnconfigure(e_n_f, weight=1)
            upload_output_frame.grid_rowconfigure(e_n_f, weight=1)
        upload_output_frame.grid_rowconfigure(0, weight=100)

        # create window
        upload_status_info = scrolledtextwidget.ScrolledText(
            upload_output_frame,
            bg=custom_scrolled_text_widget_color["background"],
            fg=custom_scrolled_text_widget_color["foreground"],
            bd=4,
            wrap=WORD,
        )
        upload_status_info.grid(
            row=0, column=0, columnspan=3, pady=(2, 0), padx=5, sticky=E + W
        )
        upload_status_info.insert(END, "Uploading, please wait...")
        upload_status_info.config(state=DISABLED)

        # function to save new name to config.ini
        def encoder_okay_func():
            upload_window.wm_attributes("-alpha", 1.0)  # restore transparency
            upload_status_window.destroy()  # close window

        # create 'OK' button
        uploader_okay_btn = HoverButton(
            upload_output_frame,
            text="OK",
            command=encoder_okay_func,
            borderwidth="3",
            width=8,
            foreground=custom_button_colors["foreground"],
            background=custom_button_colors["background"],
            activeforeground=custom_button_colors["activeforeground"],
            activebackground=custom_button_colors["activebackground"],
            disabledforeground=custom_button_colors["disabledforeground"],
        )
        uploader_okay_btn.grid(row=2, column=2, columnspan=1, padx=7, pady=5, sticky=E)

        # if live boolean is True
        if live_boolean.get():
            live_release = 1
        # if live boolean is False
        elif not live_boolean.get():
            live_release = 0

        # if anon boolean is True
        if anonymous_boolean.get():
            anonymous_release = 1
        # if anon boolean is False
        elif not anonymous_boolean.get():
            anonymous_release = 0

        # api link
        api_link = (
            f"https://beyond-hd.me/api/upload/{api_parser['bhd_upload_api']['key']}"
        )

        # define upload params for BHD
        upload_payload_params = {
            "name": title_input_entry_box.get().strip(),
            "category_id": 1,
            "type": type_choices[type_var.get()],
            "source": source_choices[source_var.get()],
            "internal": 1,
            "imdb_id": imdb_id_var.get(),
            "tmdb_id": tmdb_id_var.get(),
            "description": nfo_info_var.get(),
            "nfo": nfo_info_var.get(),
            "live": live_release,
            "anon": anonymous_release,
            "stream": "optimized",
            "promo": 2,
        }

        # if any preset edition selections are selected add the params and value
        if edition_var.get() != "N/A":
            upload_payload_params.update(
                {"edition": edition_choices[edition_var.get()]}
            )

        try:  # try to upload
            upload_job = requests.post(
                api_link,
                upload_payload_params,
                files={
                    "file": open(pathlib.Path(torrent_file_path.get()), "rb"),
                    "mediainfo": encode_media_info.get(),
                },
            )
        except requests.exceptions.ConnectionError:  # if there is a connection error show function
            encoder_okay_func()  # this runs the okay button function to close the window and restore transparency
            messagebox.showerror(
                parent=upload_window,
                title="Error",
                message="There is a connection error, check "
                "your internet connection",
            )
            return  # exit the function

        upload_status_info.config(state=NORMAL)  # enable scrolled text box
        upload_status_info.delete("1.0", END)  # delete all contents of the box

        def successful_upload_func():
            """function to inject if it's enabled and reset the GUI after a successful upload"""
            api2_parser = ConfigParser()
            api2_parser.read(config_file)

            # inject torrent to qBittorrent/deluge if injection is enabled
            if (
                api2_parser["qbit_client"]["qbit_injection_toggle"] == "true"
                or api2_parser["deluge_client"]["deluge_injection_toggle"] == "true"
            ):
                # create Clients() instance
                injection_client = Clients()

                if api2_parser["qbit_client"]["qbit_injection_toggle"] == "true":
                    # use qBittorrent method
                    auto_injection = injection_client.qbittorrent(
                        encode_file_path=encode_file_path.get(),
                        torrent_file_path=torrent_file_path.get(),
                    )

                elif api2_parser["deluge_client"]["deluge_injection_toggle"] == "true":
                    # use Deluge method
                    auto_injection = injection_client.deluge(
                        torrent_file_path=torrent_file_path.get()
                    )

                # update status window
                upload_status_info.insert(END, f"\n\n{auto_injection}")

            reset_gui()

        # if upload returns a status code '200', assume success
        if upload_job.status_code == 200:

            # if upload is saved to drafts
            if (
                upload_job.json()["status_code"] == 1
                and "saved" in upload_job.json()["status_message"]
                and upload_job.json()["success"]
            ):
                upload_status_info.insert(
                    END,
                    "Upload is successful!\nUpload has been successfully "
                    "saved as a draft on site",
                )
                successful_upload_func()

            # if upload is released live on site
            elif upload_job.json()["status_code"] == 2 and upload_job.json()["success"]:
                upload_status_info.insert(
                    END,
                    "Upload is successful!\nUpload has been successfully "
                    f"released live on site\n\nDownload URL:\n{upload_job.json()['status_message']}",
                )
                successful_upload_func()

            # if there was an error
            elif upload_job.json()["status_code"] == 0:
                upload_status_info.insert(
                    END,
                    f"Upload failed!\n\nError:\n{upload_job.json()['status_message']}",
                )

                # if there was an error exit this function
                return

            else:
                upload_status_info.insert(
                    END,
                    f"There was an error:\n\n{upload_job.json()['status_message']}",
                )

        # if upload returns a status code '400', site error
        elif upload_job.status_code == 404:
            upload_status_info.insert(
                END,
                f"Upload failed! This is likely a problem with the site\n\n"
                f"{upload_job.json()['status_message']}",
            )

        # if upload returns a status code '400', critical site error
        elif upload_job.status_code == 500:
            upload_status_info.insert(
                END,
                "Error!\n\nThe site isn't returning the upload status.\n"
                "This is a critical error from the site.\n"
                f"Status code:{str(upload_job.status_code)}",
            )

        # if it returns any other status code, raise a pythonic error to be shown and print unknown error
        else:
            upload_status_info.insert(END, "Unknown error!")
            upload_job.raise_for_status()
        upload_status_info.config(state=DISABLED)  # disable scrolled textbox

    # enabled upload img
    decode_resize_tmdb_image = Image.open(
        BytesIO(base64.b64decode(bhd_upload_icon))
    ).resize((120, 45))
    upload_img = ImageTk.PhotoImage(decode_resize_tmdb_image)

    # disabled upload img
    decode_resize_tmdb_image2 = Image.open(
        BytesIO(base64.b64decode(bhd_upload_icon_disabled))
    ).resize((120, 45))
    upload_img_disabled = ImageTk.PhotoImage(decode_resize_tmdb_image2)

    upload_button = HoverButton(
        upload_window,
        text="Upload",
        image=upload_img_disabled,
        borderwidth=0,
        cursor="question_arrow",
        background=custom_button_colors["background"],
        activebackground=custom_button_colors["activebackground"],
        disabledforeground=custom_button_colors["disabledforeground"],
    )
    upload_button.grid(row=5, column=3, padx=(5, 10), pady=(5, 10), sticky=E + S)
    upload_button.image = upload_img_disabled

    # function to define and display missing inputs
    def show_missing_input():
        missing_list = []  # create empty missing list
        if torrent_file_path.get() == "":
            missing_list.append("Torrent Input")
        if title_input_entry_box.get().strip() == "":
            missing_list.append("Title")
        if type_var.get() == "":
            missing_list.append("Type")
        if source_var.get() == "":
            missing_list.append("Source")
        if imdb_id_var.get().strip() == "":
            missing_list.append("IMDB ID")
        if tmdb_id_var.get().strip() == "":
            missing_list.append("TMDB ID")
        if encode_media_info.get() == "":
            missing_list.append("MediaInfo")
        if nfo_info_var.get() == "":
            missing_list.append("NFO/Description")

        # open messagebox with all the missing inputs
        messagebox.showinfo(
            parent=upload_window,
            title="Missing Input",
            message=f"Missing inputs:\n\n{', '.join(missing_list)}",
        )

    # function to check for missing variables and enable/change button and button commands
    def enable_disable_upload_button():
        # if everything is needed in the window, enable upload button
        if (
            torrent_file_path.get() != ""
            and title_input_entry_box.get().strip() != ""
            and type_var.get() != ""
            and source_var.get() != ""
            and imdb_id_var.get().strip() != ""
            and tmdb_id_var.get().strip() != ""
            and encode_media_info.get() != ""
            and nfo_info_var.get() != ""
        ):
            upload_button.config(image=upload_img)
            upload_button.image = upload_img
            upload_button.config(command=upload_to_api, cursor="hand2")
        else:  # if 1 item is missing, disable upload button and enable show missing input function
            upload_button.config(image=upload_img_disabled)
            upload_button.image = upload_img_disabled
            upload_button.config(command=show_missing_input, cursor="question_arrow")
        upload_window.after(
            50, enable_disable_upload_button
        )  # loop to check this constantly

    # start loop
    enable_disable_upload_button()


# open torrent window button
open_uploader_button = HoverButton(
    manual_workflow,
    text="Uploader",
    state=DISABLED,
    command=lambda: [
        automatic_workflow_boolean.set(False),
        open_uploader_window("manual"),
    ],
    borderwidth="3",
    width=15,
    foreground=custom_button_colors["foreground"],
    background=custom_button_colors["background"],
    activeforeground=custom_button_colors["activeforeground"],
    activebackground=custom_button_colors["activebackground"],
    disabledforeground=custom_button_colors["disabledforeground"],
)
open_uploader_button.grid(
    row=0, column=2, columnspan=1, padx=(5, 10), pady=1, sticky=E + W
)


# automatic work flow button
def auto_workflow():
    # check screens
    check_screens = parse_screen_shots()
    if (
        not check_screens
    ):  # if returned false, show error message and exit this function
        messagebox.showerror(
            parent=root,
            title="Error!",
            message="Missing or incorrectly formatted screenshots\n\n"
            "Screen shots need to be in multiples of 2",
        )
        return
    torrent_function_window()  # if passed run torrent function
    if (
        not automatic_workflow_boolean.get()
    ):  # if returned false, exit this function back to main GUI
        return
    open_nfo_viewer()  # if passed run nfo viewer function
    if (
        not automatic_workflow_boolean.get()
    ):  # if returned false, exit this function back to main GUI
        return
    open_uploader_window(
        "auto"
    )  # if it passes all the automatic requirements, open upload window in 'auto' mode


# parse and upload button
parse_and_upload = HoverButton(
    automatic_workflow,
    text="Parse & Upload",
    state=DISABLED,
    command=lambda: [automatic_workflow_boolean.set(True), auto_workflow()],
    borderwidth="3",
    width=1,
    foreground=custom_button_colors["foreground"],
    background=custom_button_colors["background"],
    activeforeground=custom_button_colors["activeforeground"],
    activebackground=custom_button_colors["activebackground"],
    disabledforeground=custom_button_colors["disabledforeground"],
)
parse_and_upload.grid(row=0, column=0, columnspan=1, padx=10, pady=1, sticky=E + W)


# Hide/Open all top level window function -----------------------------------------------------------------------------
def hide_all_toplevels():
    for widget in root.winfo_children():
        if isinstance(widget, Toplevel):
            widget.withdraw()


def open_all_toplevels():
    for widget in root.winfo_children():
        if isinstance(widget, Toplevel):
            widget.deiconify()


# ----------------------------------------------------------------------------- Hide/Open all top level window function

# function to check state of root, then deiconify it accordingly ------------------------------------------------------
def advanced_root_deiconify():
    if root.winfo_viewable():
        root.deiconify()
    elif not root.winfo_viewable():
        root.iconify()
        root.deiconify()


# ------------------------------------------------------ function to check state of root, then deiconify it accordingly

# reset gui -----------------------------------------------------------------------------------------------------------
def reset_gui():
    delete_source_entry()
    delete_encode_entry()
    image_listbox.config(state=NORMAL)
    image_listbox.delete(0, END)
    image_listbox.config(state=DISABLED)
    screenshot_scrolledtext.delete("1.0", END)
    tabs.select(image_tab)
    clear_all_variables()


# ----------------------------------------------------------------------------------------------------------- reset gui

# reset settings ------------------------------------------------------------------------------------------------------
def reset_all_settings():
    reset_settings = messagebox.askyesno(
        title="Prompt", message="Are you sure you want to reset all settings?"
    )

    # if user presses yes
    if reset_settings:
        pathlib.Path(config_file).unlink(missing_ok=True)
        pathlib.Path("runtime/user.bin").unlink(missing_ok=True)
        pathlib.Path("runtime/pass.bin").unlink(missing_ok=True)
        messagebox.showinfo(
            title="Prompt",
            message="Settings are reset, program will restart automatically",
        )

        # close root window
        root.destroy()

        # re-open the program
        subprocess.run(
            pathlib.Path().cwd() / "BHDStudioUploadTool.exe"
        )  # use subprocess.run to restart


# ------------------------------------------------------------------------------------------------------ reset settings

# menu Items and Sub-Bars ---------------------------------------------------------------------------------------------
my_menu_bar = Menu(root, tearoff=0)
root.config(menu=my_menu_bar)

file_menu = Menu(my_menu_bar, tearoff=0, activebackground="dim grey")
my_menu_bar.add_cascade(label="File", menu=file_menu)

file_menu.add_command(
    label="Open Source File", command=manual_source_input, accelerator="[Ctrl+O]"
)
root.bind("<Control-s>", lambda event: manual_source_input())
file_menu.add_command(
    label="Open Encode File", command=manual_encode_input, accelerator="[Ctrl+E]"
)
root.bind("<Control-e>", lambda event: manual_encode_input())
file_menu.add_separator()
file_menu.add_command(
    label="Open StaxRip Temp", command=staxrip_manual_open, accelerator="[Ctrl+S]"
)
root.bind("<Control-s>", lambda event: staxrip_manual_open())
file_menu.add_separator()
file_menu.add_command(label="Reset GUI", command=reset_gui, accelerator="[Ctrl+R]")
root.bind("<Control-r>", lambda event: reset_gui())
file_menu.add_command(label="Exit", command=root_exit_function, accelerator="[Alt+F4]")


# custom input box that accepts parent window, label, config option, and config key
def custom_input_prompt(
    parent_window, label_input, config_option, config_key, hide_show
):
    # hide all top levels if they are opened
    hide_all_toplevels()
    # set parser
    custom_input_parser = ConfigParser()
    custom_input_parser.read(config_file)

    # encoder name window
    custom_input_window = Toplevel()
    custom_input_window.title("")
    custom_input_window.configure(background=custom_window_bg_color)
    custom_input_window.geometry(
        f'+{str(int(parent_window.geometry().split("+")[1]) + 220)}+'
        f'{str(int(parent_window.geometry().split("+")[2]) + 230)}'
    )
    custom_input_window.resizable(False, False)
    custom_input_window.grab_set()
    custom_input_window.protocol("WM_DELETE_WINDOW", lambda: custom_okay_func())
    parent_window.wm_attributes(
        "-alpha", 0.90
    )  # set parent window to be slightly transparent
    custom_input_window.grid_rowconfigure(0, weight=1)
    custom_input_window.grid_columnconfigure(0, weight=1)

    # encoder name frame
    custom_input_frame = Frame(
        custom_input_window,
        highlightbackground=custom_frame_bg_colors["highlightcolor"],
        highlightthickness=2,
        bg=custom_frame_bg_colors["background"],
        highlightcolor=custom_frame_bg_colors["highlightcolor"],
    )
    custom_input_frame.grid(column=0, row=0, columnspan=3, sticky=N + S + E + W)
    for e_n_f in range(3):
        custom_input_frame.grid_columnconfigure(e_n_f, weight=1)
        custom_input_frame.grid_rowconfigure(e_n_f, weight=1)

    # create label
    image_name_label3 = Label(
        custom_input_frame,
        text=label_input,
        background=custom_label_colors["background"],
        fg=custom_label_colors["foreground"],
        font=(set_font, set_font_size, "bold"),
    )
    image_name_label3.grid(
        row=0, column=0, columnspan=3, sticky=W + N, padx=5, pady=(2, 0)
    )

    # create entry box
    custom_entry_box = Entry(
        custom_input_frame,
        borderwidth=4,
        fg=custom_entry_colors["foreground"],
        bg=custom_entry_colors["background"],
        width=30,
        font=(set_fixed_font, set_font_size),
    )
    custom_entry_box.grid(
        row=1, column=0, columnspan=3, padx=10, pady=(0, 5), sticky=E + W
    )
    custom_entry_box.insert(END, custom_input_parser[config_option][config_key])
    # if api key is called
    if hide_show == "hide":
        custom_entry_box.config(show="*")
        custom_entry_box.bind("<Enter>", lambda event: custom_entry_box.config(show=""))
        custom_entry_box.bind(
            "<Leave>", lambda event: custom_entry_box.config(show="*")
        )

    # function to save new name to config.ini
    def custom_okay_func():
        if (
            custom_input_parser[config_option][config_key]
            != custom_entry_box.get().strip()
        ):
            custom_input_parser.set(
                config_option, config_key, custom_entry_box.get().strip()
            )
            with open(config_file, "w") as encoder_name_config_file:
                custom_input_parser.write(encoder_name_config_file)
        parent_window.wm_attributes("-alpha", 1.0)  # restore transparency
        custom_input_window.destroy()  # close window

    # create 'OK' button
    custom_okay_btn = HoverButton(
        custom_input_frame,
        text="OK",
        command=custom_okay_func,
        borderwidth="3",
        width=8,
        foreground=custom_button_colors["foreground"],
        background=custom_button_colors["background"],
        activeforeground=custom_button_colors["activeforeground"],
        activebackground=custom_button_colors["activebackground"],
        disabledforeground=custom_button_colors["disabledforeground"],
    )
    custom_okay_btn.grid(row=2, column=0, columnspan=1, padx=7, pady=5, sticky=S + W)

    # create 'Cancel' button
    custom_cancel_btn = HoverButton(
        custom_input_frame,
        text="Cancel",
        width=8,
        command=lambda: [
            custom_input_window.destroy(),
            root.wm_attributes("-alpha", 1.0),
        ],
        borderwidth="3",
        foreground=custom_button_colors["foreground"],
        background=custom_button_colors["background"],
        activeforeground=custom_button_colors["activeforeground"],
        activebackground=custom_button_colors["activebackground"],
        disabledforeground=custom_button_colors["disabledforeground"],
    )
    custom_cancel_btn.grid(row=2, column=2, columnspan=1, padx=7, pady=5, sticky=S + E)

    def right_click_pop_up_menu(e):
        """
        Right click menu for screenshot box
        Function for mouse button 3 (right click) to pop up menu
        """

        # get the position of 'e'
        copy_paste_menu.tk_popup(e.x_root, e.y_root)

    # pop up menu to enable/disable manual edits in release notes
    copy_paste_menu = Menu(
        custom_input_window,
        tearoff=False,
        font=(set_font, set_font_size + 1),
        background=custom_button_colors["background"],
        foreground=custom_button_colors["foreground"],
        activebackground=custom_button_colors["activebackground"],
        activeforeground=custom_button_colors["activeforeground"],
    )

    # Right click menu for copy
    copy_paste_menu.add_command(
        label="Copy",
        command=lambda: pyperclip.copy(custom_entry_box.get().strip()),
    )

    # Right click menu for paste
    copy_paste_menu.add_command(
        label="Paste",
        command=lambda: [
            custom_entry_box.delete(0, END),
            custom_entry_box.insert(END, pyperclip.paste()),
        ],
    )
    # Uses mouse button 3 (right click) to open
    custom_input_window.bind("<Button-3>", right_click_pop_up_menu)

    custom_input_window.wait_window()  # wait for window to be closed
    open_all_toplevels()  # re-open all top levels if they exist


# define default torrent path window
def torrent_path_window_func(label_text, config_set_opt1, config_set_opt2):
    # hide all top levels if they are opened
    hide_all_toplevels()
    # define parser
    general_path_parser = ConfigParser()
    general_path_parser.read(config_file)

    # function to exit torrent path window
    def general_path_okay_func():
        root.wm_attributes("-alpha", 1.0)  # restore transparency
        general_path_window.destroy()  # close window

    # torrent path window
    general_path_window = Toplevel()
    general_path_window.title("")
    general_path_window.configure(background=custom_window_bg_color)
    general_path_window.geometry(
        f'+{str(int(root.geometry().split("+")[1]) + 156)}+'
        f'{str(int(root.geometry().split("+")[2]) + 230)}'
    )
    general_path_window.resizable(False, False)
    general_path_window.grab_set()
    general_path_window.protocol("WM_DELETE_WINDOW", general_path_okay_func)
    root.wm_attributes("-alpha", 0.92)  # set parent window to be slightly transparent
    general_path_window.grid_rowconfigure(0, weight=1)
    general_path_window.grid_columnconfigure(0, weight=1)

    # encoder name frame
    general_path_frame = Frame(
        general_path_window,
        highlightbackground=custom_frame_bg_colors["highlightcolor"],
        highlightthickness=2,
        bg=custom_frame_bg_colors["background"],
        highlightcolor=custom_frame_bg_colors["highlightcolor"],
    )
    general_path_frame.grid(column=0, row=0, columnspan=3, sticky=N + S + E + W)

    # grid and row config
    for e_n_f in range(4):
        general_path_frame.grid_columnconfigure(e_n_f, weight=1)
        general_path_frame.grid_rowconfigure(e_n_f, weight=1)
    general_path_frame.grid_columnconfigure(1, weight=100)
    general_path_frame.grid_rowconfigure(2, weight=50)

    # create label
    general_path_label = Label(
        general_path_frame,
        text=f"{label_text} Output Path",
        background=custom_label_colors["background"],
        fg=custom_label_colors["foreground"],
        font=(set_font, set_font_size, "bold"),
    )
    general_path_label.grid(
        row=0, column=0, columnspan=3, sticky=W + N, padx=5, pady=(2, 8)
    )

    # set torrent default path function
    def save_default_torrent_path():
        # save directory dialog box
        general_path_dialogue = filedialog.askdirectory(
            parent=general_path_window, title="Set Default Path"
        )
        # if directory is defined
        if general_path_dialogue:
            # define parser/settings then write to config file
            general_path_update_parser = ConfigParser()
            general_path_update_parser.read(config_file)
            general_path_update_parser.set(
                str(config_set_opt1),
                str(config_set_opt2),
                str(pathlib.Path(general_path_dialogue)),
            )
            with open(config_file, "w") as t_p_configfile:
                general_path_update_parser.write(t_p_configfile)

            # update entry box
            general_path_entry_box.config(state=NORMAL)
            general_path_entry_box.delete(0, END)
            general_path_entry_box.insert(END, str(pathlib.Path(general_path_dialogue)))
            general_path_entry_box.config(state=DISABLED)

            # update torrent_file_path string var
            if label_text == "Torrent":
                if torrent_file_path.get() != "":
                    torrent_file_path.set(
                        str(
                            pathlib.Path(
                                general_path_update_parser[str(config_set_opt1)][
                                    str(config_set_opt2)
                                ]
                            )
                            / pathlib.Path(
                                pathlib.Path(torrent_file_path.get()).stem
                            ).with_suffix(".torrent")
                        )
                    )

    # create torrent path button
    general_path_btn = HoverButton(
        general_path_frame,
        text="Path",
        command=save_default_torrent_path,
        borderwidth="3",
        width=8,
        foreground=custom_button_colors["foreground"],
        background=custom_button_colors["background"],
        activeforeground=custom_button_colors["activeforeground"],
        activebackground=custom_button_colors["activebackground"],
        disabledforeground=custom_button_colors["disabledforeground"],
    )
    general_path_btn.grid(row=1, column=0, columnspan=1, padx=(5, 2), pady=5, sticky=W)

    # create entry box
    general_path_entry_box = Entry(
        general_path_frame,
        borderwidth=4,
        fg=custom_entry_colors["foreground"],
        bg=custom_entry_colors["background"],
        disabledforeground=custom_entry_colors["disabledforeground"],
        disabledbackground=custom_entry_colors["disabledbackground"],
        width=30,
        font=(set_fixed_font, set_font_size),
    )
    general_path_entry_box.grid(
        row=1, column=1, columnspan=2, padx=5, pady=5, sticky=E + W
    )
    general_path_entry_box.insert(
        END, general_path_parser[str(config_set_opt1)][str(config_set_opt2)]
    )
    general_path_entry_box.config(state=DISABLED)

    # reset path function
    def reset_torrent_path_function():
        # confirm reset
        confirm_reset = messagebox.askyesno(
            parent=general_path_window,
            title="Confirm",
            message="Are you sure you want to reset path back to default?\n"
            "(Encode file input path)",
        )
        # if user presses yes
        if confirm_reset:
            # define parser/settings then write to config file
            reset_path_parser = ConfigParser()
            reset_path_parser.read(config_file)
            reset_path_parser.set(str(config_set_opt1), str(config_set_opt2), "")
            with open(config_file, "w") as t_r_configfile:
                reset_path_parser.write(t_r_configfile)
            # update entry box
            general_path_entry_box.config(state=NORMAL)
            general_path_entry_box.delete(0, END)
            general_path_entry_box.config(state=DISABLED)
            # update torrent_file_path string var if encode_file_path is loaded
            if encode_file_path.get() != "":
                torrent_file_path.set(
                    str(pathlib.Path(encode_file_path.get()).with_suffix(".torrent"))
                )

    # create torrent reset path button
    general_path_reset_btn = HoverButton(
        general_path_frame,
        text="X",
        command=reset_torrent_path_function,
        borderwidth="3",
        width=3,
        foreground=custom_button_colors["foreground"],
        background=custom_button_colors["background"],
        activeforeground=custom_button_colors["activeforeground"],
        activebackground=custom_button_colors["activebackground"],
        disabledforeground=custom_button_colors["disabledforeground"],
    )
    general_path_reset_btn.grid(
        row=1, column=3, columnspan=1, padx=(2, 5), pady=5, sticky=E
    )

    # create 'OK' button
    general_path_okay_btn = HoverButton(
        general_path_frame,
        text="OK",
        command=general_path_okay_func,
        borderwidth="3",
        width=8,
        foreground=custom_button_colors["foreground"],
        background=custom_button_colors["background"],
        activeforeground=custom_button_colors["activeforeground"],
        activebackground=custom_button_colors["activebackground"],
        disabledforeground=custom_button_colors["disabledforeground"],
    )
    general_path_okay_btn.grid(
        row=2, column=2, columnspan=2, padx=7, pady=(5, 3), sticky=E + S
    )

    general_path_window.wait_window()  # wait for window to be closed
    open_all_toplevels()  # re-open all top levels if they exist


# beyondhd.co login credentials
def bhd_co_login_window():
    # hide all top levels if they are opened
    hide_all_toplevels()

    # function to save new name to config.ini
    def save_exit_function():
        # get user and pass to encrypt and save
        user_pass_encoder = Fernet(crypto_key)
        encode_user = user_pass_encoder.encrypt(
            str(user_entry_box.get()).strip().encode()
        )
        encode_password = user_pass_encoder.encrypt(
            str(pass_entry_box.get()).strip().encode()
        )

        # write encrypted data to config
        with open("runtime/user.bin", "wb") as user_bin, open(
            "runtime/pass.bin", "wb"
        ) as pass_bin:
            # write info to user and password bins
            user_bin.write(encode_user)
            pass_bin.write(encode_password)

        # restore transparency
        root.wm_attributes("-alpha", 1.0)
        # close window
        bhd_login_win.destroy()

    # encoder name window
    bhd_login_win = Toplevel()
    bhd_login_win.title("")
    bhd_login_win.configure(background=custom_window_bg_color)
    bhd_login_win.geometry(
        f'+{str(int(root.geometry().split("+")[1]) + 220)}+'
        f'{str(int(root.geometry().split("+")[2]) + 230)}'
    )
    bhd_login_win.resizable(False, False)
    bhd_login_win.grab_set()
    bhd_login_win.protocol("WM_DELETE_WINDOW", save_exit_function)
    root.wm_attributes("-alpha", 0.90)  # set parent window to be slightly transparent
    bhd_login_win.grid_rowconfigure(0, weight=1)
    bhd_login_win.grid_columnconfigure(0, weight=1)

    # encoder name frame
    bhd_login_frame = Frame(
        bhd_login_win,
        highlightbackground=custom_frame_bg_colors["highlightcolor"],
        highlightthickness=2,
        bg=custom_frame_bg_colors["background"],
        highlightcolor=custom_frame_bg_colors["highlightcolor"],
    )
    bhd_login_frame.grid(column=0, row=0, columnspan=5, sticky=N + S + E + W)
    for e_n_f in range(5):
        bhd_login_frame.grid_columnconfigure(e_n_f, weight=1)
        bhd_login_frame.grid_rowconfigure(e_n_f, weight=1)

    # create label
    user_label = Label(
        bhd_login_frame,
        text="Username",
        background=custom_label_colors["background"],
        fg=custom_label_colors["foreground"],
        font=(set_font, set_font_size, "bold"),
    )
    user_label.grid(row=0, column=0, columnspan=5, sticky=W + N, padx=5, pady=(2, 0))

    # create username entry box
    user_entry_box = Entry(
        bhd_login_frame,
        borderwidth=4,
        fg=custom_entry_colors["foreground"],
        bg=custom_entry_colors["background"],
        width=30,
        font=(set_fixed_font, set_font_size),
    )
    user_entry_box.grid(
        row=1, column=0, columnspan=5, padx=10, pady=(0, 5), sticky=E + W
    )

    # create label
    pass_label = Label(
        bhd_login_frame,
        text="Password",
        background=custom_label_colors["background"],
        fg=custom_label_colors["foreground"],
        font=(set_font, set_font_size, "bold"),
    )
    pass_label.grid(row=2, column=0, columnspan=5, sticky=W + N, padx=5, pady=(2, 0))

    # create password entry box
    pass_entry_box = Entry(
        bhd_login_frame,
        borderwidth=4,
        fg=custom_entry_colors["foreground"],
        bg=custom_entry_colors["background"],
        show="*",
        width=30,
        font=(set_fixed_font, set_font_size),
    )
    pass_entry_box.grid(
        row=3, column=0, columnspan=5, padx=10, pady=(0, 5), sticky=E + W
    )
    pass_entry_box.bind("<Enter>", lambda event: pass_entry_box.config(show=""))
    pass_entry_box.bind("<Leave>", lambda event: pass_entry_box.config(show="*"))

    # custom_entry_box.insert(END, custom_input_parser[config_option][config_key])

    # function to check login credentials
    def check_bhd_login():
        # login to beyondhd image host to confirm username and password
        # start requests session
        session = requests.session()

        # get raw text of web page
        try:
            auth_raw = session.get("https://beyondhd.co/login", timeout=60).text
        except requests.exceptions.ConnectionError:
            messagebox.showerror(
                parent=bhd_login_win, title="Error", message="No internet connection"
            )
            session.close()  # end session
            return  # exit the function

        # if web page didn't return a response
        if not auth_raw:
            messagebox.showerror(
                parent=bhd_login_win,
                title="Error",
                message="Could not access beyondhd.co",
            )
            session.close()  # end session
            return  # exit the function

        # split auth token out of raw web page for later use
        auth_code = (
            auth_raw.split("PF.obj.config.auth_token = ")[1]
            .split(";")[0]
            .replace('"', "")
        )
        if not auth_code:
            messagebox.showerror(
                parent=bhd_login_win, title="Error", message="Could not find auth token"
            )
            session.close()  # end session
            return  # exit the function

        # login payload
        login_payload = {
            "login-subject": str(user_entry_box.get()).strip(),
            "password": str(pass_entry_box.get()).strip(),
            "auth_token": auth_code,
        }

        # login post
        try:
            login_post = session.post(
                "https://beyondhd.co/login", data=login_payload, timeout=60
            )
        except requests.exceptions.ConnectionError:
            session.close()  # end session
            return  # exit the function

        # find user info from login post
        confirm_login = re.search(
            r"CHV.obj.logged_user =(.+);", login_post.text, re.MULTILINE
        )
        if confirm_login:
            messagebox.showinfo(
                parent=bhd_login_win, title="Success", message="Successfully logged in"
            )
            session.close()  # end session

        # if post confirm_login is none
        if not confirm_login:
            messagebox.showerror(
                parent=bhd_login_win,
                title="Error",
                message="Incorrect username and/or password",
            )
            session.close()  # end session
            return  # exit the function

    # create 'Login' button
    login_okay_btn = HoverButton(
        bhd_login_frame,
        text="Check Login",
        command=check_bhd_login,
        borderwidth="3",
        width=10,
        foreground=custom_button_colors["foreground"],
        background=custom_button_colors["background"],
        activeforeground=custom_button_colors["activeforeground"],
        activebackground=custom_button_colors["activebackground"],
        disabledforeground=custom_button_colors["disabledforeground"],
    )
    login_okay_btn.grid(row=4, column=0, columnspan=1, padx=7, pady=5, sticky=S + W)

    # create 'Save' button
    custom_cancel_btn = HoverButton(
        bhd_login_frame,
        text="Save",
        width=10,
        command=save_exit_function,
        borderwidth="3",
        foreground=custom_button_colors["foreground"],
        background=custom_button_colors["background"],
        activeforeground=custom_button_colors["activeforeground"],
        activebackground=custom_button_colors["activebackground"],
        disabledforeground=custom_button_colors["disabledforeground"],
    )
    custom_cancel_btn.grid(row=4, column=4, columnspan=1, padx=7, pady=5, sticky=S + E)

    # decode user and password
    if (
        pathlib.Path("runtime/user.bin").is_file()
        and pathlib.Path("runtime/pass.bin").is_file()
    ):
        # start fernet instance
        pass_user_decoder = Fernet(crypto_key)
        # open both user and pass bin files
        with open("runtime/user.bin", "rb") as user_file, open(
            "runtime/pass.bin", "rb"
        ) as pass_file:
            # decode and insert user name
            decode_user = pass_user_decoder.decrypt(user_file.read())
            user_entry_box.delete(0, END)
            user_entry_box.insert(END, decode_user.decode("utf-8"))
            # decode and insert password
            decode_pass = pass_user_decoder.decrypt(pass_file.read())
            pass_entry_box.delete(0, END)
            pass_entry_box.insert(END, decode_pass.decode("utf-8"))

    bhd_login_win.wait_window()  # wait for window to be closed

    open_all_toplevels()  # re-open all top levels if they exist


screen_shot_window_opened = False


# function to set screenshot count
def screen_shot_count_spinbox(*e_hotkey):
    global screen_shot_window_opened
    # check if window is opened
    if screen_shot_window_opened:
        return  # exit the function
    else:
        screen_shot_window_opened = True

    # hide all top levels if they are opened
    hide_all_toplevels()

    # set parser
    ss_count_parser = ConfigParser()
    ss_count_parser.read(config_file)

    # encoder name window
    ss_count_win = Toplevel()
    ss_count_win.title("SS Count")
    ss_count_win.configure(background=custom_window_bg_color)
    ss_count_win.geometry(
        f'+{str(int(root.geometry().split("+")[1]) + 220)}+'
        f'{str(int(root.geometry().split("+")[2]) + 230)}'
    )
    ss_count_win.resizable(False, False)
    ss_count_win.grab_set()
    ss_count_win.protocol(
        "WM_DELETE_WINDOW",
        lambda: [ss_count_win.destroy(), root.wm_attributes("-alpha", 1.0)],
    )
    root.wm_attributes("-alpha", 0.90)  # set parent window to be slightly transparent
    ss_count_win.grid_rowconfigure(0, weight=1)
    ss_count_win.grid_columnconfigure(0, weight=1)

    # screenshot count frame
    ss_count_frame = Frame(
        ss_count_win,
        highlightbackground=custom_frame_bg_colors["highlightcolor"],
        highlightthickness=2,
        bg=custom_frame_bg_colors["background"],
        highlightcolor=custom_frame_bg_colors["highlightcolor"],
    )
    ss_count_frame.grid(column=0, row=0, columnspan=3, sticky=N + S + E + W)
    for e_n_f in range(3):
        ss_count_frame.grid_columnconfigure(e_n_f, weight=1)
        ss_count_frame.grid_rowconfigure(e_n_f, weight=1)

    # add right click menu to quickly set screenshot count
    def spinbox_right_click_options():
        def popup_spinbox_e_b_menu(
            e,
        ):  # Function for mouse button 3 (right click) to pop up menu
            spinbox_sel_menu.tk_popup(
                e.x_root, e.y_root
            )  # This gets the position of 'e'

        spinbox_sel_menu = Menu(
            ss_spinbox,
            tearoff=False,
            font=(set_font, set_font_size + 1),
            background=custom_button_colors["background"],
            foreground=custom_button_colors["foreground"],
            activebackground=custom_button_colors["activebackground"],
            activeforeground=custom_button_colors["activeforeground"],
        )
        spinbox_sel_menu.add_command(label="20", command=lambda: ss_count.set("20"))
        spinbox_sel_menu.add_command(label="30", command=lambda: ss_count.set("30"))
        spinbox_sel_menu.add_command(label="40", command=lambda: ss_count.set("40"))
        spinbox_sel_menu.add_command(label="50", command=lambda: ss_count.set("50"))
        spinbox_sel_menu.add_command(label="60", command=lambda: ss_count.set("60"))
        spinbox_sel_menu.add_command(label="70", command=lambda: ss_count.set("70"))
        spinbox_sel_menu.add_command(label="80", command=lambda: ss_count.set("80"))
        spinbox_sel_menu.add_command(label="90", command=lambda: ss_count.set("90"))
        spinbox_sel_menu.add_command(label="100", command=lambda: ss_count.set("100"))
        ss_spinbox.bind(
            "<Button-3>", popup_spinbox_e_b_menu
        )  # Uses mouse button 3 (right click) to open
        # custom hover tip
        CustomTooltipLabel(
            anchor_widget=ss_spinbox,
            hover_delay=200,
            background=custom_window_bg_color,
            foreground=custom_label_frame_colors["foreground"],
            font=(set_fixed_font, set_font_size, "bold"),
            text="Right click to quickly select amount",
        )

    # create label
    ss_count_lbl = Label(
        ss_count_frame,
        text="Select desired amount of comparisons",
        background=custom_label_colors["background"],
        fg=custom_label_colors["foreground"],
        font=(set_font, set_font_size, "bold"),
    )
    ss_count_lbl.grid(row=0, column=0, columnspan=3, sticky=W + N, padx=5, pady=(2, 0))

    # create spinbox
    ss_count = StringVar()
    ss_spinbox = Spinbox(
        ss_count_frame,
        from_=20,
        to=100,
        increment=1,
        justify=CENTER,
        wrap=True,
        textvariable=ss_count,
        state="readonly",
        background=custom_spinbox_color["background"],
        foreground=custom_spinbox_color["foreground"],
        highlightthickness=1,
        buttonbackground=custom_spinbox_color["buttonbackground"],
        readonlybackground=custom_spinbox_color["readonlybackground"],
        font=(set_font, set_font_size - 1),
    )
    ss_spinbox.grid(
        row=1, column=0, columnspan=3, padx=40, pady=10, sticky=N + S + E + W
    )
    spinbox_right_click_options()

    # set default value for the spinbox
    if ss_count_parser["screenshot_settings"]["semi_auto_count"] != "":
        ss_count.set(ss_count_parser["screenshot_settings"]["semi_auto_count"])
    else:
        ss_count.set("20")

    # define returned var
    temp_var = ""

    # function to save new name to config.ini
    def custom_okay_func():
        nonlocal temp_var

        # create parser instance
        ss_parser = ConfigParser()
        ss_parser.read(config_file)

        # define temp var
        temp_var = ss_count.get()

        # save setting and exit the window
        if ss_parser["screenshot_settings"]["semi_auto_count"] != ss_count.get():
            ss_parser.set("screenshot_settings", "semi_auto_count", ss_count.get())
            with open(config_file, "w") as ss_config_file:
                ss_parser.write(ss_config_file)
        root.wm_attributes("-alpha", 1.0)  # restore transparency
        ss_count_win.destroy()  # close window

    # create 'OK' button
    ss_okay_btn = HoverButton(
        ss_count_frame,
        text="OK",
        command=custom_okay_func,
        borderwidth="3",
        width=8,
        foreground=custom_button_colors["foreground"],
        background=custom_button_colors["background"],
        activeforeground=custom_button_colors["activeforeground"],
        activebackground=custom_button_colors["activebackground"],
        disabledforeground=custom_button_colors["disabledforeground"],
    )
    ss_okay_btn.grid(row=2, column=2, columnspan=1, padx=7, pady=5, sticky=S + E)

    # create 'Cancel' button
    ss_cancel_btn = HoverButton(
        ss_count_frame,
        text="Cancel",
        width=8,
        command=lambda: [ss_count_win.destroy(), root.wm_attributes("-alpha", 1.0)],
        borderwidth="3",
        foreground=custom_button_colors["foreground"],
        background=custom_button_colors["background"],
        activeforeground=custom_button_colors["activeforeground"],
        activebackground=custom_button_colors["activebackground"],
        disabledforeground=custom_button_colors["disabledforeground"],
    )
    ss_cancel_btn.grid(row=2, column=0, columnspan=1, padx=7, pady=5, sticky=S + W)

    ss_count_win.wait_window()  # wait for window to be closed
    open_all_toplevels()  # re-open all top levels if they exist
    screen_shot_window_opened = False  # set variable back to false

    # return temp_var
    return temp_var


options_menu = Menu(my_menu_bar, tearoff=0, activebackground="dim grey")
my_menu_bar.add_cascade(label="Options", menu=options_menu)
options_menu.add_command(
    label="API Key",
    accelerator="[Ctrl+A]",
    command=lambda: [
        custom_input_prompt(root, "BHD Upload Key:", "bhd_upload_api", "key", "hide")
    ],
)
root.bind(
    "<Control-a>",
    lambda event: custom_input_prompt(
        root, "BHD Upload Key:", "bhd_upload_api", "key", "hide"
    ),
)
options_menu.add_command(
    label="BeyondHD.co", command=bhd_co_login_window, accelerator="[Ctrl+I]"
)
root.bind("<Control-i>", bhd_co_login_window)
options_menu.add_command(
    label="Encoder Name",
    accelerator="[Ctrl+E]",
    command=lambda: [
        custom_input_prompt(root, "Encoder Name:", "encoder_name", "name", "show")
    ],
)
root.bind(
    "<Control-e>",
    lambda event: custom_input_prompt(
        root, "Encoder Name:", "encoder_name", "name", "show"
    ),
)
options_menu.add_command(
    label="Torrent Output Path",
    command=lambda: torrent_path_window_func(
        label_text="Torrent",
        config_set_opt1="torrent_settings",
        config_set_opt2="default_path",
    ),
    accelerator="[Ctrl+T]",
)
root.bind(
    "<Control-t>",
    lambda event: torrent_path_window_func(
        label_text="Torrent",
        config_set_opt1="torrent_settings",
        config_set_opt2="default_path",
    ),
)

options_menu.add_command(
    label="Deluge Injection",
    command=lambda: DelugeWindow(
        master=root,
        options_menu=options_menu,
        custom_window_bg_color=custom_window_bg_color,
        font=set_font,
        font_size=set_font_size,
        custom_label_frame_color_dict=custom_label_frame_colors,
        custom_frame_color_dict=custom_frame_bg_colors,
        custom_button_color_dict=custom_button_colors,
        custom_entry_colors_dict=custom_entry_colors,
        custom_label_colors_dict=custom_label_colors,
    ),
    accelerator="[Ctrl+D]",
)
root.bind(
    "<Control-d>",
    lambda event: DelugeWindow(
        master=root,
        options_menu=options_menu,
        custom_window_bg_color=custom_window_bg_color,
        font=set_font,
        font_size=set_font_size,
        custom_label_frame_color_dict=custom_label_frame_colors,
        custom_frame_color_dict=custom_frame_bg_colors,
        custom_button_color_dict=custom_button_colors,
        custom_entry_colors_dict=custom_entry_colors,
        custom_label_colors_dict=custom_label_colors,
    ),
)

options_menu.add_command(
    label="qBittorrent Injection",
    command=lambda: QBittorrentWindow(
        master=root,
        options_menu=options_menu,
        custom_window_bg_color=custom_window_bg_color,
        font=set_font,
        font_size=set_font_size,
        custom_label_frame_color_dict=custom_label_frame_colors,
        custom_frame_color_dict=custom_frame_bg_colors,
        custom_button_color_dict=custom_button_colors,
        custom_entry_colors_dict=custom_entry_colors,
        custom_label_colors_dict=custom_label_colors,
    ),
    accelerator="[Ctrl+Q]",
)
root.bind(
    "<Control-q>",
    lambda event: QBittorrentWindow(
        master=root,
        options_menu=options_menu,
        custom_window_bg_color=custom_window_bg_color,
        font=set_font,
        font_size=set_font_size,
        custom_label_frame_color_dict=custom_label_frame_colors,
        custom_frame_color_dict=custom_frame_bg_colors,
        custom_button_color_dict=custom_button_colors,
        custom_entry_colors_dict=custom_entry_colors,
        custom_label_colors_dict=custom_label_colors,
    ),
)
options_menu.add_separator()
options_menu.add_command(
    label="Semi-Auto Screenshot Count",
    command=screen_shot_count_spinbox,
    accelerator="[Ctrl+C]",
)
root.bind("<Control-c>", screen_shot_count_spinbox)

options_menu.add_command(
    label="Screen Shot Directory",
    command=lambda: torrent_path_window_func(
        label_text="Image",
        config_set_opt1="image_generation_folder",
        config_set_opt2="path",
    ),
    accelerator="[Ctrl+M]",
)
root.bind(
    "<Control-m>",
    lambda event: torrent_path_window_func(
        label_text="Image",
        config_set_opt1="image_generation_folder",
        config_set_opt2="path",
    ),
)
options_menu.add_separator()

# auto update options menu
auto_update_var = StringVar()
auto_update_var.set(config["check_for_updates"]["value"])
if auto_update_var.get() == "True":
    auto_update_var.set("True")
elif auto_update_var.get() == "False":
    auto_update_var.set(config["check_for_updates"]["value"])


def auto_update_func():
    """save auto update value to config"""

    # parser
    a_u_parser = ConfigParser()
    a_u_parser.read(config_file)

    # write
    a_u_parser.set("check_for_updates", "value", auto_update_var.get())
    with open(config_file, "w") as au_configfile:
        a_u_parser.write(au_configfile)


auto_update_func()
options_submenu2 = Menu(root, tearoff=0, activebackground="dim grey")
options_menu.add_cascade(label="Auto Update", menu=options_submenu2)
options_submenu2.add_radiobutton(
    label="On", variable=auto_update_var, value="True", command=auto_update_func
)
options_submenu2.add_radiobutton(
    label="Off", variable=auto_update_var, value="False", command=auto_update_func
)

options_menu.add_separator()

# theme options menu
theme_var = StringVar()
if config["themes"]["selected_theme"] == "":
    theme_var.set("bhd_theme")
else:
    theme_var.set(config["themes"]["selected_theme"])


def theme_selection_func(start_up):
    """save theme to config"""

    # parser
    theme_parser = ConfigParser()
    theme_parser.read(config_file)

    # write
    theme_parser.set("themes", "selected_theme", theme_var.get())
    with open(config_file, "w") as theme_config_file:
        theme_parser.write(theme_config_file)

    if not start_up:
        # prompt user with message
        messagebox.showinfo(
            parent=root,
            title="Prompt",
            message="Program must be restarted for changes to take effect",
        )


# run theme function on start up
theme_selection_func(start_up=True)
options_theme = Menu(root, tearoff=0, activebackground="dim grey")
options_menu.add_cascade(label="Themes", menu=options_theme)
options_theme.add_radiobutton(
    label="BHDStudio",
    variable=theme_var,
    value="bhd_theme",
    command=lambda: theme_selection_func(start_up=False),
)
options_theme.add_radiobutton(
    label="System Default",
    variable=theme_var,
    value="system_theme",
    command=lambda: theme_selection_func(start_up=False),
)
options_theme.add_radiobutton(
    label="Light",
    variable=theme_var,
    value="light_theme",
    command=lambda: theme_selection_func(start_up=False),
)
options_theme.add_separator()
options_theme.add_radiobutton(
    label="Dark Cyan",
    variable=theme_var,
    value="dark_cyan_theme",
    command=lambda: theme_selection_func(start_up=False),
)
options_theme.add_radiobutton(
    label="Dark Green",
    variable=theme_var,
    value="dark_green_theme",
    command=lambda: theme_selection_func(start_up=False),
)
options_theme.add_radiobutton(
    label="Dark Orange",
    variable=theme_var,
    value="dark_orange_theme",
    command=lambda: theme_selection_func(start_up=False),
)
options_theme.add_radiobutton(
    label="Dark Purple",
    variable=theme_var,
    value="dark_purple_theme",
    command=lambda: theme_selection_func(start_up=False),
)
options_theme.add_radiobutton(
    label="Dark Red",
    variable=theme_var,
    value="dark_red_theme",
    command=lambda: theme_selection_func(start_up=False),
)
options_theme.add_radiobutton(
    label="Dark Yellow",
    variable=theme_var,
    value="dark_yellow_theme",
    command=lambda: theme_selection_func(start_up=False),
)
options_theme.add_separator()
options_theme.add_radiobutton(
    label="Mid Dark Cyan",
    variable=theme_var,
    value="mid_dark_cyan_theme",
    command=lambda: theme_selection_func(start_up=False),
)
options_theme.add_radiobutton(
    label="Mid Dark Green",
    variable=theme_var,
    value="mid_dark_green_theme",
    command=lambda: theme_selection_func(start_up=False),
)
options_theme.add_radiobutton(
    label="Mid Dark Orange",
    variable=theme_var,
    value="mid_dark_orange_theme",
    command=lambda: theme_selection_func(start_up=False),
)
options_theme.add_radiobutton(
    label="Mid Dark Purple",
    variable=theme_var,
    value="mid_dark_purple_theme",
    command=lambda: theme_selection_func(start_up=False),
)
options_theme.add_radiobutton(
    label="Mid Dark Red",
    variable=theme_var,
    value="mid_dark_red_theme",
    command=lambda: theme_selection_func(start_up=False),
)
options_theme.add_radiobutton(
    label="Mid Dark Yellow",
    variable=theme_var,
    value="mid_dark_yellow_theme",
    command=lambda: theme_selection_func(start_up=False),
)


# ui scale menu
def ui_scale_func():
    """function to save UI scale to config"""

    # prompt
    check_message = messagebox.askyesno(
        parent=root,
        title="Prompt!",
        message="This will clear all of your previous saved window position data. "
        "Would you like to continue?\n\nNote: The program will remember new "
        "closed window positions as you use it.\n\n",
    )

    if not check_message:
        return

    # parser
    ui_parser = ConfigParser()
    ui_parser.read(config_file)

    # wipe saved window position data
    ui_parser.remove_section("save_window_locations")

    # set new scale
    ui_parser.set("ui_scale", "value", str(int(ui_var.get()) + int(default_font_size)))

    # write
    with open(config_file, "w") as ui_config_file:
        ui_parser.write(ui_config_file)

    messagebox.showinfo(parent=root, title="Info", message="Please restart the program")

    root.destroy()


ui_var = StringVar()
ui_var.set(str(int(config["ui_scale"]["value"]) - int(default_font_size)))
scale_menu = Menu(root, tearoff=0, activebackground="dim grey")
options_menu.add_cascade(label="UI Scale", menu=scale_menu)
scale_menu.add_radiobutton(
    label="Default",
    variable=ui_var,
    value="0",
    command=ui_scale_func,
)
scale_menu.add_radiobutton(
    label="+10%",
    variable=ui_var,
    value="1",
    command=ui_scale_func,
)
scale_menu.add_radiobutton(
    label="+20%",
    variable=ui_var,
    value="2",
    command=ui_scale_func,
)
scale_menu.add_radiobutton(
    label="+30%",
    variable=ui_var,
    value="3",
    command=ui_scale_func,
)
scale_menu.add_radiobutton(
    label="+40%",
    variable=ui_var,
    value="4",
    command=ui_scale_func,
)
scale_menu.add_radiobutton(
    label="+50%",
    variable=ui_var,
    value="5",
    command=ui_scale_func,
)

options_menu.add_separator()

options_menu.add_command(label="Reset All Settings", command=reset_all_settings)

# tools menu
tools_menu = Menu(my_menu_bar, tearoff=0, activebackground="dim grey")
my_menu_bar.add_cascade(label="Tools", menu=tools_menu)

# command to check for bhdstudio encodes
def check_bhd_dupes(*args):
    """function to get movie and check for BHDStudio encodes"""
    # parser
    check_for_dupe_parser = ConfigParser()
    check_for_dupe_parser.read(config_file)

    # clear some quick variables
    reset_gui()

    # run the search movie function to get a very clean title
    search_movie_global_function()

    # check to see if the user selected a name in search_movie_global_function()
    try:
        source_file_name = source_file_information["imdb_movie_name"]
    except KeyError:
        return

    # run function to check for dupes on beyondhd
    check_bhd = dupe_check(
        api_key=check_for_dupe_parser["bhd_upload_api"]["key"],
        title=source_file_name,
    )

    # if check_bhd returns anything display it
    if check_bhd:
        dupe_check_window(check_bhd)
    elif not check_bhd:
        messagebox.showinfo(
            parent=root,
            title="No BHDStudio Release Found",
            message="No BHDStudio encodes found for title:\n\n"
            + '"'
            + str(source_file_information["imdb_movie_name"])
            + '"',
        )


tools_menu.add_command(
    label="BHDStudio Encodes", command=check_bhd_dupes, accelerator="[Ctrl+B]"
)
root.bind("<Control-b>", lambda event: check_bhd_dupes())

# help menu
help_menu = Menu(my_menu_bar, tearoff=0, activebackground="dim grey")
my_menu_bar.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(
    label="Documentation                 [F1]",  # Open GitHub wiki
    command=lambda: webbrowser.open(
        "https://github.com/jlw4049/BHDStudio-Upload-Tool/wiki"
    ),
)
root.bind(
    "<F1>",
    lambda event: webbrowser.open(
        "https://github.com/jlw4049/BHDStudio-Upload-Tool/wiki"
    ),
)
help_menu.add_command(
    label="Project Page",  # Open GitHub project page
    command=lambda: webbrowser.open("https://github.com/jlw4049/BHDStudio-Upload-Tool"),
)
help_menu.add_command(
    label="Report Error / Feature Request",  # Open GitHub tracker link
    command=lambda: webbrowser.open(
        "https://github.com/jlw4049/BHDStudio-Upload-Tool" "/issues/new/choose"
    ),
)
help_menu.add_command(
    label="Download Latest Release",  # Open GitHub release link
    command=lambda: webbrowser.open(
        "https://github.com/jlw4049/BHDStudio-Upload-Tool/releases"
    ),
)
help_menu.add_separator()
help_menu.add_command(
    label="Info",
    command=lambda: openaboutwindow(
        main_root_title,
        custom_window_bg_color,
        custom_label_frame_colors["background"],
        custom_label_frame_colors["foreground"],
        custom_text_color["foreground"],
        custom_text_color["background"],
        set_font_size,
    ),
)  # Opens about window


# function to enable/disable main GUI buttons
def generate_button_checker():
    if (
        source_file_path.get() != "" and encode_file_path.get() != ""
    ):  # if source/encode is not empty strings
        open_torrent_window_button.config(state=NORMAL)
        auto_screens_multi_btn.config(state=NORMAL)
        view_loaded_script.config(state=NORMAL)
        check_screens = parse_screen_shots()
        # if check screens was not False
        if check_screens:
            generate_nfo_button.config(state=NORMAL)
            parse_and_upload.config(state=NORMAL)
            # if nfo is not blank and torrent file is exists
            if (
                nfo_info_var.get() != ""
                and pathlib.Path(torrent_file_path.get()).is_file()
            ):
                open_uploader_button.config(state=NORMAL)
    else:  # if source/encode is empty strings
        generate_nfo_button.config(state=DISABLED)
        open_torrent_window_button.config(state=DISABLED)
        parse_and_upload.config(state=DISABLED)
        open_uploader_button.config(state=DISABLED)
        auto_screens_multi_btn.config(state=DISABLED)
        view_loaded_script.config(state=DISABLED)
    root.after(50, generate_button_checker)  # loop to constantly check


# start button checker loop
generate_button_checker()


# duplicate check window
def dupe_check_window(dup_release_dict):
    """window to display duplicate releases"""

    # set parser
    movie_window_parser = ConfigParser()
    movie_window_parser.read(config_file)

    # decode imdb img for use with the buttons
    decode_resize_imdb_image = Image.open(BytesIO(base64.b64decode(imdb_icon))).resize(
        (35, 35)
    )
    imdb_img = ImageTk.PhotoImage(decode_resize_imdb_image)

    # decode tmdb img for use with the buttons
    decode_resize_tmdb_image = Image.open(BytesIO(base64.b64decode(tmdb_icon))).resize(
        (35, 35)
    )
    tmdb_img = ImageTk.PhotoImage(decode_resize_tmdb_image)

    # decode seed/leech arrow img for use with a label
    decode_resize_seeds_image = Image.open(
        BytesIO(base64.b64decode(seed_leech_arrow))
    ).resize((35, 35))
    seed_leech_img = ImageTk.PhotoImage(decode_resize_seeds_image)

    def movie_info_exit_function():
        """movie window exit function"""

        # set parser
        exit_movie_window_parser = ConfigParser()
        exit_movie_window_parser.read(config_file)

        # save window position/geometry
        if movie_info_window.wm_state() == "normal":
            if (
                exit_movie_window_parser["save_window_locations"]["dupe_viewer"]
                != movie_info_window.geometry()
            ):
                exit_movie_window_parser.set(
                    "save_window_locations",
                    "dupe_viewer",
                    movie_info_window.geometry(),
                )
                with open(config_file, "w") as root_exit_config_file:
                    exit_movie_window_parser.write(root_exit_config_file)

        # close movie info window
        movie_info_window.destroy()

    # movie info window
    movie_info_window = Toplevel()
    movie_info_window.configure(
        background=custom_window_bg_color
    )  # Set's the background color
    movie_info_window.title("Duplicate Releases")  # Toplevel Title
    if movie_window_parser["save_window_locations"]["dupe_viewer"] != "":
        movie_info_window.geometry(
            movie_window_parser["save_window_locations"]["dupe_viewer"]
        )
    movie_info_window.grab_set()
    movie_info_window.protocol("WM_DELETE_WINDOW", movie_info_exit_function)

    # Row/Grid configures
    for m_i_w_c in range(6):
        movie_info_window.grid_columnconfigure(m_i_w_c, weight=1)
    for m_i_w_r in range(4):
        movie_info_window.grid_rowconfigure(m_i_w_r, weight=1)
    # Row/Grid configures

    # Set dynamic listbox frame
    movie_listbox_frame = Frame(
        movie_info_window, bg=custom_frame_bg_colors["background"]
    )
    movie_listbox_frame.grid(
        column=0, columnspan=6, row=0, padx=5, pady=(5, 3), sticky=N + S + E + W
    )
    movie_listbox_frame.grid_rowconfigure(0, weight=1)
    movie_listbox_frame.grid_columnconfigure(0, weight=1)

    right_scrollbar = Scrollbar(movie_listbox_frame, orient=VERTICAL)  # Scrollbars
    bottom_scrollbar = Scrollbar(movie_listbox_frame, orient=HORIZONTAL)

    # Create listbox
    movie_listbox = Listbox(
        movie_listbox_frame,
        xscrollcommand=bottom_scrollbar.set,
        activestyle="none",
        yscrollcommand=right_scrollbar.set,
        bd=2,
        height=10,
        selectmode=SINGLE,
        font=(set_font, set_font_size + 2),
        bg=custom_listbox_color["background"],
        fg=custom_listbox_color["foreground"],
        selectbackground=custom_listbox_color["selectbackground"],
        selectforeground=custom_listbox_color["selectforeground"],
    )
    movie_listbox.grid(row=0, column=0, columnspan=5, sticky=N + E + S + W)

    # add scrollbars to the listbox
    right_scrollbar.config(command=movie_listbox.yview)
    right_scrollbar.grid(row=0, column=5, rowspan=2, sticky=N + W + S)
    bottom_scrollbar.config(command=movie_listbox.xview)
    bottom_scrollbar.grid(row=1, column=0, sticky=W + E + N)

    def update_movie_listbox(movie_dict):
        """update the list box with supplied dictionary"""

        # # loop through the keys (movie titles) and display them in the listbox
        for key in movie_dict.keys():
            movie_listbox.insert(END, key)

        # function that is run each time a movie is selected to update all the information in the window
        def update_movie_info(event):
            selection = event.widget.curselection()  # get current selection
            # if there is a selection
            if selection:
                # define index of selection
                movie_listbox_index = selection[0]
                movie_data = event.widget.get(movie_listbox_index)

                # update link label
                bhd_link_label.config(
                    text="Link: " + str(movie_dict[movie_data]["url"])[:60] + "..."
                )
                bhd_link_label.bind(
                    "<Button-1>",
                    lambda e: webbrowser.open(url=str(movie_dict[movie_data]["url"])),
                )

                # update resolution label
                resolution_lbl.config(
                    text="Resolution: " + str(movie_dict[movie_data]["type"])
                )

                # update size label
                math_to_gb = str(
                    round(float(movie_dict[movie_data]["size"]) / 1000000000, 2)
                )
                movie_size_lbl.config(text="Size (GB): " + math_to_gb)

                # update created_on_lbl label
                created_on_lbl.config(
                    text="Uploaded: "
                    + str(movie_dict[movie_data]["created_at"].split(" ")[0])
                )

                # update seed_leech_label_numbers label
                seed_leech_label.config(
                    compound="left",
                    text=" "
                    + str(movie_dict[movie_data]["seeders"])
                    + " / "
                    + str(movie_dict[movie_data]["leechers"]),
                )

                # update imdb and tmdb entry box's
                imdb_id_var.set(movie_dict[movie_data]["imdb_id"])
                tmdb_id_var.set(movie_dict[movie_data]["tmdb_id"].replace("movie/", ""))

                # update text imdb_button2
                imdb_button2.config(
                    text="  " + str(movie_dict[movie_data]["imdb_rating"])
                )

                # update text tmdb_button2
                tmdb_button2.config(
                    text="  " + str(movie_dict[movie_data]["tmdb_rating"])
                )

        # bind listbox select event to the updater
        movie_listbox.bind("<<ListboxSelect>>", update_movie_info)

    # information frame
    information_frame = Frame(
        movie_info_window, bd=0, bg=custom_frame_bg_colors["background"]
    )
    information_frame.grid(
        column=0, row=3, columnspan=3, padx=5, pady=(5, 3), sticky=E + W
    )
    for i_f_g_r in range(4):
        information_frame.grid_rowconfigure(i_f_g_r, weight=1)
    for i_f_g_c in range(3):
        information_frame.grid_columnconfigure(i_f_g_c, weight=1)

    # beyondhd clickable label
    bhd_link_label = Label(
        information_frame,
        borderwidth=0,
        cursor="hand2",
        background=custom_label_colors["background"],
        fg="#0000FF",
        font=(set_fixed_font, set_font_size, "bold"),
    )
    bhd_link_label.grid(
        row=0, column=0, columnspan=3, sticky=W + E, padx=5, pady=(5, 2)
    )

    # resolution label
    resolution_lbl = Label(
        information_frame,
        background=custom_label_colors["background"],
        fg=custom_label_colors["foreground"],
        font=(set_fixed_font, set_font_size + 1),
        width=8,
        text="Resolution: ",
    )
    resolution_lbl.grid(row=1, column=0, sticky=W + E, padx=(1, 5), pady=(5, 2))

    # size label
    movie_size_lbl = Label(
        information_frame,
        background=custom_label_colors["background"],
        fg=custom_label_colors["foreground"],
        font=(set_fixed_font, set_font_size + 1),
        width=8,
        text="Size (GB)",
    )
    movie_size_lbl.grid(row=1, column=1, sticky=W + E, padx=(1, 5), pady=(5, 2))

    # created on label
    created_on_lbl = Label(
        information_frame,
        background=custom_label_colors["background"],
        fg=custom_label_colors["foreground"],
        font=(set_fixed_font, set_font_size + 1),
        width=12,
        text="Uploaded: ",
    )
    created_on_lbl.grid(row=1, column=2, sticky=W + E, padx=(1, 5), pady=(5, 2))

    # seeds label
    seed_leech_label = Label(
        information_frame,
        image=seed_leech_img,
        borderwidth=0,
        background=custom_label_colors["background"],
        fg=custom_label_colors["foreground"],
        font=(set_fixed_font, set_font_size),
        text="        ",
    )
    seed_leech_label.grid(row=2, column=0, sticky=W + E, padx=5, pady=(5, 2))
    seed_leech_label.image = seed_leech_img

    # downloaded amount label
    times_downloaded_lbl = Label(
        information_frame,
        background=custom_label_colors["background"],
        fg=custom_label_colors["foreground"],
        font=(set_fixed_font, set_font_size + 1),
    )
    times_downloaded_lbl.grid(row=2, column=1, sticky=W + E, padx=(1, 5), pady=(5, 2))

    # imdb/tmdb info frame
    imdb_tmdb_frame = Frame(
        information_frame, bd=0, bg=custom_frame_bg_colors["background"]
    )
    imdb_tmdb_frame.grid(
        column=0, row=3, columnspan=6, padx=5, pady=(5, 3), sticky=E + W
    )
    imdb_tmdb_frame.grid_rowconfigure(0, weight=1)
    imdb_tmdb_frame.grid_rowconfigure(1, weight=1)
    imdb_tmdb_frame.grid_columnconfigure(0, weight=1)
    imdb_tmdb_frame.grid_columnconfigure(1, weight=1000)
    imdb_tmdb_frame.grid_columnconfigure(2, weight=1000)
    imdb_tmdb_frame.grid_columnconfigure(3, weight=1)

    # imdb clickable icon button
    imdb_button2 = Button(
        imdb_tmdb_frame,
        image=imdb_img,
        borderwidth=0,
        cursor="hand2",
        bg=custom_window_bg_color,
        activebackground=custom_window_bg_color,
        command=open_imdb_link,
        text="    ",
        compound="left",
        fg=custom_label_colors["foreground"],
    )
    imdb_button2.grid(row=0, column=0, rowspan=2, padx=5, pady=(5, 2), sticky=W)
    imdb_button2.photo = imdb_img

    # imdb entry box internal
    imdb_entry_box2 = Entry(
        imdb_tmdb_frame,
        borderwidth=4,
        textvariable=imdb_id_var,
        fg=custom_entry_colors["foreground"],
        bg=custom_entry_colors["background"],
        disabledforeground=custom_entry_colors["disabledforeground"],
        disabledbackground=custom_entry_colors["disabledbackground"],
        font=(set_fixed_font, set_font_size),
    )
    imdb_entry_box2.grid(row=0, column=1, rowspan=2, padx=5, pady=(5, 2), sticky=W)

    # tmdb clickable icon button
    tmdb_button2 = Button(
        imdb_tmdb_frame,
        image=tmdb_img,
        borderwidth=0,
        cursor="hand2",
        bg=custom_window_bg_color,
        activebackground=custom_window_bg_color,
        command=open_tmdb_link,
        text="    ",
        compound="left",
        fg=custom_label_colors["foreground"],
    )
    tmdb_button2.grid(row=0, column=2, rowspan=2, padx=5, pady=(5, 2), sticky=E)
    tmdb_button2.photo = tmdb_img

    # tmdb internal entry box
    tmdb_entry_box2 = Entry(
        imdb_tmdb_frame,
        borderwidth=4,
        textvariable=tmdb_id_var,
        fg=custom_entry_colors["foreground"],
        bg=custom_entry_colors["background"],
        disabledforeground=custom_entry_colors["disabledforeground"],
        disabledbackground=custom_entry_colors["disabledbackground"],
        font=(set_fixed_font, set_font_size),
    )
    tmdb_entry_box2.grid(row=0, column=3, rowspan=2, padx=5, pady=(5, 2), sticky=E)

    # focus's id window
    movie_info_window.focus_set()

    # clear movie list box
    movie_listbox.delete(0, END)

    # run the function to update the listbox
    update_movie_listbox(dup_release_dict)

    # wait for window to close
    movie_info_window.wait_window()


def check_for_latest_program_updates():
    """check program for updates against the project GitHub releases"""

    def error_message_open_browser():
        auto_error = messagebox.askyesno(
            parent=root,
            title="Error",
            message="There was an error automatically getting the download, would you "
            "like to manually update? ",
        )
        # if user selects yes
        if auto_error:
            webbrowser.open(release_link)  # open link to the latest release page
            update_window.destroy()  # close update window

    # update parser
    check_for_update_parser = ConfigParser()
    check_for_update_parser.read(config_file)

    # if check for updates is disabled
    if check_for_update_parser["check_for_updates"]["value"] == "False":
        return  # exit function

    # if GitHub token is not supplied exit this update function
    if github_token == "":
        return  # exit function

    # repo release link
    release_link = (
        "https://api.github.com/repos/jlw4049/BHDStudio-Upload-Tool/releases/latest"
    )

    # header to be sent with the token
    headers = {"Authorization": "token " + github_token}

    # parse release page without GitHub api
    try:
        parse_release_page = requests.get(release_link, headers=headers, timeout=60)
    except requests.exceptions.ConnectionError:
        error_message_open_browser()
        return  # exit function

    # if extracted version is equal to current version exit this function
    if parse_release_page.json()["name"] == main_root_title:
        return  # program is up-to-date, exit the function

    # if extracted version is the same as skipped version exit this function
    if (
        check_for_update_parser["check_for_updates"]["ignore_version"]
        == parse_release_page.json()["name"]
    ):
        return  # newest version is set to be skipped

    # updater window
    update_window = Toplevel()
    update_window.title("Update")
    update_window.configure(background=custom_window_bg_color)
    update_window.geometry(
        f'{800}x{540}+{root.geometry().split("+")[1]}+{root.geometry().split("+")[2]}'
    )
    for e_w in range(4):
        update_window.grid_columnconfigure(e_w, weight=1)
    update_window.grid_rowconfigure(0, weight=1)
    update_window.grid_rowconfigure(1, weight=1)
    update_window.grid_rowconfigure(2, weight=1)
    update_window.grab_set()  # only allow input on update window until it's closed
    update_window.wm_transient(root)  # bring window above the main window

    # basic update label to show parsed version
    update_label = Label(
        update_window,
        text=parse_release_page.json()["name"],
        bd=0,
        relief=SUNKEN,
        background=custom_label_colors["background"],
        fg=custom_label_colors["foreground"],
        font=(set_font, set_font_size + 4, "bold"),
    )
    update_label.grid(column=0, row=0, columnspan=4, pady=3, padx=3, sticky=W + E)

    # scrolled update window
    update_scrolled = scrolledtextwidget.ScrolledText(
        update_window,
        bg=custom_scrolled_text_widget_color["background"],
        fg=custom_scrolled_text_widget_color["foreground"],
        bd=4,
        wrap=WORD,
    )
    update_scrolled.grid(
        row=1, column=0, columnspan=4, pady=5, padx=5, sticky=E + W + N + S
    )
    update_scrolled.tag_configure(
        "bold_color",
        background=custom_entry_colors["disabledbackground"],
        foreground=custom_label_frame_colors["foreground"],
        font=12,
        justify=CENTER,
    )
    update_scrolled.tag_configure(
        "version_color",
        background=custom_entry_colors["disabledbackground"],
        foreground=custom_entry_colors["foreground"],
        font=(set_fixed_font, set_font_size),
        justify=LEFT,
    )
    update_scrolled.insert(
        END,
        f"Current version: {main_root_title}\nVersion found: {parse_release_page.json()['name']}\n\n",
        "version_color",
    )
    update_scrolled.insert(END, "Patch Notes\n", "bold_color")
    update_scrolled.tag_configure(
        "highlight_color",
        background=custom_button_colors["background"],
        foreground=custom_button_colors["foreground"],
        font=(set_fixed_font, set_font_size),
    )
    update_scrolled.insert(END, parse_release_page.json()["body"], "highlight_color")
    update_scrolled.config(state=DISABLED)

    # update button frame
    update_frame = Frame(update_window, bd=0, bg=custom_frame_bg_colors["background"])
    update_frame.grid(column=0, row=2, columnspan=4, padx=5, pady=(5, 3), sticky=E + W)
    update_frame.grid_rowconfigure(0, weight=1)
    update_frame.grid_columnconfigure(0, weight=1)
    update_frame.grid_columnconfigure(1, weight=50)
    update_frame.grid_columnconfigure(2, weight=50)
    update_frame.grid_columnconfigure(3, weight=1)

    # close updater button
    close_updater_btn = HoverButton(
        update_frame,
        text="Close",
        command=update_window.destroy,
        borderwidth="3",
        width=14,
        foreground=custom_button_colors["foreground"],
        background=custom_button_colors["background"],
        activeforeground=custom_button_colors["activeforeground"],
        activebackground=custom_button_colors["activebackground"],
        disabledforeground=custom_button_colors["disabledforeground"],
    )
    close_updater_btn.grid(
        row=0, column=0, columnspan=1, padx=10, pady=(5, 4), sticky=S + W
    )

    # ignore update function
    def ignore_update_function():
        # parser
        i_a_u_parser = ConfigParser()
        i_a_u_parser.read(config_file)
        # write
        i_a_u_parser.set("check_for_updates", "value", "False")
        with open(config_file, "w") as au_configfile:
            i_a_u_parser.write(au_configfile)
        # close update window
        update_window.destroy()

    # ignore updates button
    ignore_updates = HoverButton(
        update_frame,
        text="Ignore Updates",
        command=ignore_update_function,
        borderwidth="3",
        width=14,
        foreground=custom_button_colors["foreground"],
        background=custom_button_colors["background"],
        activeforeground=custom_button_colors["activeforeground"],
        activebackground=custom_button_colors["activebackground"],
        disabledforeground=custom_button_colors["disabledforeground"],
    )
    ignore_updates.grid(
        row=0, column=1, columnspan=1, padx=10, pady=(5, 4), sticky=S + W
    )

    # ignore update function
    def skip_version_function():
        # parser
        skip_version_parser = ConfigParser()
        skip_version_parser.read(config_file)

        # write the version to skip
        if (
            skip_version_parser["check_for_updates"]["ignore_version"]
            != parse_release_page.json()["name"]
        ):
            skip_version_parser.set(
                "check_for_updates", "ignore_version", parse_release_page.json()["name"]
            )
            with open(config_file, "w") as version_config:
                skip_version_parser.write(version_config)

        # close update window
        update_window.destroy()

    # skip version button
    skip_version = HoverButton(
        update_frame,
        text="Skip Version",
        command=skip_version_function,
        borderwidth="3",
        width=14,
        foreground=custom_button_colors["foreground"],
        background=custom_button_colors["background"],
        activeforeground=custom_button_colors["activeforeground"],
        activebackground=custom_button_colors["activebackground"],
        disabledforeground=custom_button_colors["disabledforeground"],
    )
    skip_version.grid(row=0, column=2, columnspan=1, padx=10, pady=(5, 4), sticky=S + E)

    # update button function
    def update_program():
        # get bhdstudio upload tool download
        try:
            request_download = requests.get(
                parse_release_page.json()["assets"][0]["browser_download_url"],
                timeout=60,
            )
        except requests.exceptions.ConnectionError:
            messagebox.showerror(
                parent=update_window, title="Error", message="Automatic update failed"
            )
            return  # exit function

        # if requests passes internet check but for some reason timeouts
        if not request_download:
            messagebox.showerror(
                parent=update_window, title="Error", message="Automatic update failed"
            )
            return  # exit function

        # if download was successful
        if request_download.ok:
            # delete old exe if it exists (it shouldn't)
            try:
                pathlib.Path("OLD.exe").unlink(missing_ok=True)
            except PermissionError:
                pass

            # rename current running exe
            pathlib.Path("BHDStudioUploadTool.exe").rename("OLD.exe")

            # use zipfile module to unzip latest update
            with zipfile.ZipFile(BytesIO(request_download.content)) as dl_zipfile:
                dl_zipfile.extractall()

            # check to ensure new exe is moved
            if pathlib.Path("BHDStudioUploadTool.exe").is_file():
                # prompt update message box
                messagebox.showinfo(
                    parent=update_window,
                    title="Update Status",
                    message="Update complete, program will now restart and automatically clean "
                    "update files",
                )

                # use subprocess to open the new download
                subprocess.Popen(
                    pathlib.Path(pathlib.Path.cwd() / "BHDStudioUploadTool.exe"),
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )

                # close update window
                update_window.destroy()

                # close main gui
                root.destroy()

                # exit function to kill thread
                return
            else:
                # if program couldn't move new exe
                messagebox.showinfo(
                    parent=update_window,
                    title="Update Status",
                    message="Could not move updated exe to main directory, please do this manually",
                )

                # open main directory
                webbrowser.open(str(pathlib.Path.cwd()))

                # close update window
                update_window.destroy()

                # close main gui
                root.destroy()

                # exit function to kill thread
                return

        # if downloaded exe is not detected
        if not pathlib.Path("BHDStudioUploadTool.exe").is_file():
            # open message box failed message
            messagebox.showinfo(
                parent=update_window,
                title="Update Status",
                message="Update failed! Opening link to manual update",
            )
            webbrowser.open(
                parse_release_page.json()["assets"][0]["browser_download_url"]
            )  # open browser for manual download
            return  # exit function

    # update button
    update_button = HoverButton(
        update_frame,
        text="Update",
        command=update_program,
        borderwidth="3",
        width=14,
        foreground=custom_button_colors["foreground"],
        background=custom_button_colors["background"],
        activeforeground=custom_button_colors["activeforeground"],
        activebackground=custom_button_colors["activebackground"],
        disabledforeground=custom_button_colors["disabledforeground"],
    )
    update_button.grid(
        row=0, column=3, columnspan=1, padx=10, pady=(5, 4), sticky=S + E
    )

    update_window.grab_set()  # Brings attention to this window until it's closed


def open_script_in_viewer(filename):
    """open script file"""
    if sys.platform == "win32":
        subprocess.run(["cmd", "/c", pathlib.Path(filename)])
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, pathlib.Path(filename)])


# start check for updates function in a new thread
if app_type == "bundled":
    check_for_latest_program_updates()

# if program was opened with a dropped video file load it into the source function
if cli_command:
    source_input_function(cli_command)


# clean update files
def clean_update_files():
    if pathlib.Path("OLD.exe").is_file():
        try:
            # delete old exe
            pathlib.Path("OLD.exe").unlink(missing_ok=True)
        except PermissionError:
            pass


if app_type == "bundled":
    root.after(5000, clean_update_files)

# tkinter mainloop
root.mainloop()
