import base64
import math
import os
import pathlib
import re
import sys
import threading
import tkinter.scrolledtext as scrolledtextwidget
import webbrowser
from configparser import ConfigParser
from ctypes import windll
from idlelib.tooltip import Hovertip
from io import BytesIO
from tkinter import filedialog, StringVar, ttk, messagebox, NORMAL, DISABLED, N, S, W, E, Toplevel, \
    LabelFrame, END, Label, Checkbutton, OptionMenu, Entry, HORIZONTAL, SUNKEN, Button, TclError, font, Menu, Text, \
    INSERT, colorchooser, Frame, Scrollbar, VERTICAL, PhotoImage, BooleanVar, Listbox, SINGLE

import pyperclip
import requests
import torf
from PIL import Image, ImageTk
from TkinterDnD2 import *
from imdb import Cinemagoer
from pymediainfo import MediaInfo
from torf import Torrent

from Packages.About import openaboutwindow
from Packages.icon import base_64_icon, imdb_icon, tmdb_icon, bhd_upload_icon, bhd_upload_icon_disabled
from Packages.show_streams import stream_menu
from Packages.tmdb_key import tmdb_api_key

# Set variable to True if you want errors to pop up in window + console, False for console only
enable_error_logger = True  # Change this to false if you don't want to log errors to pop up window

# Set main window title variable
main_root_title = "BHDStudio Upload Tool v1.1 Beta"

# create runtime folder if it does not exist
pathlib.Path(pathlib.Path.cwd() / 'Runtime').mkdir(parents=True, exist_ok=True)

# define config file and settings
config_file = 'Runtime/config.ini'  # Creates (if doesn't exist) and defines location of config.ini
config = ConfigParser()
config.read(config_file)

# general settings
if not config.has_section('torrent_settings'):
    config.add_section('torrent_settings')
if not config.has_option('torrent_settings', 'tracker_url'):
    config.set('torrent_settings', 'tracker_url', '')
if not config.has_section('encoder_name'):
    config.add_section('encoder_name')
if not config.has_option('encoder_name', 'name'):
    config.set('encoder_name', 'name', '')
if not config.has_section('bhd_upload_api'):
    config.add_section('bhd_upload_api')
if not config.has_option('bhd_upload_api', 'key'):
    config.set('bhd_upload_api', 'key', '')
if not config.has_section('live_release'):
    config.add_section('live_release')
if not config.has_option('live_release', 'password'):
    config.set('live_release', 'password', '')
if not config.has_option('live_release', 'value'):
    config.set('live_release', 'value', '')

# window location settings
if not config.has_section('save_window_locations'):
    config.add_section('save_window_locations')
if not config.has_option('save_window_locations', 'bhdstudiotool'):
    config.set('save_window_locations', 'bhdstudiotool', '')
if not config.has_option('save_window_locations', 'torrent_window'):
    config.set('save_window_locations', 'torrent_window', '')
if not config.has_option('save_window_locations', 'nfo_pad'):
    config.set('save_window_locations', 'nfo_pad', '')
if not config.has_option('save_window_locations', 'uploader'):
    config.set('save_window_locations', 'uploader', '')
if not config.has_option('save_window_locations', 'movie_info'):
    config.set('save_window_locations', 'movie_info', '')
if not config.has_option('save_window_locations', 'about_window'):
    config.set('save_window_locations', 'about_window', '')

with open(config_file, 'w') as configfile:
    config.write(configfile)


# root
def root_exit_function():
    def save_config_information_root():
        # root exit parser
        root_exit_parser = ConfigParser()
        root_exit_parser.read(config_file)

        # save main gui window position/geometry
        if root.wm_state() == 'normal':
            if root_exit_parser['save_window_locations']['bhdstudiotool'] != root.geometry():
                if int(root.geometry().split('x')[0]) >= root_window_width or \
                        int(root.geometry().split('x')[1].split('+')[0]) >= root_window_height:
                    root_exit_parser.set('save_window_locations', 'bhdstudiotool', root.geometry())
                    with open(config_file, 'w') as root_exit_config_file:
                        root_exit_parser.write(root_exit_config_file)

    # check for opened windows before closing
    open_tops = False  # Set variable for open toplevel windows
    for widget in root.winfo_children():  # Loop through roots children
        if isinstance(widget, Toplevel):  # If any of roots children is a TopLevel window
            open_tops = True  # Set variable for open tops to True
    if open_tops:  # If open_tops is True
        confirm_exit = messagebox.askyesno(title='Prompt', message="Are you sure you want to exit the program?\n\n"
                                                                   "Warning: This will close all windows", parent=root)
        if confirm_exit:  # If user wants to exit, kill app and all of it's children
            save_config_information_root()
            root.destroy()  # root destroy
    if not open_tops:  # If no top levels are found, exit the program without prompt
        save_config_information_root()
        root.destroy()  # root destroy


root = TkinterDnD.Tk()
root.title(main_root_title)
root.iconphoto(True, PhotoImage(data=base_64_icon))
root.configure(background="#363636")
root_window_height = 660
root_window_width = 720
if config['save_window_locations']['bhdstudiotool'] == '':
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_coordinate = int((screen_width / 2) - (root_window_width / 2))
    y_coordinate = int((screen_height / 2) - (root_window_height / 2))
    root.geometry(f"{root_window_width}x{root_window_height}+{x_coordinate}+{y_coordinate}")
elif config['save_window_locations']['bhdstudiotool'] != '':
    root.geometry(config['save_window_locations']['bhdstudiotool'])
root.protocol('WM_DELETE_WINDOW', root_exit_function)

# root_pid = os.getpid()  # Get root process ID

# Block of code to fix DPI awareness issues on Windows 7 or higher
try:
    windll.shcore.SetProcessDpiAwareness(2)  # if your Windows version >= 8.1
except(Exception,):
    windll.user32.SetProcessDPIAware()  # Windows 8.0 or less
# Block of code to fix DPI awareness issues on Windows 7 or higher

for n in range(4):
    root.grid_columnconfigure(n, weight=1)
for n in range(5):
    root.grid_rowconfigure(n, weight=1)


class HoverButton(Button):
    def __init__(self, master, **kw):
        Button.__init__(self, master=master, **kw)
        self.defaultBackground = self["foreground"]
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self['foreground'] = self['activeforeground']

    def on_leave(self, e):
        self['foreground'] = self.defaultBackground


detect_font = font.nametofont("TkDefaultFont")  # Get default font value into Font object
set_font = detect_font.actual().get("family")
set_font_size = detect_font.actual().get("size")
detect_fixed_font = font.nametofont("TkFixedFont")
set_fixed_font = detect_fixed_font.actual().get("family")
color1 = "#434547"

# Custom Tkinter Theme-----------------------------------------
custom_style = ttk.Style()
custom_style.theme_create('jlw_style', parent='alt', settings={
    # Notebook Theme Settings -------------------
    "TNotebook": {"configure": {"tabmargins": [5, 5, 5, 0], 'background': "#565656"}},
    "TNotebook.Tab": {
        "configure": {"padding": [5, 1], "background": 'grey', 'foreground': 'white', 'focuscolor': ''},
        "map": {"background": [("selected", '#434547')], "expand": [("selected", [1, 1, 1, 0])]}},
    # Notebook Theme Settings -------------------
    # ComboBox Theme Settings -------------------
    'TCombobox': {'configure': {'selectbackground': '#23272A', 'fieldbackground': '#23272A',
                                'background': 'white', 'foreground': 'white'}}},
                          # ComboBox Theme Settings -------------------
                          )
custom_style.theme_use('jlw_style')  # Enable the use of the custom theme
custom_style.layout('text.Horizontal.TProgressbar',
                    [('Horizontal.Progressbar.trough',
                      {'children': [('Horizontal.Progressbar.pbar',
                                     {'side': 'left', 'sticky': 'ns'})],
                       'sticky': 'nswe'}),
                     ('Horizontal.Progressbar.label', {'sticky': 'nswe'})])
# set initial text
custom_style.configure('text.Horizontal.TProgressbar', text='', anchor='center', background="#3498db")


# custom_style.configure("custom.Horizontal.TProgressbar", background="#3498db")

# ------------------------------------------ Custom Tkinter Theme


# Logger class, handles all traceback/stdout errors for program, writes to file and to window -------------------------
class Logger(object):  # Logger class, this class puts stderr errors into a window and file at the same time
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
                info_scrolled.insert(END, f'{str(message)}\n')
            info_scrolled.see(END)
            info_scrolled.config(state=DISABLED)
        except (NameError, TclError):
            error_window = Toplevel()
            error_window.title('Traceback Error(s)')
            error_window.configure(background="#434547")
            window_height = 400
            window_width = 600
            error_window.geometry(f'{window_width}x{window_height}+{root.geometry().split("+")[1]}+'
                                  f'{root.geometry().split("+")[2]}')
            for e_w in range(4):
                error_window.grid_columnconfigure(e_w, weight=1)
            error_window.grid_rowconfigure(0, weight=1)
            info_scrolled = scrolledtextwidget.ScrolledText(error_window, tabs=10, spacing2=3, spacing1=2,
                                                            spacing3=3)
            info_scrolled.grid(row=0, column=0, columnspan=4, pady=5, padx=5, sticky=E + W + N + S)
            info_scrolled.configure(bg='black', fg='#CFD2D1', bd=8)
            info_scrolled.insert(END, message)
            info_scrolled.see(END)
            info_scrolled.config(state=DISABLED)

            report_error = HoverButton(error_window, text='Report Error',
                                       command=lambda: webbrowser.open('https://github.com/jlw4049/BHDStudio-Upload-'
                                                                       'Tool/issues/new?assignees=jlw4049&labels=bug'
                                                                       '&template=bug_report.md&title='),
                                       foreground='white', background='#23272A', borderwidth='3',
                                       activeforeground="#3498db", activebackground="#23272A")
            report_error.grid(row=1, column=3, columnspan=1, padx=10, pady=(5, 4), sticky=S + E + N)

            force_close_root = HoverButton(error_window, text='Force Close Program', command=root.destroy,
                                           foreground='white', background='#23272A', borderwidth='3',
                                           activeforeground="#3498db", activebackground="#23272A")
            force_close_root.grid(row=1, column=0, columnspan=1, padx=10, pady=(5, 4), sticky=S + W + N)

            def right_click_menu_func(x_y_pos):  # Function for mouse button 3 (right click) to pop up menu
                right_click_menu.tk_popup(x_y_pos.x_root, x_y_pos.y_root)  # This gets the position of cursor

            right_click_menu = Menu(info_scrolled, tearoff=False)  # This is the right click menu
            right_click_menu.add_command(label='Copy to clipboard', command=lambda: pyperclip.copy(
                info_scrolled.get(1.0, END).strip()))
            info_scrolled.bind('<Button-3>', right_click_menu_func)  # Uses mouse button 3 to open the menu
            Hovertip(info_scrolled, 'Right click to copy', hover_delay=1200)  # Hover tip tool-tip
            error_window.grab_set()  # Brings attention to this window until it's closed
            root.bell()  # Error bell sound

    def flush(self):
        pass

    def __exit__(self):  # Class exit function
        sys.stderr = sys.__stderr__  # Redirect stderr back to original stderr
        # self.error_log_file.close()  # Close file


def start_logger():
    if enable_error_logger:  # If True
        sys.stderr = Logger()  # Start the Logger() class to write to console and file


threading.Thread(target=start_logger).start()

# variables to be used within the program
source_file_path = StringVar()
source_loaded = StringVar()
source_file_information = {}
encode_file_path = StringVar()
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


# function to clear all variables
def clear_all_variables():
    source_file_path.set('')
    source_loaded.set('')
    source_file_information.clear()
    encode_file_path.set('')
    encode_file_resolution.set('')
    encode_media_info.set('')
    encode_file_audio.set('')
    encode_hdr_string.set('')
    torrent_file_path.set('')
    nfo_info_var.set('')
    automatic_workflow_boolean.set(0)
    live_boolean.set(0)
    anonymous_boolean.set(0)
    movie_search_var.set('')
    movie_search_active.set(0)
    tmdb_id_var.set('')
    imdb_id_var.set('')
    release_date_var.set('')
    rating_var.set('')


# function to open imdb links with and without the id
def open_imdb_link():
    if imdb_id_var.get() != '':
        webbrowser.open(f'https://imdb.com/title/{imdb_id_var.get()}')
    else:
        webbrowser.open('https://www.imdb.com/')


# function to open tmdb links with and without the id
def open_tmdb_link():
    if tmdb_id_var.get() != '':
        webbrowser.open(f'https://www.themoviedb.org/movie/{tmdb_id_var.get()}')
    else:
        webbrowser.open('https://www.themoviedb.org/movie')


def source_input_function(*args):
    delete_encode_entry()  # clear encode entry
    source_file_information.clear()  # clear dictionary
    audio_pop_up_var = StringVar()  # audio pop up var

    media_info = MediaInfo.parse(pathlib.Path(*args))
    video_track = media_info.video_tracks[0]
    calculate_average_video_bitrate = round((float(video_track.stream_size) / 1000) /
                                            ((float(video_track.duration) / 60000) * 0.0075) / 1000)
    update_source_label = f"Avg BR:  {str(calculate_average_video_bitrate)} kbps  |  " \
                          f"Res:  {str(video_track.width)}x{str(video_track.height)}  |  " \
                          f"FPS:  {str(video_track.frame_rate)}  |  " \
                          f"Size:  {str(video_track.other_stream_size[3])}"
    hdr_string = ''
    if video_track.other_hdr_format:
        hdr_string = f"HDR format:  {str(video_track.hdr_format)} / {str(video_track.hdr_format_compatibility)}"
    elif not video_track.other_hdr_format:
        hdr_string = ''

    # if source has 0 audio streams (this should never happen)
    if not media_info.general_tracks[0].count_of_audio_streams:
        messagebox.showerror(parent=root, title='Error', message='Source has no audio track')
        return

    # if source file only has 2 or more tracks
    if int(media_info.general_tracks[0].count_of_audio_streams) >= 2:
        audio_track_win = Toplevel()  # Toplevel window
        audio_track_win.configure(background='#363636')  # Set color of audio_track_win background
        audio_track_win.title('Audio Track Selection')
        # Open on top left of root window
        audio_track_win.geometry(f'{480}x{160}+{str(int(root.geometry().split("+")[1]) + 108)}+'
                                 f'{str(int(root.geometry().split("+")[2]) + 80)}')
        audio_track_win.resizable(0, 0)  # makes window not resizable
        audio_track_win.grab_set()  # forces audio_track_win to stay on top of root
        audio_track_win.wm_overrideredirect(True)
        root.wm_attributes('-alpha', 0.90)  # set main gui to be slightly transparent
        audio_track_win.grid_rowconfigure(0, weight=1)
        audio_track_win.grid_columnconfigure(0, weight=1)

        track_frame = Frame(audio_track_win, highlightbackground="white", highlightthickness=2, bg="#363636",
                            highlightcolor='white')
        track_frame.grid(column=0, row=0, columnspan=3, sticky=N + S + E + W)
        for e_n_f in range(3):
            track_frame.grid_columnconfigure(e_n_f, weight=1)
            track_frame.grid_rowconfigure(e_n_f, weight=1)

        # create label
        track_selection_label = Label(track_frame, text='Select audio source that down-mix was encoded from:',
                                      background='#363636', fg="#3498db", font=(set_font, set_font_size, "bold"))
        track_selection_label.grid(row=0, column=0, columnspan=3, sticky=W + N, padx=5, pady=(2, 0))

        # create drop down menu set
        audio_stream_track_counter = {}
        for i in range(int(media_info.general_tracks[0].count_of_audio_streams)):
            audio_stream_track_counter[f'Track #{i + 1}  |  {stream_menu(*args)[i]}'] = i

        audio_pop_up_var.set(next(iter(audio_stream_track_counter)))  # set the default option
        audio_pop_up_menu = OptionMenu(track_frame, audio_pop_up_var, *audio_stream_track_counter.keys())
        audio_pop_up_menu.config(background="#23272A", foreground="white", highlightthickness=1,
                                 width=48, anchor='w', activebackground="#23272A", activeforeground="#3498db")
        audio_pop_up_menu.grid(row=1, column=0, columnspan=3, padx=10, pady=6, sticky=N + W + E)
        audio_pop_up_menu["menu"].configure(background="#23272A", foreground="white", activebackground="#23272A",
                                            activeforeground="#3498db")

        # create 'OK' button
        def audio_ok_button_function():
            audio_pop_up_var.set(audio_stream_track_counter[audio_pop_up_var.get()])
            root.wm_attributes('-alpha', 1.0)  # restore transparency
            audio_track_win.destroy()

        audio_track_okay_btn = HoverButton(track_frame, text="OK", command=audio_ok_button_function, foreground="white",
                                           background="#23272A", borderwidth="3", width=8, activeforeground="#3498db",
                                           activebackground="#23272A")
        audio_track_okay_btn.grid(row=2, column=2, columnspan=1, padx=7, pady=5, sticky=S + E)
        audio_track_win.wait_window()

    # if source file only has 1 audio track
    elif int(media_info.general_tracks[0].count_of_audio_streams) == 1:
        audio_pop_up_var.set('0')

    # set source variables
    source_loaded.set('loaded')  # set string var to loaded

    # update dictionary
    # source input path
    source_file_information.update({"source_path": str(pathlib.Path(*args))})

    # selected source audio track info
    source_file_information.update(
        {"source_selected_audio_info": media_info.audio_tracks[int(audio_pop_up_var.get())].to_data()})

    # audio track selection
    source_file_information.update({"audio_track": audio_pop_up_var.get()})

    # resolution
    source_file_information.update({"resolution": f"{str(video_track.width)}x{str(video_track.height)}"})

    source_label.config(text=update_source_label)
    source_hdr_label.config(text=hdr_string)
    source_file_path.set(str(pathlib.Path(*args)))

    source_entry_box.config(state=NORMAL)
    source_entry_box.delete(0, END)
    source_entry_box.insert(END, pathlib.Path(*args).name)
    source_entry_box.config(state=DISABLED)


def encode_input_function(*args):
    if source_loaded.get() == '':
        messagebox.showinfo(parent=root, title='Info', message='You must open a source file first')
        return

    # code to check input extension
    if pathlib.Path(*args).suffix != '.mp4':
        messagebox.showerror(parent=root, title='Incorrect container',
                             message=f'Incorrect container/extension "{pathlib.Path(*args).suffix}":\n\n'
                                     f'BHDStudio encodes are muxed into MP4 containers and should have a '
                                     f'".mp4" extension')
        delete_encode_entry()
        return

    # if file has the correct extension type parse it
    media_info = MediaInfo.parse(pathlib.Path(*args))

    # function to generate generic errors
    def encode_input_error_box(media_info_count, track_type, error_string):
        error_message = f'"{pathlib.Path(*args).stem}":\n\nHas {media_info_count} {track_type} track' \
                        f'(s)\n\n{error_string}'
        messagebox.showerror(parent=root, title='Incorrect Format', message=error_message)
        delete_encode_entry()

    # video checks ----------------------------------------------------------------------------------------------------
    # if encode is missing the video track
    if not media_info.general_tracks[0].count_of_video_streams:
        encode_input_error_box('0', 'video', 'BHDStudio encodes should have 1 video track')
        return

    # if encode has more than 1 video track
    if int(media_info.general_tracks[0].count_of_video_streams) > 1:
        encode_input_error_box(media_info.general_tracks[0].count_of_video_streams, 'video',
                               'BHDStudio encodes should only have 1 video track')
        return

    # select video track for parsing
    video_track = media_info.video_tracks[0]

    # calculate average video bit rate for encode
    calculate_average_video_bit_rate = round((float(video_track.stream_size) / 1000) /
                                             ((float(video_track.duration) / 60000) * 0.0075) / 1000)

    # check for un-even crops
    width_value = int(str(source_file_information.get('resolution')).split('x')[0]) - int(video_track.width)
    height_value = int(str(source_file_information.get('resolution')).split('x')[1]) - int(video_track.height)
    if (int(width_value) % 2) != 0 or (int(height_value) % 2) != 0:
        messagebox.showerror(parent=root, title='Crop Error',
                             message=f'Resolution: "{str(video_track.width)}x{str(video_track.height)}"\n\n'
                                     f'BHDStudio encodes should only be cropped in even numbers')
        delete_encode_entry()
        return

    # error function for resolution check and miss match bit rates
    def resolution_bit_rate_miss_match_error(res_error_string):
        messagebox.showerror(parent=root, title='Resolution/Bit rate Miss Match', message=res_error_string)
        delete_encode_entry()

    # detect resolution and check miss match bit rates
    if video_track.width <= 1280 and video_track.height <= 720:  # 720p
        encoded_source_resolution = '720p'
        if calculate_average_video_bit_rate <= 3000 or calculate_average_video_bit_rate >= 5000:
            resolution_bit_rate_miss_match_error(f'Input bit rate: {str(calculate_average_video_bit_rate)} kbps\n\n'
                                                 f'Bit rate for 720p encodes should be @ 4000 kbps')
            return
    elif video_track.width <= 1920 and video_track.height <= 1080:  # 1080p
        encoded_source_resolution = '1080p'
        if calculate_average_video_bit_rate <= 7000 or calculate_average_video_bit_rate >= 9000:
            resolution_bit_rate_miss_match_error(f'Input bit rate: {str(calculate_average_video_bit_rate)} kbps\n\n'
                                                 f'Bit rate for 1080p encodes should be @ 8000 kbps')
            return
    elif video_track.width <= 3840 and video_track.height <= 2160:  # 2160p
        encoded_source_resolution = '2160p'
        if calculate_average_video_bit_rate <= 15000 or calculate_average_video_bit_rate >= 17000:
            resolution_bit_rate_miss_match_error(f'Input bit rate: {str(calculate_average_video_bit_rate)} kbps\n\n'
                                                 f'Bit rate for 2160p encodes should be @ 16000 kbps')
            return
    # set encode file resolution stringvar
    encode_file_resolution.set(encoded_source_resolution)

    # check for source resolution vs encode resolution (do not allow 2160p encode on a 1080p source)
    source_width = str(source_file_information['resolution']).split('x')[0]
    source_height = str(source_file_information['resolution']).split('x')[1]
    if int(source_width) <= 1920 and int(source_height) <= 1080:  # 1080p
        source_resolution = '1080p'
        allowed_encode_resolutions = ['720p', '1080p']
    elif int(source_width) <= 3840 and int(source_height) <= 2160:  # 2160p
        source_resolution = '2160p'
        allowed_encode_resolutions = ['2160p']
    if encoded_source_resolution not in allowed_encode_resolutions:
        messagebox.showerror(parent=root, title='Error',
                             message=f'Source resolution {source_resolution}:\n'
                                     f'Encode resolution {encoded_source_resolution}\n\n'
                                     f'Allowed encode resolutions based on source:\n'
                                     f'"{", ".join(allowed_encode_resolutions)}"')
        return

    # audio checks ----------------------------------------------------------------------------------------------------
    # if encode is missing the audio track
    if not media_info.general_tracks[0].count_of_audio_streams:
        encode_input_error_box('0', 'audio', 'BHDStudio encodes should have 1 audio track')
        return

    # if encode has more than 1 audio track
    if int(media_info.general_tracks[0].count_of_audio_streams) > 1:
        encode_input_error_box(media_info.general_tracks[0].count_of_audio_streams, 'audio',
                               'BHDStudio encodes should only have 1 audio track')
        return

    # select audio track #1
    audio_track = media_info.audio_tracks[0]

    # check audio track format
    if str(audio_track.format) != 'AC-3':
        messagebox.showerror(parent=root, title='Error',
                             message=f'Audio format "{str(audio_track.format)}" '
                                     f'is not correct.\n\nBHDStudio encodes should be in "Dolby Digital (AC-3)" only')
        return

    # check if audio channels was properly encoded from source
    source_audio_channels = int(source_file_information["source_selected_audio_info"]["channel_s"])
    # 720p check, define accepted bhd audio channels
    if encoded_source_resolution == '720p':
        if source_audio_channels == 1:
            bhd_accepted_audio_channels = 1
        elif source_audio_channels >= 2:
            bhd_accepted_audio_channels = 2

    # 1080p/2160p check, define accepted bhd audio channels
    elif encoded_source_resolution == '1080p' or encoded_source_resolution == '2160p':
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
            source_audio_string = '1.0'
        elif source_audio_channels == 2:
            source_audio_string = '2.0'
        elif source_audio_channels == 3:
            source_audio_string = '2.1'
        elif source_audio_channels == 6:
            source_audio_string = '5.1'
        elif source_audio_channels == 7:
            source_audio_string = '6.1'
        elif source_audio_channels == 8:
            source_audio_string = '7.1'
        else:
            source_audio_string = str(source_audio_channels)

        # generate cleaner audio strings for encode
        if bhd_accepted_audio_channels == 1:
            encode_audio_string = '1.0'
        elif bhd_accepted_audio_channels == 2:
            encode_audio_string = '2.0 (dplII)'
        elif bhd_accepted_audio_channels == 6:
            encode_audio_string = '5.1'
        messagebox.showerror(parent=root, title='Error',
                             message=f'Source audio is {source_audio_string}\n\n'
                                     f'{encoded_source_resolution} BHDStudio audio should be Dolby Digital '
                                     f'{encode_audio_string}')
        return

    # update audio channel string var for use with the uploader
    if bhd_accepted_audio_channels == 1:
        encode_file_audio.set('DD1.0')
    elif bhd_accepted_audio_channels == 2:
        encode_file_audio.set('DD2.0')
    elif bhd_accepted_audio_channels == 6:
        encode_file_audio.set('DD5.1')

    # audio channel string conversion and error check
    if audio_track.channel_s == 1:
        audio_channels_string = '1.0'
    elif audio_track.channel_s == 2:
        audio_channels_string = '2.0'
    elif audio_track.channel_s == 6:
        audio_channels_string = '5.1'
    else:
        messagebox.showerror(parent=root, title='Incorrect Format',
                             message=f'Incorrect audio channel format {str(audio_track.channel_s)}:\n\nBHDStudio '
                                     f'encodes audio channels should be 1.0, 2.0 (dplII), or 5.1')
        delete_encode_entry()
        return

    calculate_average_video_bitrate = round((float(video_track.stream_size) / 1000) /
                                            ((float(video_track.duration) / 60000) * 0.0075) / 1000)

    update_source_label = f"Avg BR:  {str(calculate_average_video_bitrate)} kbps  |  " \
                          f"Res:  {str(video_track.width)}x{str(video_track.height)}  |  " \
                          f"FPS:  {str(video_track.frame_rate)}  |  " \
                          f"Audio:  {str(audio_track.format)} / {audio_channels_string} / " \
                          f"{str(audio_track.other_bit_rate[0]).replace('kb/s', '').strip().replace(' ', '')} kbps"
    hdr_string = ''
    if video_track.other_hdr_format:
        hdr_string = f"HDR format:  {str(video_track.hdr_format)} / {str(video_track.hdr_format_compatibility)}"
        if 'hdr10' in hdr_string.lower():
            encode_hdr_string.set('HDR')
    elif not video_track.other_hdr_format:
        hdr_string = ''
        encode_hdr_string.set('')

    release_notes_scrolled.config(state=NORMAL)
    release_notes_scrolled.delete('1.0', END)
    release_notes_scrolled.insert(END, '-Optimized for PLEX, emby, Jellyfin, and other streaming platforms')
    if audio_channels_string == '1.0':
        release_notes_scrolled.insert(END, '\n-Downmixed Lossless audio track to Dolby Digital 1.0')
    elif audio_channels_string == '2.0':
        release_notes_scrolled.insert(END, '\n-Downmixed Lossless audio track to Dolby Pro Logic II 2.0')
    elif audio_channels_string == '5.1':
        release_notes_scrolled.insert(END, '\n-Downmixed Lossless audio track to Dolby Digital 5.1')
    if 'HDR10+' in str(video_track.hdr_format_compatibility):
        release_notes_scrolled.insert(END, '\n-HDR10+ compatible')
        release_notes_scrolled.insert(END, '\n-Screenshots tone mapped for comparison')
    elif 'HDR10' in str(video_track.hdr_format_compatibility):
        release_notes_scrolled.insert(END, '\n-HDR10 compatible')
        release_notes_scrolled.insert(END, '\n-Screenshots tone mapped for comparison')
    release_notes_scrolled.config(state=DISABLED)

    enable_clear_all_checkbuttons()

    # set torrent name
    torrent_file_path.set(str(pathlib.Path(*args).with_suffix('.torrent')))

    # set media info memory file
    media_info_original = MediaInfo.parse(pathlib.Path(*args), full=False, output="")  # parse identical to mediainfo
    encode_media_info.set(media_info_original)

    encode_label.config(text=update_source_label)
    encode_hdr_label.config(text=hdr_string)
    encode_file_path.set(str(pathlib.Path(*args)))
    encode_entry_box.config(state=NORMAL)
    encode_entry_box.delete(0, END)
    encode_entry_box.insert(END, pathlib.Path(*args).name)
    encode_entry_box.config(state=DISABLED)


def drop_function(event):
    file_input = [x for x in root.splitlist(event.data)][0]
    widget_source = str(event.widget.cget('text')).strip()

    if widget_source == 'Source':
        source_input_function(file_input)

    elif widget_source == 'Encode':
        encode_input_function(file_input)


# source --------------------------------------------------------------------------------------------------------------
source_frame = LabelFrame(root, text=' Source ', labelanchor="nw")
source_frame.grid(column=0, row=0, columnspan=4, padx=5, pady=(5, 3), sticky=E + W)
source_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 10, 'bold'))
source_frame.grid_rowconfigure(0, weight=1)
source_frame.grid_rowconfigure(1, weight=1)
source_frame.grid_columnconfigure(0, weight=2)
source_frame.grid_columnconfigure(1, weight=20)
source_frame.grid_columnconfigure(2, weight=1)
source_frame.grid_columnconfigure(3, weight=1)

source_frame.drop_target_register(DND_FILES)
source_frame.dnd_bind('<<Drop>>', drop_function)


def manual_source_input():
    source_file_input = filedialog.askopenfilename(parent=root, title='Select Source', initialdir='/',
                                                   filetypes=[("Media Files", "*.*")])
    if source_file_input:
        source_input_function(source_file_input)


source_button = HoverButton(source_frame, text="Open", command=manual_source_input, foreground="white",
                            background="#23272A", borderwidth="3", activeforeground="#3498db",
                            activebackground="#23272A")
source_button.grid(row=0, column=0, columnspan=1, padx=5, pady=(7, 0), sticky=N + S + E + W)

source_entry_box = Entry(source_frame, borderwidth=4, bg="#565656", fg='white', state=DISABLED,
                         disabledforeground='white', disabledbackground="#565656")
source_entry_box.grid(row=0, column=1, columnspan=2, padx=5, pady=(5, 0), sticky=E + W)

source_info_frame = LabelFrame(source_frame, text='Info:', bd=0, bg="#363636", fg="#3498db",
                               font=(set_font, set_font_size))
source_info_frame.grid(row=1, column=0, columnspan=4, padx=5, pady=0, sticky=N + S + E + W)
for s_i_f in range(4):
    source_info_frame.grid_columnconfigure(s_i_f, weight=1)
source_info_frame.grid_rowconfigure(0, weight=1)
source_info_frame.grid_rowconfigure(1, weight=1)

source_label = Label(source_info_frame, text=' ' * 100, bd=0, relief=SUNKEN, background='#363636', foreground="white")
source_label.grid(column=0, row=0, columnspan=4, pady=3, padx=3, sticky=W)
source_hdr_label = Label(source_info_frame, text=' ' * 100, bd=0, relief=SUNKEN, background='#363636',
                         foreground="white")
source_hdr_label.grid(column=0, row=1, columnspan=4, pady=3, padx=3, sticky=W)


def delete_source_entry():
    source_entry_box.config(state=NORMAL)
    source_entry_box.delete(0, END)
    source_entry_box.config(state=DISABLED)
    source_label.config(text=' ' * 100)
    source_hdr_label.config(text=' ' * 100)
    source_file_path.set('')
    source_loaded.set('')
    delete_encode_entry()


reset_source_input = HoverButton(source_frame, text="X", command=delete_source_entry, foreground="white",
                                 background="#23272A", borderwidth="3", activeforeground="#3498db",
                                 activebackground="#23272A")
reset_source_input.grid(row=0, column=3, columnspan=1, padx=5, pady=(7, 0), sticky=N + S + E + W)

# encode --------------------------------------------------------------------------------------------------------------
encode_frame = LabelFrame(root, text=' Encode ', labelanchor="nw")
encode_frame.grid(column=0, row=1, columnspan=4, padx=5, pady=(5, 3), sticky=E + W)
encode_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 10, 'bold'))
encode_frame.grid_rowconfigure(0, weight=1)
encode_frame.grid_rowconfigure(1, weight=1)
encode_frame.grid_columnconfigure(0, weight=2)
encode_frame.grid_columnconfigure(1, weight=20)
encode_frame.grid_columnconfigure(3, weight=1)

encode_frame.drop_target_register(DND_FILES)
encode_frame.dnd_bind('<<Drop>>', drop_function)


def manual_encode_input():
    encode_file_input = filedialog.askopenfilename(parent=root, title='Select Encode', initialdir='/',
                                                   filetypes=[("Media Files", "*.*")])
    if encode_file_input:
        encode_input_function(encode_file_input)


encode_button = HoverButton(encode_frame, text="Open", command=manual_encode_input, foreground="white",
                            background="#23272A", borderwidth="3", activeforeground="#3498db",
                            activebackground="#23272A")
encode_button.grid(row=0, column=0, columnspan=1, padx=5, pady=5, sticky=N + S + E + W)

encode_entry_box = Entry(encode_frame, borderwidth=4, bg="#565656", fg='white', state=DISABLED,
                         disabledforeground='white', disabledbackground="#565656")
encode_entry_box.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky=E + W)

encode_info_frame = LabelFrame(encode_frame, text='Info:', bd=0, bg="#363636", fg="#3498db",
                               font=(set_font, set_font_size))
encode_info_frame.grid(row=1, column=0, columnspan=4, padx=5, pady=0, sticky=N + S + E + W)
for s_i_f in range(4):
    encode_info_frame.grid_columnconfigure(s_i_f, weight=1)
encode_info_frame.grid_rowconfigure(0, weight=1)
encode_info_frame.grid_rowconfigure(1, weight=1)

encode_label = Label(encode_info_frame, text=' ' * 100, bd=0, relief=SUNKEN, background='#363636', foreground="white")
encode_label.grid(column=0, row=0, columnspan=1, pady=3, padx=3, sticky=W)
encode_hdr_label = Label(encode_info_frame, text=' ' * 100, bd=0, relief=SUNKEN, background='#363636',
                         foreground="white")
encode_hdr_label.grid(column=0, row=1, columnspan=1, pady=3, padx=3, sticky=W)


def delete_encode_entry():
    encode_entry_box.config(state=NORMAL)
    encode_entry_box.delete(0, END)
    encode_entry_box.config(state=DISABLED)
    encode_label.config(text=' ' * 100)
    encode_hdr_label.config(text=' ' * 100)
    release_notes_scrolled.config(state=NORMAL)
    release_notes_scrolled.delete('1.0', END)
    release_notes_scrolled.config(state=DISABLED)
    disable_clear_all_checkbuttons()
    torrent_file_path.set('')
    open_torrent_window_button.config(state=DISABLED)
    generate_nfo_button.config(state=DISABLED)
    encode_file_path.set('')
    encode_file_resolution.set('')
    encode_media_info.set('')
    encode_file_audio.set('')
    encode_hdr_string.set('')


reset_encode_input = HoverButton(encode_frame, text="X", command=delete_encode_entry, foreground="white",
                                 background="#23272A", borderwidth="3", activeforeground="#3498db",
                                 activebackground="#23272A")
reset_encode_input.grid(row=0, column=3, columnspan=1, padx=5, pady=5, sticky=N + S + E + W)

# release notes -------------------------------------------------------------------------------------------------------
release_notes_frame = LabelFrame(root, text=' Release Notes ', labelanchor="nw")
release_notes_frame.grid(column=0, row=2, columnspan=4, padx=5, pady=(5, 3), sticky=E + W)
release_notes_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 10, 'bold'))

for rl_row in range(3):
    release_notes_frame.grid_rowconfigure(rl_row, weight=1)
for rl_f in range(3):
    release_notes_frame.grid_columnconfigure(rl_f, weight=1)


def update_forced_var():
    release_notes_scrolled.config(state=NORMAL)
    if forced_subtitles_burned_var.get() == 'on':
        release_notes_scrolled.insert(END, '\n-Forced English subtitles embedded for non English dialogue')
    elif forced_subtitles_burned_var.get() == 'off':
        delete_forced = release_notes_scrolled.search(
            "-Forced English subtitles embedded for non English dialogue", '1.0', END)
        if delete_forced != '':
            release_notes_scrolled.delete(str(delete_forced), str(float(delete_forced) + 1.0))
    release_notes_scrolled.config(state=DISABLED)


forced_subtitles_burned_var = StringVar()
forced_subtitles_burned = Checkbutton(release_notes_frame, text='Forced Subtitles',
                                      variable=forced_subtitles_burned_var, takefocus=False,
                                      onvalue='on', offvalue='off', command=update_forced_var,
                                      background="#363636", foreground="white", activebackground="#363636",
                                      activeforeground="white", selectcolor="#434547",
                                      font=(set_font, set_font_size + 1), state=DISABLED)
forced_subtitles_burned.grid(row=0, column=0, columnspan=1, rowspan=1, padx=5, pady=0, sticky=S + E + W + N)
forced_subtitles_burned_var.set('off')


def update_balanced_borders():
    release_notes_scrolled.config(state=NORMAL)
    if balance_borders_var.get() == 'on':
        release_notes_scrolled.insert(END, '\n-Cleaned dirty edges with BalanceBorders')
    elif balance_borders_var.get() == 'off':
        delete_balanced_borders = release_notes_scrolled.search("-Cleaned dirty edges with BalanceBorders", '1.0', END)
        if delete_balanced_borders != '':
            release_notes_scrolled.delete(str(delete_balanced_borders), str(float(delete_balanced_borders) + 1.0))
    release_notes_scrolled.config(state=DISABLED)


balance_borders_var = StringVar()
balance_borders = Checkbutton(release_notes_frame, text='Balance Borders',
                              variable=balance_borders_var, takefocus=False,
                              onvalue='on', offvalue='off', command=update_balanced_borders,
                              background="#363636", foreground="white", activebackground="#363636",
                              activeforeground="white", selectcolor="#434547",
                              font=(set_font, set_font_size + 1), state=DISABLED)
balance_borders.grid(row=0, column=1, columnspan=1, rowspan=1, padx=5, pady=0, sticky=S + E + W + N)
balance_borders_var.set('off')


def update_fill_borders():
    release_notes_scrolled.config(state=NORMAL)
    if fill_borders_var.get() == 'on':
        release_notes_scrolled.insert(END, '\n-Fill borders with FillBorders')
    elif fill_borders_var.get() == 'off':
        delete_fill_borders = release_notes_scrolled.search("-Fill borders with FillBorders", '1.0', END)
        if delete_fill_borders != '':
            release_notes_scrolled.delete(str(delete_fill_borders), str(float(delete_fill_borders) + 1.0))
    release_notes_scrolled.config(state=DISABLED)


fill_borders_var = StringVar()
fill_borders = Checkbutton(release_notes_frame, text='Fill Borders',
                           variable=fill_borders_var, takefocus=False,
                           onvalue='on', offvalue='off', command=update_fill_borders,
                           background="#363636", foreground="white", activebackground="#363636",
                           activeforeground="white", selectcolor="#434547",
                           font=(set_font, set_font_size + 1), state=DISABLED)
fill_borders.grid(row=0, column=2, columnspan=1, rowspan=1, padx=5, pady=0, sticky=S + E + W + N)
fill_borders_var.set('off')

release_notes_scrolled = scrolledtextwidget.ScrolledText(release_notes_frame, height=5, bg="#565656", bd=8, fg='white')
release_notes_scrolled.grid(row=1, column=0, columnspan=4, pady=(0, 2), padx=5, sticky=E + W)
release_notes_scrolled.config(state=DISABLED)
Hovertip(release_notes_scrolled, 'Right click to enable manual edits', hover_delay=1000)  # Hover tip tool-tip


def popup_auto_e_b_menu(e):  # Function for mouse button 3 (right click) to pop up menu
    enable_edits_menu.tk_popup(e.x_root, e.y_root)  # This gets the position of 'e'


# pop up menu to enable/disable manual edits in release notes
enable_edits_menu = Menu(release_notes_scrolled, tearoff=False, font=(set_font, set_font_size + 1),
                         background="#23272A", foreground="white", activebackground="grey")  # Right click menu
enable_edits_menu.add_command(label='Enable Manual Edits', command=lambda: release_notes_scrolled.config(state=NORMAL))
enable_edits_menu.add_command(label='Disable Manual Edits',
                              command=lambda: release_notes_scrolled.config(state=DISABLED))
release_notes_scrolled.bind('<Button-3>', popup_auto_e_b_menu)  # Uses mouse button 3 (right click) to open


def disable_clear_all_checkbuttons():
    forced_subtitles_burned.config(state=NORMAL)
    balance_borders.config(state=NORMAL)
    fill_borders.config(state=NORMAL)
    forced_subtitles_burned_var.set('off')
    balance_borders_var.set('off')
    fill_borders_var.set('off')
    forced_subtitles_burned.config(state=DISABLED)
    balance_borders.config(state=DISABLED)
    fill_borders.config(state=DISABLED)


def enable_clear_all_checkbuttons():
    forced_subtitles_burned.config(state=NORMAL)
    balance_borders.config(state=NORMAL)
    fill_borders.config(state=NORMAL)
    forced_subtitles_burned_var.set('off')
    balance_borders_var.set('off')
    fill_borders_var.set('off')


# screenshots ---------------------------------------------------------------------------------------------------------
screenshot_frame = LabelFrame(root, text=' Sreenshots ', labelanchor="nw")
screenshot_frame.grid(column=0, row=3, columnspan=4, padx=5, pady=(5, 3), sticky=E + W)
screenshot_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 10, 'bold'))
screenshot_frame.grid_rowconfigure(0, weight=1)
screenshot_frame.grid_columnconfigure(0, weight=20)
screenshot_frame.grid_columnconfigure(1, weight=20)
screenshot_frame.grid_columnconfigure(2, weight=20)
screenshot_frame.grid_columnconfigure(3, weight=1)

# screenshot textbox
screenshot_scrolledtext = scrolledtextwidget.ScrolledText(screenshot_frame, height=4, bg='#565656', fg='white', bd=8)
screenshot_scrolledtext.grid(row=0, column=0, columnspan=3, pady=(0, 6), padx=10, sticky=E + W)

# clear screenshot box
reset_screenshot_box = HoverButton(screenshot_frame, text="X", activebackground="#23272A",
                                   command=lambda: screenshot_scrolledtext.delete('1.0', END), foreground="white",
                                   background="#23272A", borderwidth="3", activeforeground="#3498db", width=4)
reset_screenshot_box.grid(row=0, column=3, columnspan=1, padx=5, pady=5, sticky=N + E + W)


def popup_auto_e_b_menu(e):  # Function for mouse button 3 (right click) to pop up menu
    screen_shot_right_click_menu.tk_popup(e.x_root, e.y_root)  # This gets the position of 'e'


# pop up menu to enable/disable manual edits in release notes
screen_shot_right_click_menu = Menu(release_notes_scrolled, tearoff=False, font=(set_font, set_font_size + 1),
                                    background="#23272A", foreground="white",
                                    activebackground="grey")  # Right click menu


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


screen_shot_right_click_menu.add_command(label='Cut', command=text_cut)


# right click menu copy
def text_copy():
    if screenshot_scrolledtext.selection_get():
        # Grab selected text from text box
        selected_text_copy = screenshot_scrolledtext.selection_get()
        # Clear the clipboard then append
        screenshot_scrolledtext.clipboard_clear()
        screenshot_scrolledtext.clipboard_append(selected_text_copy)


screen_shot_right_click_menu.add_command(label='Copy', command=text_copy)


# right click menu paste
def text_paste():
    screenshot_scrolledtext.delete("1.0", END)
    screenshot_scrolledtext.insert(END, screenshot_scrolledtext.clipboard_get())


screen_shot_right_click_menu.add_command(label='Paste', command=text_paste)


# right click menu clear
def text_delete():
    screenshot_scrolledtext.delete("1.0", END)


screen_shot_right_click_menu.add_command(label='Clear', command=text_delete)

screenshot_scrolledtext.bind('<Button-3>', popup_auto_e_b_menu)  # Uses mouse button 3 (right click) to open


# check/return screenshots
def parse_screen_shots():
    # if screenshot textbox is not empty
    if screenshot_scrolledtext.compare("end-1c", "!=", "1.0"):
        new_screenshots = screenshot_scrolledtext.get(1.0, END).split('[/url]')
        fresh_list = [str(i).strip() for i in new_screenshots]
        if '' in fresh_list:
            fresh_list.remove('')

        if int(len(fresh_list)) % 2 == 0:
            sorted_screenshots = ''
            iterate_list = iter(fresh_list)
            for x in iterate_list:
                sorted_screenshots += x + '[/url]'
                sorted_screenshots += "  "
                sorted_screenshots += str(next(iterate_list)) + '[/url]'
                sorted_screenshots += "\n"
                sorted_screenshots += "\n"
            return sorted_screenshots
        else:
            return False


# manual workflow frame
manual_workflow = LabelFrame(root, text=' Manual Workflow ', labelanchor="nw")
manual_workflow.grid(column=0, row=4, columnspan=3, padx=5, pady=(5, 3), sticky=W)
manual_workflow.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 10, 'bold'))
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
        messagebox.showerror(parent=root, title='Error!', message='Source file is missing!')
        return
    if not pathlib.Path(encode_file_path.get()).is_file():
        messagebox.showerror(parent=root, title='Error!', message='Encode file is missing!')
        return
    parse_screenshots = parse_screen_shots()
    if not parse_screenshots:
        messagebox.showerror(parent=root, title='Error!', message='Missing or incorrectly formatted screenshots\n\n'
                                                                  'Screen shots need to be in multiples of 2')
        return

    # nfo formatter
    def run_nfo_formatter():
        nfo_b64 = """
        W2NvbG9yPSNmNWM3MGFdUkVMRUFTRSBJTkZPWy9jb2xvcl0NCg0KU291cmNlICAgICAgICAgICAg
        ICAgICAgOiB7Ymx1cmF5X3NvdXJjZX0gKFRoYW5rcyEpDQpDaGFwdGVycyAgICAgICAgICAgICAg
        ICA6IHtjaGFwdGVyX3R5cGV9DQpGaWxlIFNpemUgICAgICAgICAgICAgICA6IHtlbmNvZGVfZmls
        ZV9zaXplfQ0KRHVyYXRpb24gICAgICAgICAgICAgICAgOiB7ZW5jb2RlX2ZpbGVfZHVyYXRpb259
        DQpWaWRlbyAgICAgICAgICAgICAgICAgICA6IHtjb250YWluZXJfZm9ybWF0fSB7dl9jb2RlY30g
        VmlkZW8gLyB7dl9iaXRyYXRlfSBrYnBzIC8ge3ZfZnBzfSAvIHt2X2Zvcm1hdF9wcm9maWxlfQ0K
        UmVzb2x1dGlvbiAgICAgICAgICAgICAgOiB7dl93aWR0aH0geCB7dl9oZWlnaHR9ICh7dl9hc3Bl
        Y3RfcmF0aW99KQ0KQXVkaW8gICAgICAgICAgICAgICAgICAgOiB7YV9sbmd9IC8ge2FfY29tbWVy
        Y2lhbH0gQXVkaW8gLyB7YV9jaG5sX3N9IC8ge2FfZnJlcX0gLyB7YV9iaXRyYXRlfSBrYnBzIHtv
        cHRpb25hbF9zdWJfc3RyaW5nfQ0KRW5jb2RlciAgICAgICAgICAgICAgICAgOiBbY29sb3I9I2Y1
        YzcwYV17ZW5jb2RlZF9ieX1bL2NvbG9yXQ0KDQpbY29sb3I9I2Y1YzcwYV1SRUxFQVNFIE5PVEVT
        Wy9jb2xvcl0NCg0Ke25mb19yZWxlYXNlX25vdGVzfQ0KDQpbY29sb3I9I2Y1YzcwYV1TQ1JFRU5T
        SE9UU1svY29sb3JdDQpbY2VudGVyXQ0KW2NvbG9yPSNmNWM3MGFdU09VUkNFWy9jb2xvcl08PDw8
        PDw8PDw8PDw8PDw8PC0tLS0tLS0tLS0tLS0tLS0tLS1bY29sb3I9I2Y1YzcwYV1WU1svY29sb3Jd
        LS0tLS0tLS0tLS0tLS0tLS0tLT4+Pj4+Pj4+Pj4+Pj4+Pj4+W2NvbG9yPSNmNWM3MGFdRU5DT0RF
        Wy9jb2xvcl0NCntuZm9fc2NyZWVuX3Nob3RzfQ0KWy9jZW50ZXJdDQpbY29sb3I9I2Y1YzcwYV1H
        UkVFVFpbL2NvbG9yXQ0KDQpBbGwgdGhvc2Ugd2hvIHN1cHBvcnQgb3VyIGdyb3VwLCBvdXIgZW5j
        b2RlcnMsIGFuZCBvdXIgY29tbXVuaXR5LiANCg0KW2NvbG9yPSNmNWM3MGFdR1JPVVAgTk9URVNb
        L2NvbG9yXQ0KDQpFbmpveSENCg0KV2UgYXJlIGN1cnJlbnRseSBsb29raW5nIGZvciBub3RoaW5n
        IGluIHBhcnRpY3VsYXIuIElmIHlvdSBmZWVsIHlvdSBoYXZlIHNvbWV0aGluZyB0byBvZmZlciwg
        Y29udGFjdCB1cyENCg0KW2NlbnRlcl1baW1nXWh0dHBzOi8vYmV5b25kaGQuY28vaW1hZ2VzLzIw
        MjEvMDMvMzAvNjJiY2E4ZDU4N2I3MTczMTIxMDA4ODg3ZWJlMDVhNDIucG5nWy9pbWddWy9jZW50
        ZXJdDQoNCg==
        """

        decoded_nfo = base64.b64decode(nfo_b64).decode("ascii")

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
            chapters_start_numbered = re.search(r"chapter\s*(\d+)", str(list(encode_chapter.values())),
                                                re.IGNORECASE).group(1)
            chapters_end_numbered = re.search(r"chapter\s*(\d+)", str(list(reversed(encode_chapter.values()))),
                                              re.IGNORECASE).group(1)
            chapter_type = f'Numbered ({chapters_start_numbered.lstrip("0")}-{chapters_end_numbered.lstrip("0")})'
        except AttributeError:
            chapter_type = 'Named'

        # file size
        encode_file_size = encode_general_track.other_file_size[0]

        # duration
        encode_file_duration = encode_video_track.other_duration[0]

        # video container format
        container_format = encode_general_track.commercial_name

        # video codec
        v_codec = encode_video_track.commercial_name

        # video bitrate
        v_bitrate = round((float(encode_video_track.stream_size) / 1000) /
                          ((float(encode_video_track.duration) / 60000) * 0.0075) / 1000)

        # video fps
        v_fps = f'{encode_video_track.frame_rate} fps'

        # video format profile
        v_format_profile = ''
        if encode_video_track.format_profile == 'High@L4.1':
            v_format_profile = 'High Profile 4.1'
        elif encode_video_track.format_profile == 'Main 10@L5.1@Main':
            hdr_type = str(encode_video_track.hdr_format_compatibility)
            if 'HDR10+' in hdr_type:
                hdr_string = ' / HDR10+'
            elif 'HDR10' in hdr_type:
                hdr_string = ' / HDR10'
            else:
                hdr_string = ''
            v_format_profile = f'Main 10 @ Level 5.1 @ Main / 4:2:0{hdr_string}'

        # video width
        v_width = encode_video_track.width

        # video height
        v_height = encode_video_track.height

        # video aspect ratio
        v_aspect_ratio = encode_video_track.other_display_aspect_ratio[0]

        # audio language
        a_lng = ''
        check_audio_language = encode_audio_track.other_language
        if check_audio_language:
            a_lng = encode_audio_track.other_language[0]
        if not check_audio_language:
            a_lng = 'English'

        # audio commercial name
        a_commercial = encode_audio_track.commercial_name

        # audio channels
        if encode_audio_track.channel_s == 1:
            a_chnl_s = '1.0'
        elif encode_audio_track.channel_s == 2:
            a_chnl_s = '2.0'
        elif encode_audio_track.channel_s == 6:
            a_chnl_s = '5.1'
        else:
            a_chnl_s = encode_audio_track.channel_s

        # audio frequency
        a_freq = encode_audio_track.other_sampling_rate[0]

        # audio bitrate
        a_bitrate = str(encode_audio_track.other_bit_rate[0]).replace('kb/s', '').strip()

        # optional sub string
        if forced_subtitles_burned_var.get() == 'on':
            optional_sub_string = '\nSubtitles               : English (Forced)'
        elif forced_subtitles_burned_var.get() == 'off':
            optional_sub_string = ''

        # encoder name
        encoded_by = ''
        encoder_sig = nfo_pad_parser['encoder_name']['name'].strip()
        if encoder_sig == '':
            encoded_by = 'Anonymous'
        elif encoder_sig != '':
            encoded_by = nfo_pad_parser['encoder_name']['name'].strip()

        # release notes
        nfo_release_notes = release_notes_scrolled.get("1.0", END).strip()

        # screen shots
        nfo_screen_shots = parse_screenshots

        formatted_nfo = decoded_nfo.format(bluray_source=bluray_source, chapter_type=chapter_type,
                                           encode_file_size=encode_file_size, encode_file_duration=encode_file_duration,
                                           container_format=container_format, v_codec=v_codec, v_bitrate=v_bitrate,
                                           v_fps=v_fps, v_format_profile=v_format_profile, v_width=v_width,
                                           v_height=v_height, v_aspect_ratio=v_aspect_ratio, a_lng=a_lng,
                                           a_commercial=a_commercial, a_chnl_s=a_chnl_s, a_freq=a_freq,
                                           a_bitrate=a_bitrate, optional_sub_string=optional_sub_string,
                                           encoded_by=encoded_by, nfo_release_notes=nfo_release_notes,
                                           nfo_screen_shots=nfo_screen_shots)
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
        if nfo_pad.wm_state() == 'normal':
            if nfo_pad_exit_parser['save_window_locations']['nfo_pad'] != nfo_pad.geometry():
                if int(nfo_pad.geometry().split('x')[0]) >= nfo_pad_window_width or \
                        int(nfo_pad.geometry().split('x')[1].split('+')[0]) >= nfo_pad_window_height:
                    nfo_pad_exit_parser.set('save_window_locations', 'nfo_pad', nfo_pad.geometry())
                    with open(config_file, 'w') as nfo_configfile:
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
    nfo_pad.title('BHDStudioUploadTool - NFO Pad')
    nfo_pad_window_height = 600
    nfo_pad_window_width = 1000
    nfo_pad.config(bg="#363636")
    if nfo_pad_parser['save_window_locations']['nfo_pad'] == '':
        nfo_screen_width = nfo_pad.winfo_screenwidth()
        nfo_screen_height = nfo_pad.winfo_screenheight()
        nfo_x_coordinate = int((nfo_screen_width / 2) - (nfo_pad_window_width / 2))
        nfo_y_coordinate = int((nfo_screen_height / 2) - (nfo_pad_window_height / 2))
        nfo_pad.geometry(f"{nfo_pad_window_width}x{nfo_pad_window_height}+{nfo_x_coordinate}+{nfo_y_coordinate}")
    elif nfo_pad_parser['save_window_locations']['nfo_pad'] != '':
        nfo_pad.geometry(nfo_pad_parser['save_window_locations']['nfo_pad'])
    nfo_pad.protocol('WM_DELETE_WINDOW', lambda: [automatic_workflow_boolean.set(False), nfo_pad_exit_function()])

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
        nfo_pad.title('New File - TextPad!')
        status_bar.config(text="New File")

        global open_status_name
        open_status_name = False

    # Open Files
    def open_file():
        # Delete previous text
        nfo_pad_text_box.delete("1.0", END)

        # Grab Filename
        text_file = filedialog.askopenfilename(parent=nfo_pad, initialdir="/", title="Open File",
                                               filetypes=[("Text Files, NFO Files", ".txt .nfo")])

        # Check to see if there is a file name
        if text_file:
            # Make filename global so we can access it later
            global open_status_name
            open_status_name = text_file

        # Update Status bars
        name = text_file
        status_bar.config(text=f'{name}')
        nfo_pad.title(f'{name} - NFO Pad!')

        # Open the file
        text_file = open(text_file, 'r')
        stuff = text_file.read()
        # Add file to textbox
        nfo_pad_text_box.insert(END, stuff)
        # Close the opened file
        text_file.close()

    # Save As File
    def nfo_pad_save():
        text_file = filedialog.asksaveasfilename(parent=nfo_pad, defaultextension=".nfo", initialdir="/",
                                                 title="Save File", filetypes=[("NFO File", "*.nfo")])
        if text_file:
            # update status bars
            name = text_file
            status_bar.config(text=f'Saved: {name}')
            nfo_pad.title(f'{name} - NFO Pad')

            # save the file
            text_file = open(text_file, 'w')
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

    # Change bg color
    def bg_color():
        my_color = colorchooser.askcolor(parent=nfo_pad)[1]
        if my_color:
            nfo_pad_text_box.config(bg=my_color)

    # Change ALL Text Color
    def all_text_color():
        my_color = colorchooser.askcolor(parent=nfo_pad)[1]
        if my_color:
            nfo_pad_text_box.config(fg=my_color)

    # Select all Text
    def select_all(e):
        # Add sel tag to select all text
        nfo_pad_text_box.tag_add('sel', '1.0', 'end')

    # Clear All Text
    def clear_all():
        nfo_pad_text_box.delete(1.0, END)

    # Create Main Frame
    nfo_frame = Frame(nfo_pad)
    nfo_frame.grid(column=0, columnspan=2, row=0, pady=(5, 0), padx=5, sticky=N + S + E + W)
    nfo_frame.grid_columnconfigure(0, weight=1)
    nfo_frame.grid_rowconfigure(0, weight=1)

    # scroll bars
    right_scrollbar = Scrollbar(nfo_frame, orient=VERTICAL)  # Scrollbars
    bottom_scrollbar = Scrollbar(nfo_frame, orient=HORIZONTAL)

    # Create Text Box
    nfo_pad_text_box = Text(nfo_frame, undo=True, yscrollcommand=right_scrollbar.set, wrap="none",
                            xscrollcommand=bottom_scrollbar.set, background='#c0c0c0',
                            font=(set_fixed_font, set_font_size + 1))
    nfo_pad_text_box.grid(column=0, row=0, sticky=N + S + E + W)

    # add scrollbars to the textbox
    right_scrollbar.config(command=nfo_pad_text_box.yview)
    right_scrollbar.grid(row=0, column=1, sticky=N + W + S)
    bottom_scrollbar.config(command=nfo_pad_text_box.xview)
    bottom_scrollbar.grid(row=1, column=0, sticky=W + E + N)

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
    nfo_menu.add_command(label="Exit", command=lambda: [automatic_workflow_boolean.set(False), nfo_pad_exit_function()])

    # Add Edit Menu
    edit_menu = Menu(nfo_main_menu, tearoff=False)
    nfo_main_menu.add_cascade(label="Edit", menu=edit_menu)
    edit_menu.add_command(label="Cut", command=lambda: cut_text(False), accelerator="(Ctrl+x)")
    edit_menu.add_command(label="Copy", command=lambda: copy_text(False), accelerator="(Ctrl+c)")
    edit_menu.add_command(label="Paste             ", command=lambda: paste_text(False), accelerator="(Ctrl+v)")
    edit_menu.add_separator()
    edit_menu.add_command(label="Undo", command=nfo_pad_text_box.edit_undo, accelerator="(Ctrl+z)")
    edit_menu.add_command(label="Redo", command=nfo_pad_text_box.edit_redo, accelerator="(Ctrl+y)")
    edit_menu.add_separator()
    edit_menu.add_command(label="Select All", command=lambda: select_all(True), accelerator="(Ctrl+a)")
    edit_menu.add_command(label="Clear", command=clear_all)

    # Add Color Menu
    color_menu = Menu(nfo_main_menu, tearoff=False)
    nfo_main_menu.add_cascade(label="Colors", menu=color_menu)
    color_menu.add_command(label="Text Color", command=all_text_color)
    color_menu.add_command(label="Background", command=bg_color)

    # Add Status Bar To Bottom Of App
    status_bar = Label(nfo_pad, text='Ready', anchor=E, bg="#565656", fg="white", relief=SUNKEN)
    status_bar.grid(column=0, columnspan=2, row=2, pady=1, padx=1, sticky=E + W)

    # Edit Bindings
    nfo_pad.bind('<Control-Key-x>', cut_text)
    nfo_pad.bind('<Control-Key-c>', copy_text)
    nfo_pad.bind('<Control-Key-v>', paste_text)
    # Select Binding
    nfo_pad.bind('<Control-A>', select_all)
    nfo_pad.bind('<Control-a>', select_all)

    nfo = run_nfo_formatter()

    nfo_pad_text_box.delete("1.0", END)
    nfo_pad_text_box.insert(END, nfo)

    # if program is in automatic workflow mode
    if automatic_workflow_boolean.get():
        workflow_frame = Frame(nfo_pad, bg="#363636")
        workflow_frame.grid(row=1, column=0, columnspan=2, padx=0, pady=0, sticky=N + S + E + W)
        workflow_frame.grid_columnconfigure(0, weight=1)
        workflow_frame.grid_columnconfigure(1, weight=1)
        workflow_frame.grid_rowconfigure(0, weight=1)

        continue_button = HoverButton(workflow_frame, text="Continue", activebackground="#23272A",
                                      command=lambda: [automatic_workflow_boolean.set(True), nfo_pad_exit_function()],
                                      foreground="white", background="#23272A", borderwidth="3",
                                      activeforeground="#3498db", width=10)
        continue_button.grid(row=0, column=1, columnspan=1, padx=7, pady=(3, 0), sticky=N + S + E)

        cancel_workflow_button = HoverButton(workflow_frame, text="Cancel", width=10, foreground="white",
                                             command=lambda: [automatic_workflow_boolean.set(False),
                                                              nfo_pad_exit_function()], activebackground="#23272A",
                                             borderwidth="3", activeforeground="#3498db", background="#23272A")
        cancel_workflow_button.grid(row=0, column=0, columnspan=1, padx=7, pady=(3, 0), sticky=N + S + W)
        status_bar.config(text="(Saving is optional)   Cancel / Closing NFO Pad will stop the automatic workflow  |  "
                               "Click continue to proceed...")
        nfo_pad.wait_window()


generate_nfo_button = HoverButton(manual_workflow, text="Generate NFO", command=open_nfo_viewer, foreground="white",
                                  background="#23272A", borderwidth="3", activeforeground="#3498db",
                                  activebackground="#23272A", width=12)
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
        if '/announce' in torrent_tracker_url_entry_box.get().strip():
            torrent_parser.set('torrent_settings', 'tracker_url', torrent_tracker_url_entry_box.get().strip())
            with open(config_file, 'w') as torrent_configfile:
                torrent_parser.write(torrent_configfile)

        # save torrent window position/geometry
        if torrent_window.wm_state() == 'normal':
            if torrent_parser['save_window_locations']['torrent_window'] != torrent_window.geometry():
                if int(torrent_window.geometry().split('x')[0]) >= tor_window_width or \
                        int(torrent_window.geometry().split('x')[1].split('+')[0]) >= tor_window_height:
                    torrent_parser.set('save_window_locations', 'torrent_window', torrent_window.geometry())
                    with open(config_file, 'w') as torrent_configfile:
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
    torrent_window.configure(background="#363636")  # Set color of torrent_window background
    torrent_window.title('BHDStudio Torrent Creator')
    tor_window_height = 330  # win height
    tor_window_width = 520  # win width
    if torrent_config['save_window_locations']['torrent_window'] == '':
        # open near the center of root
        torrent_window.geometry(f'{tor_window_width}x{tor_window_height}+'
                                f'{str(int(root.geometry().split("+")[1]) + 100)}+'
                                f'{str(int(root.geometry().split("+")[2]) + 210)}')
    elif torrent_config['save_window_locations']['torrent_window'] != '':
        torrent_window.geometry(torrent_config['save_window_locations']['torrent_window'])
    torrent_window.protocol('WM_DELETE_WINDOW', lambda: [automatic_workflow_boolean.set(False),
                                                         torrent_window_exit_function()])

    # row and column configure
    for t_w in range(10):
        torrent_window.grid_columnconfigure(t_w, weight=1)
    for t_w in range(10):
        torrent_window.grid_rowconfigure(t_w, weight=1)

    # torrent path frame
    torrent_path_frame = LabelFrame(torrent_window, text=' Path ', labelanchor="nw")
    torrent_path_frame.grid(column=0, row=0, columnspan=10, padx=5, pady=(0, 3), sticky=E + W + N + S)
    torrent_path_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 10, 'bold'))
    torrent_path_frame.grid_rowconfigure(0, weight=1)
    torrent_path_frame.grid_rowconfigure(1, weight=1)
    for t_f in range(10):
        torrent_path_frame.grid_columnconfigure(t_f, weight=1)

    # re-define torrent output if the user wants
    def torrent_save_output():
        torrent_file_input = filedialog.asksaveasfilename(parent=root, title='Save Torrent',
                                                          initialdir=pathlib.Path(torrent_file_path.get()).parent,
                                                          initialfile=pathlib.Path(torrent_file_path.get()).name,
                                                          filetypes=[("Torrent Files", "*.torrent")])
        if torrent_file_input:
            torrent_entry_box.config(state=NORMAL)
            torrent_entry_box.delete(0, END)
            torrent_entry_box.insert(END, pathlib.Path(torrent_file_input).with_suffix('.torrent'))
            torrent_file_path.set(pathlib.Path(torrent_file_input).with_suffix('.torrent'))
            torrent_entry_box.config(state=DISABLED)
            return True
        if not torrent_file_input:
            return False

    # torrent set path button
    torrent_button = HoverButton(torrent_path_frame, text="Set", command=torrent_save_output, foreground="white",
                                 background="#23272A", borderwidth="3", activeforeground="#3498db",
                                 activebackground="#23272A")
    torrent_button.grid(row=0, column=0, columnspan=1, padx=5, pady=(7, 5), sticky=N + S + E + W)

    # torrent path entry box
    torrent_entry_box = Entry(torrent_path_frame, borderwidth=4, bg="#565656", fg='white',
                              disabledforeground='white', disabledbackground="#565656")
    torrent_entry_box.grid(row=0, column=1, columnspan=9, padx=5, pady=(5, 5), sticky=N + S + E + W)
    torrent_entry_box.insert(END, pathlib.Path(torrent_file_path.get()).with_suffix('.torrent'))
    torrent_entry_box.config(state=DISABLED)

    # torrent piece frame
    torrent_piece_frame = LabelFrame(torrent_window, text=' Settings ', labelanchor="nw")
    torrent_piece_frame.grid(column=0, row=1, columnspan=10, padx=5, pady=(0, 3), sticky=E + W + N + S)
    torrent_piece_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 10, 'bold'))
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
        if torrent_piece.get() == 'Auto':
            calculate_pieces = math.ceil(file / float(Torrent.calculate_piece_size(file)))
        # if any other setting manually calculate it
        else:
            calculate_pieces = math.ceil(float(os.stat(pathlib.Path(encode_file_path.get())).st_size) / float(
                torrent_piece_choices[torrent_piece.get()]))

        # update label with piece size
        piece_size_label2.config(text=str(calculate_pieces))

    # piece size info label
    piece_size_info_label = Label(torrent_piece_frame, text='Piece Size:', bd=0, relief=SUNKEN, background='#363636',
                                  fg="#3498db", font=(set_font, set_font_size + 1))
    piece_size_info_label.grid(column=0, row=0, columnspan=1, pady=(5, 0), padx=(5, 0), sticky=W)

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
        "32 MiB": 33554432}
    torrent_piece = StringVar()
    torrent_piece.set("Auto")
    torrent_piece_menu = OptionMenu(torrent_piece_frame, torrent_piece, *torrent_piece_choices.keys(),
                                    command=set_piece_size)
    torrent_piece_menu.config(background="#23272A", foreground="white", highlightthickness=1, width=7,
                              activebackground="grey")
    torrent_piece_menu.grid(row=0, column=1, columnspan=1, pady=(7, 5), padx=(10, 5), sticky=W)
    torrent_piece_menu["menu"].configure(activebackground="grey", background="#23272A", foreground='white')

    # piece size label
    piece_size_label = Label(torrent_piece_frame, text='Total Pieces:', bd=0, relief=SUNKEN, background='#363636',
                             fg="#3498db", font=(set_font, set_font_size + 1))
    piece_size_label.grid(column=2, row=0, columnspan=1, pady=(5, 0), padx=(20, 0), sticky=W)

    # piece size label 2
    piece_size_label2 = Label(torrent_piece_frame, text='', bd=0, relief=SUNKEN, background='#363636',
                              fg="white", font=(set_font, set_font_size))
    piece_size_label2.grid(column=3, row=0, columnspan=1, pady=(7, 0), padx=(5, 5), sticky=W)

    # set piece size information
    set_piece_size()

    # torrent entry frame
    torrent_entry_frame = LabelFrame(torrent_window, text=' Fields ', labelanchor="nw")
    torrent_entry_frame.grid(column=0, row=2, columnspan=10, padx=5, pady=(0, 3), sticky=E + W + N + S)
    torrent_entry_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 10, 'bold'))
    torrent_entry_frame.grid_columnconfigure(0, weight=1)
    torrent_entry_frame.grid_columnconfigure(1, weight=200)
    torrent_entry_frame.grid_columnconfigure(2, weight=2000)
    torrent_entry_frame.grid_columnconfigure(3, weight=200000)
    torrent_entry_frame.grid_rowconfigure(0, weight=1)
    torrent_entry_frame.grid_rowconfigure(1, weight=1)

    # tracker url label
    torrent_tracker_label = Label(torrent_entry_frame, text='Tracker URL:', bd=0, relief=SUNKEN, background='#363636',
                                  fg="#3498db", font=(set_font, set_font_size))
    torrent_tracker_label.grid(row=0, column=0, columnspan=1, pady=(5, 0), padx=(5, 0), sticky=W)

    # tracker url entry box
    torrent_tracker_url_entry_box = Entry(torrent_entry_frame, borderwidth=4, bg="#565656", fg='white',
                                          disabledforeground='white', disabledbackground="#565656")
    torrent_tracker_url_entry_box.grid(row=0, column=1, columnspan=7, padx=(2, 5), pady=(5, 0), sticky=N + S + E + W)

    # if tracker url from config.ini is not empty, set it
    if config['torrent_settings']['tracker_url'] != '':
        torrent_tracker_url_entry_box.insert(END, config['torrent_settings']['tracker_url'])

    # torrent source label
    torrent_source_label = Label(torrent_entry_frame, text='Source:', bd=0, relief=SUNKEN, background='#363636',
                                 fg="#3498db", font=(set_font, set_font_size))
    torrent_source_label.grid(row=1, column=0, columnspan=1, pady=(5, 0), padx=(5, 0), sticky=W)

    # torrent source entry box
    torrent_source_entry_box = Entry(torrent_entry_frame, borderwidth=4, bg="#565656", fg='white',
                                     disabledforeground='white', disabledbackground="#565656")
    torrent_source_entry_box.grid(row=1, column=1, columnspan=5, padx=(2, 5), pady=5, sticky=N + S + E + W)

    # insert string 'BHD' into source
    torrent_source_entry_box.insert(END, 'BHD')

    # create torrent
    def create_torrent():
        if pathlib.Path(torrent_file_path.get()).is_file():
            # ask user if they would like to use the existing torrent file
            use_existing_file = messagebox.askyesno(parent=root, title='Use Existing File?',
                                                    message=f'"{pathlib.Path(torrent_file_path.get()).name}"\n\n'
                                                            f'File already exists.\n\nWould you like to use '
                                                            f'existing file?')
            # if user presses yes
            if use_existing_file:
                torrent_window_exit_function()
                return

            # if user press no
            if not use_existing_file:
                # ask user if they would like to overwrite
                check_overwrite = messagebox.askyesno(parent=root, title='Overwrite File?',
                                                      message='Would you like to overwrite file?')
                if not check_overwrite:  # if user does not want to overwrite file
                    save_new_file = torrent_save_output()  # call the torrent_save_output() function
                    if not save_new_file:  # if user press cancel in the torrent_save_output() window
                        return  # exit this function

        error = False  # set temporary error variable
        try:
            build_torrent = Torrent(path=pathlib.Path(encode_file_path.get()),
                                    trackers=str(torrent_tracker_url_entry_box.get()).strip(),
                                    private=True, source=source_entry_box.get().strip(),
                                    piece_size=torrent_piece_choices[torrent_piece.get()])
        except torf.URLError:  # if tracker url is invalid
            messagebox.showerror(parent=torrent_window, title='Error', message='Invalid Tracker URL')
            error = True  # set error to true
        except torf.PathError:  # if path to encoded file is invalid
            messagebox.showerror(parent=torrent_window, title='Error', message='Path to encoded file is invalid')
            error = True  # set error to true
        except torf.PieceSizeError:  # if piece size is incorrect
            messagebox.showerror(parent=torrent_window, title='Error', message='Piece size is incorrect')
            error = True  # set error to true

        if error:  # if error is true
            return  # exit the function

        # call back method to read/abort progress
        def torrent_progress(torrent, filepath, pieces_done, pieces_total):
            try:
                app_progress_bar['value'] = int(f'{pieces_done / pieces_total * 100:3.0f}')
                custom_style.configure('text.Horizontal.TProgressbar', text=f'{pieces_done / pieces_total * 100:3.0f}')
            except TclError:  # if window is closed return 0
                return 0  # returning 0 ends process

        # if callback torrent_progress returns anything other than None, exit the function
        if not build_torrent.generate(callback=torrent_progress):
            return  # exit function

        # once hash is completed build torrent file, overwrite automatically
        build_torrent.write(pathlib.Path(torrent_file_path.get()), overwrite=True)

        # if *.torrent exists then exit the window
        if pathlib.Path(torrent_file_path.get()).is_file():
            torrent_window_exit_function()

    # progress bar
    app_progress_bar = ttk.Progressbar(torrent_window, orient=HORIZONTAL, mode='determinate',
                                       style="text.Horizontal.TProgressbar")
    app_progress_bar.grid(row=3, column=0, columnspan=10, sticky=W + E, pady=5, padx=5)

    # set text to progress bar every time window opens to ''
    custom_style.configure('text.Horizontal.TProgressbar', text='')

    # create torrent button
    create_torrent_button = HoverButton(torrent_window, text="Create", activebackground="#23272A",
                                        command=lambda: threading.Thread(target=create_torrent).start(),
                                        foreground="white", background="#23272A", borderwidth="3",
                                        activeforeground="#3498db", width=12)
    create_torrent_button.grid(row=4, column=9, columnspan=1, padx=5, pady=(5, 0), sticky=E + S + N)

    # cancel torrent button
    cancel_torrent_button = HoverButton(torrent_window, text="Cancel", activebackground="#23272A",
                                        command=lambda: [automatic_workflow_boolean.set(False),
                                                         torrent_window_exit_function()],
                                        foreground="white", background="#23272A", borderwidth="3",
                                        activeforeground="#3498db", width=12)
    cancel_torrent_button.grid(row=4, column=0, columnspan=1, padx=5, pady=(5, 0), sticky=W + S + N)

    # if program is in automatic workflow mode
    if automatic_workflow_boolean.get():
        torrent_window.wait_window()


# open torrent window button
open_torrent_window_button = HoverButton(manual_workflow, text="Create Torrent", command=torrent_function_window,
                                         foreground="white", background="#23272A", borderwidth="3", width=12,
                                         activeforeground="#3498db", activebackground="#23272A", state=DISABLED)
open_torrent_window_button.grid(row=0, column=0, columnspan=1, padx=(10, 5), pady=1, sticky=E + W)

# automatic workflow frame
automatic_workflow = LabelFrame(root, text=' Automatic Workflow ', labelanchor="nw")
automatic_workflow.grid(column=3, row=4, columnspan=1, padx=5, pady=(5, 3), sticky=E)
automatic_workflow.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, set_font_size + 1, 'bold'))
automatic_workflow.grid_rowconfigure(0, weight=1)
automatic_workflow.grid_columnconfigure(0, weight=1)


# uploader window
def open_uploader_window(job_mode):
    # uploader window config parser
    uploader_window_config_parser = ConfigParser()
    uploader_window_config_parser.read(config_file)

    # if key is not found in the config.ini file
    if uploader_window_config_parser['bhd_upload_api']['key'] == '':
        api_checkpoint = messagebox.askyesno(parent=root, title='Missing API Key',
                                             message='You are missing your BHD API Key\n\nWould you like to add '
                                                     'this key now?\n\nNote: You can do this manually in '
                                                     '"Options > Api Key"')
        # if user presses yes
        if api_checkpoint:
            # open a new custom window to obtain and save the key to config.ini
            custom_input_prompt(root, 'BHD Upload Key:', 'bhd_upload_api', 'key')
            # define temp parser
            api_temp_parser = ConfigParser()
            api_temp_parser.read(config_file)
            # if bhd key is still nothing, set workflow to False, re-open root and top levels, then exit this function
            if api_temp_parser['bhd_upload_api']['key'] == '':
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
    if job_mode == 'auto' or job_mode == 'manual':
        movie_search_var.set('')
        tmdb_id_var.set('')
        imdb_id_var.set('')
        release_date_var.set('')
        rating_var.set('')

    # if job type is custom_advanced, reset the entire GUI for a clean and empty uploader window
    elif job_mode == 'custom_advanced':
        reset_gui()

    # uploader window exit function
    def upload_window_exit_function():
        # uploader exit parser
        uploader_exit_parser = ConfigParser()
        uploader_exit_parser.read(config_file)

        # save window position/geometry
        if upload_window.wm_state() == 'normal':
            if uploader_exit_parser['save_window_locations']['uploader'] != upload_window.geometry():
                if int(upload_window.geometry().split('x')[0]) >= upload_window_window_width or \
                        int(upload_window.geometry().split('x')[1].split('+')[0]) >= upload_window_window_height:
                    uploader_exit_parser.set('save_window_locations', 'uploader', upload_window.geometry())
                    with open(config_file, 'w') as uploader_exit_config_file:
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
    upload_window.title('BHDStudio - Uploader')
    upload_window.iconphoto(True, PhotoImage(data=base_64_icon))
    upload_window.configure(background="#363636")
    upload_window_window_height = 660
    upload_window_window_width = 720
    if uploader_window_config_parser['save_window_locations']['uploader'] == '':
        uploader_screen_width = upload_window.winfo_screenwidth()
        uploader_screen_height = upload_window.winfo_screenheight()
        uploader_x_coordinate = int((uploader_screen_width / 2) - (upload_window_window_width / 2))
        uploader_y_coordinate = int((uploader_screen_height / 2) - (upload_window_window_height / 2))
        upload_window.geometry(f"{upload_window_window_width}x{upload_window_window_height}+"
                               f"{uploader_x_coordinate}+{uploader_y_coordinate}")
    elif uploader_window_config_parser['save_window_locations']['uploader'] != '':
        upload_window.geometry(uploader_window_config_parser['save_window_locations']['uploader'])
    upload_window.protocol('WM_DELETE_WINDOW', upload_window_exit_function)

    # row and column configures
    for u_w_c in range(4):
        upload_window.grid_columnconfigure(u_w_c, weight=1)
    for u_w_r in range(7):
        upload_window.grid_rowconfigure(u_w_r, weight=1)

    # upload torrent options frame
    torrent_options_frame = LabelFrame(upload_window, text=' Torrent Input ', labelanchor="nw")
    torrent_options_frame.grid(column=0, row=0, columnspan=4, padx=5, pady=(5, 3), sticky=E + W)
    torrent_options_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 10, 'bold'))
    torrent_options_frame.grid_rowconfigure(0, weight=1)
    torrent_options_frame.grid_columnconfigure(0, weight=1)
    torrent_options_frame.grid_columnconfigure(1, weight=20)

    # torrent drag and drop function for torrent file
    def torrent_drop_function(event):
        torrent_file_input = [x for x in root.splitlist(event.data)][0]
        # ensure dropped file is a *.torrent file
        if pathlib.Path(torrent_file_input).suffix == '.torrent':
            torrent_file_path.set(str(pathlib.Path(torrent_file_input)))
        else:
            messagebox.showinfo(parent=upload_window, title='Info', message='Only .torrent files can be opened')

    # bind frame to drop torrent file
    torrent_options_frame.drop_target_register(DND_FILES)
    torrent_options_frame.dnd_bind('<<Drop>>', torrent_drop_function)

    # manual torrent file selection
    def open_torrent_file():
        torrent_input = filedialog.askopenfilename(parent=upload_window, title='Select Torrent', initialdir='/',
                                                   filetypes=[("Torrent Files", "*.torrent")])
        if torrent_input:
            torrent_file_path.set(str(pathlib.Path(torrent_input)))

    torrent_input_button = HoverButton(torrent_options_frame, text="Open", command=open_torrent_file,
                                       foreground="white", background="#23272A", borderwidth="3",
                                       activeforeground="#3498db", activebackground="#23272A")
    torrent_input_button.grid(row=0, column=0, columnspan=1, padx=5, pady=(7, 0), sticky=N + S + E + W)

    torrent_input_entry_box = Entry(torrent_options_frame, borderwidth=4, bg="#565656", fg='white', state=DISABLED,
                                    disabledforeground='white', disabledbackground="#565656",
                                    textvariable=torrent_file_path)
    torrent_input_entry_box.grid(row=0, column=1, columnspan=3, padx=5, pady=(5, 0), sticky=E + W)

    title_options_frame = LabelFrame(upload_window, text=' Title ', labelanchor="nw")
    title_options_frame.grid(column=0, row=3, columnspan=4, padx=5, pady=(5, 3), sticky=E + W)
    title_options_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 10, 'bold'))
    title_options_frame.grid_rowconfigure(0, weight=1)
    title_options_frame.grid_columnconfigure(0, weight=1)

    title_input_entry_box = Entry(title_options_frame, borderwidth=4, bg="#565656", fg='white',
                                  disabledforeground='white', disabledbackground="#565656")
    title_input_entry_box.grid(row=0, column=0, columnspan=4, padx=5, pady=(5, 3), sticky=E + W)

    upload_options_frame = LabelFrame(upload_window, text=' Options ', labelanchor="nw")
    upload_options_frame.grid(column=0, row=1, columnspan=4, padx=5, pady=(5, 3), sticky=E + W)
    upload_options_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 10, 'bold'))
    upload_options_frame.grid_rowconfigure(0, weight=1)
    upload_options_frame.grid_rowconfigure(1, weight=1)
    for u_o_f in range(6):
        upload_options_frame.grid_columnconfigure(u_o_f, weight=300)

    type_label = Label(upload_options_frame, text='Type', bd=0, relief=SUNKEN, background='#363636',
                       fg="#3498db", font=(set_font, set_font_size + 1))
    type_label.grid(column=0, row=0, columnspan=1, pady=(5, 0), padx=(5, 10), sticky=E)

    # resolution menu
    type_choices = {"720p": "720p", "1080p": "1080p", "2160p": "2160p"}
    type_var = StringVar()
    type_var_menu = OptionMenu(upload_options_frame, type_var, *type_choices.keys(), command=None)
    type_var_menu.config(background="#23272A", foreground="white", highlightthickness=1, width=12,
                         activebackground="grey")
    type_var_menu.grid(row=0, column=1, columnspan=1, pady=(7, 5), padx=(0, 5), sticky=W)
    type_var_menu["menu"].configure(activebackground="grey", background="#23272A", foreground='white')
    if encode_file_path.get().strip() != '' and pathlib.Path(encode_file_path.get().strip()).is_file():
        type_var.set(encode_file_resolution.get().strip())

    # Blu-ray selection menu (only Blu-ray for BHD)
    upload_source_label = Label(upload_options_frame, text='Source', bd=0, relief=SUNKEN, background='#363636',
                                fg="#3498db", font=(set_font, set_font_size + 1))
    upload_source_label.grid(column=2, row=0, columnspan=1, pady=(5, 0), padx=(5, 5), sticky=E)

    source_choices = {"Blu-Ray": "Blu-ray"}
    source_var = StringVar()
    source_var_menu = OptionMenu(upload_options_frame, source_var, *source_choices.keys(), command=None)
    source_var_menu.config(background="#23272A", foreground="white", highlightthickness=1, width=12,
                           activebackground="grey")
    source_var_menu.grid(row=0, column=3, columnspan=1, pady=(7, 5), padx=(2, 5), sticky=W)
    source_var_menu["menu"].configure(activebackground="grey", background="#23272A", foreground='white')
    source_var.set('Blu-Ray')  # set var to Blu-Ray

    # select edition menu
    edition_label = Label(upload_options_frame, text='Edition\n(Optional)', bd=0, relief=SUNKEN, background='#363636',
                          fg="#3498db", font=(set_font, set_font_size + 1))
    edition_label.grid(column=4, row=0, columnspan=1, pady=(5, 0), padx=5, sticky=E)

    edition_choices = {
        "N/A": "",
        "Collector's Edition": "Collector",
        "Director's Cut": "Director",
        "Extended Cut": "Extended",
        "Limited Edition": "Limited",
        "Special Edition": "Special",
        "Theatrical Cut": "Theatrical",
        "Uncut": "Uncut",
        "Unrated": "Unrated"}
    edition_var = StringVar()
    edition_var.set("N/A")
    edition_var_menu = OptionMenu(upload_options_frame, edition_var, *edition_choices.keys(), command=None)
    edition_var_menu.config(background="#23272A", foreground="white", highlightthickness=1, width=12,
                            activebackground="grey")
    edition_var_menu.grid(row=0, column=5, columnspan=1, pady=(7, 5), padx=(0, 5), sticky=E)
    edition_var_menu["menu"].configure(activebackground="grey", background="#23272A", foreground='white')

    # function to automatically grab edition based off of file name
    def check_edition_function():
        if encode_file_path.get().strip() != '' and pathlib.Path(encode_file_path.get()).is_file():
            edition_check = re.search('collector.*edition|director.*cut|extended.*cut|limited.*edition|s'
                                      'pecial.*edition|theatrical.*cut|uncut|unrated',
                                      pathlib.Path(encode_file_path.get()).stem, re.IGNORECASE)
            if edition_check:
                if 'collector' in str(edition_check.group()).lower():
                    edition_var.set("Collector's Edition")
                elif 'director' in str(edition_check.group()).lower():
                    edition_var.set("Director's Cut")
                elif 'extended' in str(edition_check.group()).lower():
                    edition_var.set("Extended Cut")
                elif 'limited' in str(edition_check.group()).lower():
                    edition_var.set("Limited Edition")
                elif 'special' in str(edition_check.group()).lower():
                    edition_var.set("Special Edition")
                elif 'theatrical' in str(edition_check.group()).lower():
                    edition_var.set("Theatrical Cut")
                elif 'uncut' in str(edition_check.group()).lower():
                    edition_var.set("Uncut")
                elif 'unrated' in str(edition_check.group()).lower():
                    edition_var.set("Unrated")

    check_edition_function()  # run function to check edition upon opening the window automatically

    # custom edition label and entry box
    edition_label = Label(upload_options_frame, text='Edition\n(Custom)', bd=0, relief=SUNKEN, background='#363636',
                          fg="#3498db", font=(set_font, set_font_size + 1))
    edition_label.grid(column=0, row=1, columnspan=1, pady=(5, 0), padx=5, sticky=E)

    edition_entry_box = Entry(upload_options_frame, borderwidth=4, bg="#565656", fg='white',
                              disabledforeground='white', disabledbackground="#565656")
    edition_entry_box.grid(row=1, column=1, columnspan=5, padx=5, pady=(5, 0), sticky=E + W)

    # a constant function to check if user types in the custom edition box, this set's edition to N/A and accepts text
    def reset_disable_set_edition():
        if edition_entry_box.get().strip() != '':
            edition_var.set("N/A")
            edition_var_menu.config(state=DISABLED)
        else:
            edition_var_menu.config(state=NORMAL)
            check_edition_function()
        upload_window.after(50, reset_disable_set_edition)

    reset_disable_set_edition()  # launch loop to check edition

    # IMDB and TMDB frame
    imdb_tmdb_frame = LabelFrame(upload_window, text=' IMDB / TMDB ', labelanchor="nw")
    imdb_tmdb_frame.grid(column=0, row=2, columnspan=8, padx=5, pady=(5, 3), sticky=E + W)
    imdb_tmdb_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 10, 'bold'))
    imdb_tmdb_frame.grid_rowconfigure(0, weight=1)
    imdb_tmdb_frame.grid_rowconfigure(1, weight=1)
    imdb_tmdb_frame.grid_columnconfigure(0, weight=1)
    imdb_tmdb_frame.grid_columnconfigure(1, weight=300)
    imdb_tmdb_frame.grid_columnconfigure(7, weight=1)

    # search frame inside the IMDB and TMDB frame
    imdb_tmdb_search_frame = LabelFrame(imdb_tmdb_frame, text=' Search ', labelanchor="n")
    imdb_tmdb_search_frame.grid(column=0, row=0, columnspan=8, padx=5, pady=(5, 3), sticky=E + W)
    imdb_tmdb_search_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 9, 'bold'))
    imdb_tmdb_search_frame.grid_rowconfigure(0, weight=1)
    imdb_tmdb_search_frame.grid_columnconfigure(0, weight=1)

    # search entry box
    search_entry_box = Entry(imdb_tmdb_search_frame, borderwidth=4, bg="#565656", fg='white',
                             disabledforeground='white', disabledbackground="#565656", textvariable=movie_search_var)
    search_entry_box.grid(row=0, column=0, columnspan=3, padx=5, pady=(5, 0), sticky=E + W)

    # if encode file is loaded, parse the name of the file to get autoload it into the search box for the user
    if pathlib.Path(encode_file_path.get()).stem != '':
        search_entry_box.delete(0, END)  # clear the search box
        # use regex to find the movie name
        movie_name = re.finditer(r'\d{4}(?!p)', pathlib.Path(encode_file_path.get()).stem, re.IGNORECASE)
        movie_name_extraction = []  # create empty list
        for match in movie_name:  # get the "span" from the movie name
            movie_name_extraction.append(match.span())
        # extract the full movie name (removing anything that is not needed from the filename)
        full_movie_name = pathlib.Path(encode_file_path.get()).stem[0:int(
            movie_name_extraction[-1][-1])].replace('.', ' ').strip()
        search_entry_box.insert(END, full_movie_name)  # insert this full movie name into the search box

    # function to search tmdb for information
    def search_movie_db_ids_function(*args):
        # set parser
        movie_window_parser = ConfigParser()
        movie_window_parser.read(config_file)

        # if there is text inside the search box enable the search
        if movie_search_var.get().strip() != '':
            # movie window exit function
            def movie_info_exit_function():
                # set stop thread to True
                stop_thread.set()

                # set parser
                exit_movie_window_parser = ConfigParser()
                exit_movie_window_parser.read(config_file)

                # save window position/geometry
                if movie_info_window.wm_state() == 'normal':
                    if exit_movie_window_parser['save_window_locations']['movie_info'] != movie_info_window.geometry():
                        if int(movie_info_window.geometry().split('x')[0]) >= movie_window_width or \
                                int(movie_info_window.geometry().split('x')[1].split('+')[0]) >= movie_window_height:
                            exit_movie_window_parser.set('save_window_locations', 'movie_info',
                                                         movie_info_window.geometry())
                            with open(config_file, 'w') as root_exit_config_file:
                                exit_movie_window_parser.write(root_exit_config_file)

                # close movie info window
                movie_info_window.destroy()

            def get_imdb_update_filename():
                # check if imdb id is missing
                if imdb_id_var.get() == "None":
                    messagebox.showerror(parent=movie_info_window, title='Missing IMDB ID',
                                         message='Please manually search for the proper IMDB ID and manually '
                                                 'add it to the entry box')
                    return

                if 't' in imdb_id_var.get():
                    imdb_module = Cinemagoer()
                    movie = imdb_module.get_movie(str(imdb_id_var.get()).replace('t', ''))
                    imdb_movie_name = str(movie['long imdb title']).replace(')', '').replace('(', '')
                else:
                    return

                # check edition
                if edition_var.get() == "N/A":
                    # if edition is set to "N/A" then check for custom
                    if edition_entry_box.get().strip() != '':
                        # if custom edition box is not empty define custom edition string
                        edition_string = edition_entry_box.get().strip() + ' '
                    else:  # if custom edition box is empty, define an empty string
                        edition_string = ''
                # if edition is not "N/A", get edition from menu and define string with the edition type
                elif edition_var.get() != 'N/A':
                    edition_string = edition_var.get() + ' '

                complete_filename = ''  # define complete_filename

                # create a completed filename based on all the above information for 720p/1080p files
                if encode_file_resolution.get() == '720p' or encode_file_resolution.get() == '1080p':
                    complete_filename = f"{edition_string}BluRay {type_var.get()} " \
                                        f"{encode_file_audio.get()} x264-BHDStudio"

                # create a completed filename based on all the above information for 2160p files
                elif encode_file_resolution.get() == '2160p':
                    # check for HDR string
                    if encode_hdr_string.get() != '':
                        add_hdr_string = ' ' + encode_hdr_string.get()
                    complete_filename = f"{edition_string}UHD BluRay {type_var.get()} " \
                                        f"{encode_file_audio.get()}{add_hdr_string} x265-BHDStudio"

                # clear the title input entry box and replace with the new created name for BHD
                title_input_entry_box.delete(0, END)
                if complete_filename != '':
                    title_input_entry_box.insert(END, f"{imdb_movie_name} {complete_filename}")
                movie_info_exit_function()  # close movie_info_window

            # movie info window
            movie_info_window = Toplevel()
            movie_info_window.configure(background="#363636")  # Set's the background color
            movie_info_window.title('Movie Selection')  # Toplevel Title
            movie_window_height = 600
            movie_window_width = 1000
            if movie_window_parser['save_window_locations']['movie_info'] == '':
                movie_screen_width = movie_info_window.winfo_screenwidth()
                movie_screen_height = movie_info_window.winfo_screenheight()
                movie_x_coordinate = int((movie_screen_width / 2) - (movie_window_width / 2))
                movie_y_coordinate = int((movie_screen_height / 2) - (movie_window_height / 2))
                movie_info_window.geometry(f"{movie_window_width}x{movie_window_height}+"
                                           f"{movie_x_coordinate}+{movie_y_coordinate}")
            elif movie_window_parser['save_window_locations']['movie_info'] != '':
                movie_info_window.geometry(movie_window_parser['save_window_locations']['movie_info'])
            movie_info_window.grab_set()
            movie_info_window.protocol('WM_DELETE_WINDOW', movie_info_exit_function)

            # Row/Grid configures
            for m_i_w_c in range(6):
                movie_info_window.grid_columnconfigure(m_i_w_c, weight=1)
            for m_i_w_r in range(4):
                movie_info_window.grid_rowconfigure(m_i_w_r, weight=1)
            # Row/Grid configures

            movie_listbox_frame = Frame(movie_info_window)  # Set dynamic listbox frame
            movie_listbox_frame.grid(column=0, columnspan=6, row=0, padx=5, pady=(5, 3), sticky=N + S + E + W)
            movie_listbox_frame.grid_rowconfigure(0, weight=1)
            movie_listbox_frame.grid_columnconfigure(0, weight=1)

            right_scrollbar = Scrollbar(movie_listbox_frame, orient=VERTICAL)  # Scrollbars
            bottom_scrollbar = Scrollbar(movie_listbox_frame, orient=HORIZONTAL)

            # Create listbox
            movie_listbox = Listbox(movie_listbox_frame, xscrollcommand=bottom_scrollbar.set, activestyle="none",
                                    yscrollcommand=right_scrollbar.set, bd=2, bg="black", fg="#3498db", height=10,
                                    selectbackground='black', selectforeground='lime green', selectmode=SINGLE,
                                    font=(set_font, set_font_size + 2))
            movie_listbox.grid(row=0, column=0, columnspan=5, sticky=N + E + S + W)

            # add scrollbars to the listbox
            right_scrollbar.config(command=movie_listbox.yview)
            right_scrollbar.grid(row=0, column=5, sticky=N + W + S)
            bottom_scrollbar.config(command=movie_listbox.xview)
            bottom_scrollbar.grid(row=1, column=0, sticky=W + E + N)

            # define stop thread event
            stop_thread = threading.Event()

            # define api check function
            def run_api_check():
                if movie_search_active.get():
                    return
                movie_search_active.set(True)

                movie_listbox.delete(0, END)
                movie_listbox.insert(END, 'Loading, please wait...')

                collect_title = re.finditer(r'\d{4}', movie_search_var.get().strip())

                title_span = []
                for title_only in collect_title:
                    title_span.append(title_only.span())

                try:
                    movie_title = str(movie_search_var.get()[0:title_span[-1][0]]).replace('.', ' ').replace(
                        '(', '').replace(')', '').strip()
                except IndexError:
                    movie_title = str(movie_search_var.get().strip())

                collect_year = re.findall(r'\d{4}', movie_search_var.get().strip())
                if collect_year:
                    movie_year = collect_year[-1]
                else:
                    movie_year = ''

                search_movie = requests.get(f"https://api.themoviedb.org/3/search/movie?api_key={tmdb_api_key}&language"
                                            f"=en-US&page=1&include_adult=false&query={movie_title}&year={movie_year}")
                movie_dict = {}

                for results in search_movie.json()['results']:
                    # find imdb_id data through tmdb
                    imdb_id = requests.get(
                        f"https://api.themoviedb.org/3/movie/{results['id']}/external_ids?api_key={tmdb_api_key}")
                    # if release date string isn't nothing
                    if imdb_id.json()['imdb_id'] and results['release_date']:
                        # convert release date to standard month/day/year
                        release_date = str(results['release_date']).split('-')
                        full_release_date = f"{release_date[1]}-{release_date[2]}-{release_date[0]}"
                        # update dictionary
                        movie_dict.update({f"{results['title']} ({(release_date)[0]})": {
                            "tvdb_id": f"{results['id']}", "imdb_id": f"{imdb_id.json()['imdb_id']}",
                            "plot": f"{results['overview']}", "vote_average": f"{str(results['vote_average'])}",
                            "full_release_date": full_release_date}})
                        # if thread event stop was called
                        if stop_thread.is_set():
                            movie_search_active.set(False)  # set active search to false
                            break  # break from loop

                # if stop_thread was called and closed the loop
                if not movie_search_active.get():
                    return  # exit function

                # clear movie list box
                movie_listbox.delete(0, END)

                # add all the movies into the listbox
                for key in movie_dict.keys():
                    movie_listbox.insert(END, key)

                # function that is ran each time a movie is selected to update all the information in the window
                def update_movie_info(event):
                    selection = event.widget.curselection()  # get current selection
                    # if there is a selection
                    if selection:
                        movie_listbox_index = selection[0]  # define index of selection
                        movie_data = event.widget.get(movie_listbox_index)

                        # delete plot text and update it
                        plot_scrolled_text.delete("1.0", END)
                        plot_scrolled_text.insert(END, movie_dict[movie_data]['plot'])

                        # update imdb and tmdb entry box's
                        imdb_id_var.set(movie_dict[movie_data]['imdb_id'])
                        tmdb_id_var.set(movie_dict[movie_data]['tvdb_id'])

                        # update release date label
                        release_date_var.set(movie_dict[movie_data]['full_release_date'])

                        # update rating label
                        rating_var.set(f"{movie_dict[movie_data]['vote_average']} / 10")

                movie_listbox.bind("<<ListboxSelect>>", update_movie_info)  # bind listbox select event to the updater
                movie_search_active.set(False)  # once listbox has been updated, set active to False

            # plot frame
            plot_frame = LabelFrame(movie_info_window, text=' Plot ', labelanchor="nw")
            plot_frame.grid(column=0, row=1, columnspan=6, padx=5, pady=(5, 3), sticky=E + W)
            plot_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 9, 'bold'))
            plot_frame.grid_rowconfigure(0, weight=1)
            plot_frame.grid_columnconfigure(0, weight=1)

            # plot text window
            plot_scrolled_text = scrolledtextwidget.ScrolledText(plot_frame, height=6)
            plot_scrolled_text.grid(row=0, column=0, columnspan=6, pady=(0, 5), padx=5, sticky=E + W)
            plot_scrolled_text.config(bg='black', fg='#CFD2D1', bd=2)

            # internal search frame
            internal_search_frame = LabelFrame(movie_info_window, text=' Search ', labelanchor="nw")
            internal_search_frame.grid(column=0, row=2, columnspan=6, padx=5, pady=(5, 3), sticky=E + W)
            internal_search_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 9, 'bold'))
            internal_search_frame.grid_rowconfigure(0, weight=1)
            internal_search_frame.grid_columnconfigure(0, weight=1)

            # internal search box
            search_entry_box2 = Entry(internal_search_frame, borderwidth=4, bg="#565656", fg='white',
                                      disabledforeground='white', disabledbackground="#565656",
                                      textvariable=movie_search_var)
            search_entry_box2.grid(row=0, column=0, columnspan=5, padx=5, pady=(5, 3), sticky=E + W)

            # function to search again
            def start_search_again(*args):
                stop_thread.clear()  # set stop thread to false
                threading.Thread(target=run_api_check).start()

            # bind "Enter" key to run the function
            search_entry_box2.bind("<Return>", start_search_again)

            # internal search button
            search_button2 = HoverButton(internal_search_frame, text="Search", activebackground="#23272A",
                                         command=start_search_again,
                                         foreground="white", background="#23272A",
                                         borderwidth="3", activeforeground="#3498db", width=12)
            search_button2.grid(row=0, column=5, columnspan=1, padx=5, pady=(5, 3), sticky=E + S + N)

            # function to enable and disable the internal search button if a current search is active
            def enable_disable_internal_search_btn():
                if movie_search_active.get():  # if search is active disable button
                    search_button2.config(state=DISABLED)
                else:  # if search is not active enable button
                    search_button2.config(state=NORMAL)
                movie_info_window.after(50, enable_disable_internal_search_btn)

            # start loop to check internal button
            enable_disable_internal_search_btn()

            # information frame
            information_frame = Frame(movie_info_window, bd=0, bg="#363636")
            information_frame.grid(column=0, row=3, columnspan=7, padx=5, pady=(5, 3), sticky=E + W)
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
            imdb_button2 = Button(information_frame, image=imdb_img, borderwidth=0, cursor='hand2', bg="#363636",
                                  activebackground="#363636", command=open_imdb_link)
            imdb_button2.grid(row=0, column=0, columnspan=1, rowspan=2, padx=5, pady=(5, 2), sticky=W)
            imdb_button2.photo = imdb_img

            # imdb entry box internal
            imdb_entry_box2 = Entry(information_frame, borderwidth=4, bg="#565656", fg='white',
                                    disabledforeground='white', disabledbackground="#565656", textvariable=imdb_id_var)
            imdb_entry_box2.grid(row=0, column=1, rowspan=2, padx=5, pady=(5, 2), sticky=W)

            # tmdb clickable icon button
            tmdb_button2 = Button(information_frame, image=tmdb_img, borderwidth=0, cursor='hand2', bg="#363636",
                                  activebackground="#363636", command=open_tmdb_link)
            tmdb_button2.grid(row=0, column=2, rowspan=2, padx=5, pady=(5, 2), sticky=W)
            tmdb_button2.photo = tmdb_img

            # tmdb internal entry box
            tmdb_entry_box2 = Entry(information_frame, borderwidth=4, bg="#565656", fg='white',
                                    disabledforeground='white', disabledbackground="#565656", textvariable=tmdb_id_var)
            tmdb_entry_box2.grid(row=0, column=3, rowspan=2, padx=5, pady=(5, 2), sticky=W)

            # release date labels
            release_date_label = Label(information_frame, text='Release Date:', background='#363636', fg="#3498db",
                                       font=(set_font, set_font_size + 1, "bold"))
            release_date_label.grid(row=0, column=4, sticky=W, padx=(5, 0), pady=(5, 2))

            release_date_label2 = Label(information_frame, textvariable=release_date_var, width=10,
                                        background='#363636', fg="#3498db", font=(set_font, set_font_size))
            release_date_label2.grid(row=0, column=5, sticky=W, padx=(1, 5), pady=(5, 2))

            # rating labels
            rating_label = Label(information_frame, text='           Rating:', background='#363636', fg="#3498db",
                                 font=(set_font, set_font_size + 1, "bold"))
            rating_label.grid(row=1, column=4, sticky=W, padx=(5, 0), pady=(5, 2))

            rating_label2 = Label(information_frame, textvariable=rating_var, width=10,
                                  background='#363636', fg="#3498db", font=(set_font, set_font_size))
            rating_label2.grid(row=1, column=5, sticky=W, padx=(1, 5), pady=(5, 2))

            # confirm movie button
            confirm_movie_btn = HoverButton(information_frame, text="Confirm", command=get_imdb_update_filename,
                                            foreground="white", background="#23272A", borderwidth="3", width=10,
                                            activeforeground="#3498db", activebackground="#23272A")
            confirm_movie_btn.grid(row=1, column=6, padx=5, pady=(5, 2), sticky=E)

            movie_info_window.focus_set()  # focus's id window
            stop_thread.clear()  # set stop thread event to false
            threading.Thread(target=run_api_check).start()

    # search button and bind to use command from "Enter" key
    search_entry_box.bind("<Return>", search_movie_db_ids_function)
    search_button = HoverButton(imdb_tmdb_search_frame, text="Search", activebackground="#23272A",
                                command=search_movie_db_ids_function,
                                foreground="white", background="#23272A",
                                borderwidth="3", activeforeground="#3498db", width=12)
    search_button.grid(row=0, column=3, columnspan=1, padx=5, pady=(5, 0), sticky=E + S + N)

    # imdb label
    imdb_label = Label(imdb_tmdb_frame, text='IMDB ID\n(Required)', background='#363636',
                       fg="#3498db", font=(set_font, set_font_size + 1))
    imdb_label.grid(column=0, row=1, columnspan=1, pady=(5, 0), padx=5, sticky=W)

    # imdb entry box
    imdb_entry_box = Entry(imdb_tmdb_frame, borderwidth=4, bg="#565656", fg='white',
                           disabledforeground='white', disabledbackground="#565656", textvariable=imdb_id_var)
    imdb_entry_box.grid(row=1, column=1, columnspan=6, padx=5, pady=(5, 0), sticky=E + W)

    # decode imdb img for use with the buttons
    decode_resize_imdb_image = Image.open(BytesIO(base64.b64decode(imdb_icon))).resize((35, 35))
    imdb_img = ImageTk.PhotoImage(decode_resize_imdb_image)

    # upload window imdb button with decoded image
    imdb_button = Button(imdb_tmdb_frame, image=imdb_img, borderwidth=0, cursor='hand2', bg="#363636",
                         activebackground="#363636", command=open_imdb_link)
    imdb_button.grid(row=1, column=7, columnspan=1, padx=5, pady=(5, 0), sticky=W)
    imdb_button.photo = imdb_img

    # tmdb label
    tmdb_label = Label(imdb_tmdb_frame, text='TMDB ID\n(Required)', background='#363636',
                       fg="#3498db", font=(set_font, set_font_size + 1))
    tmdb_label.grid(column=0, row=2, columnspan=1, pady=(5, 0), padx=5, sticky=W)

    # tmdb upload window entry box
    tmdb_entry_box = Entry(imdb_tmdb_frame, borderwidth=4, bg="#565656", fg='white',
                           disabledforeground='white', disabledbackground="#565656", textvariable=tmdb_id_var)
    tmdb_entry_box.grid(row=2, column=1, columnspan=6, padx=5, pady=(5, 0), sticky=E + W)

    # decode tmdb img for use with the buttons
    decode_resize_tmdb_image = Image.open(BytesIO(base64.b64decode(tmdb_icon))).resize((35, 35))
    tmdb_img = ImageTk.PhotoImage(decode_resize_tmdb_image)

    # tmdb clickable icon button in upload window with decoded image
    tmdb_button = Button(imdb_tmdb_frame, image=tmdb_img, borderwidth=0, cursor='hand2', bg="#363636",
                         activebackground="#363636", command=open_tmdb_link)
    tmdb_button.grid(row=2, column=7, columnspan=1, padx=5, pady=(5, 0), sticky=W)
    tmdb_button.photo = tmdb_img

    # info frame
    info_frame = LabelFrame(upload_window, text=' Info ', labelanchor="nw")
    info_frame.grid(column=0, row=4, columnspan=4, padx=5, pady=(5, 3), sticky=E + W)
    info_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 10, 'bold'))
    info_frame.grid_rowconfigure(0, weight=1)
    info_frame.grid_columnconfigure(0, weight=1)
    info_frame.grid_columnconfigure(1, weight=100)
    info_frame.grid_columnconfigure(2, weight=1)
    info_frame.grid_columnconfigure(3, weight=100)

    # function when media info video file is dropped/opened, it's given a variable when called
    def update_media_info_function(m_i_input):
        # if input is *.txt
        if pathlib.Path(m_i_input).suffix == '.txt':
            # open file and set variable
            with open(pathlib.Path(m_i_input), mode='rt', encoding="utf-8") as m_i_file:
                encode_media_info.set(m_i_file.read())
        # if input is *.mp4
        elif pathlib.Path(m_i_input).suffix == '.mp4':
            # parse file with mediainfo to txt and set variable
            m_i_dropped = MediaInfo.parse(pathlib.Path(m_i_input), full=False, output="")  # parse mediainfo
            encode_media_info.set(m_i_dropped)
        media_info_entry.config(state=NORMAL) # enable entry box
        media_info_entry.delete(0, END)  # clear entry box
        media_info_entry.insert(END, 'MediaInfo loaded from file')  # insert string
        media_info_entry.config(state=DISABLED)  # disable entry box

    # function for dropped/open nfo input from txt/nfo file
    def update_nfo_desc_function(nfo_desc_input):
        # open nfo file and set it as variable
        with open(pathlib.Path(nfo_desc_input), mode='rt', encoding="utf-8") as nfo_file_open:
            nfo_info_var.set(nfo_file_open.read())
        nfo_desc_entry.config(state=NORMAL)  # enable entry box
        nfo_desc_entry.delete(0, END)  # clear entry box
        nfo_desc_entry.insert(END, 'NFO loaded from file')  # insert string
        nfo_desc_entry.config(state=DISABLED)  # disable entry box

    # torrent drag and drop function for media info and torrent files
    def media_info_nfo_drop_function(event):
        m_i_nfo_drop = [x for x in root.splitlist(event.data)][0]  # dropped path to file
        # if file is *.mp4, call update media info func
        if pathlib.Path(m_i_nfo_drop).suffix == '.mp4':
            update_media_info_function(m_i_nfo_drop)
        # if file is *.nfo or *.txt, call update nfo func
        elif pathlib.Path(m_i_nfo_drop).suffix == '.nfo' or pathlib.Path(m_i_nfo_drop).suffix == '.txt':
            update_nfo_desc_function(m_i_nfo_drop)

    # bind frame to drop media info and torrent files
    info_frame.drop_target_register(DND_FILES)
    info_frame.dnd_bind('<<Drop>>', media_info_nfo_drop_function)

    # manual media info dialog, this accepts txt and .mp4
    def open_media_info_text():
        m_i_t = filedialog.askopenfilename(parent=upload_window, title='Select Mediainfo File', initialdir='/',
                                           filetypes=[("Text, MP4", "*.txt *.mp4")])
        if m_i_t:  # if selection is made, run the media info function
            update_media_info_function(m_i_t)

    # media info button
    media_info_button = HoverButton(info_frame, text="MediaInfo", command=open_media_info_text, foreground="white",
                                    background="#23272A", borderwidth="3", activeforeground="#3498db", width=15,
                                    activebackground="#23272A")
    media_info_button.grid(row=0, column=0, columnspan=1, padx=5, pady=(5, 0), sticky=W + S + N)

    # media info entry box
    media_info_entry = Entry(info_frame, borderwidth=4, bg="#565656", fg='white',
                             disabledforeground='white', disabledbackground="#565656", state=DISABLED)
    media_info_entry.grid(row=0, column=1, columnspan=1, padx=5, pady=(5, 0), sticky=E + W)
    # if automatic work flow is set and encode media info is not blank, assume it's been automatically loaded
    if automatic_workflow_boolean and encode_media_info.get() != '':
        media_info_entry.config(state=NORMAL)  # enable entry box
        media_info_entry.delete(0, END)  # clear entry box
        media_info_entry.insert(END, 'MediaInfo Loaded Internally')  # insert string
        media_info_entry.config(state=DISABLED)  # disable entry box

    # manual nfo open dialog, this accepts *.txt and *.nfo files
    def open_nfo_info_text_nfo():
        nfo_desc = filedialog.askopenfilename(parent=upload_window, title='Select NFO', initialdir='/',
                                              filetypes=[("NFO, Text", "*.txt *.nfo")])
        if nfo_desc:  # if selection is made, run the nfo function
            update_nfo_desc_function(nfo_desc)

    # nfo load button
    nfo_desc_button = HoverButton(info_frame, text="NFO / Description", command=open_nfo_info_text_nfo,
                                  foreground="white", background="#23272A", borderwidth="3",
                                  activeforeground="#3498db", width=15, activebackground="#23272A")
    nfo_desc_button.grid(row=0, column=2, columnspan=1, padx=5, pady=(5, 0), sticky=E + S + N)

    # nfo entry
    nfo_desc_entry = Entry(info_frame, borderwidth=4, bg="#565656", fg='white',
                           disabledforeground='white', disabledbackground="#565656", state=DISABLED)
    nfo_desc_entry.grid(row=0, column=3, columnspan=1, padx=5, pady=(5, 0), sticky=E + W)
    # if automatic work flow is set and nfo info is not blank, assume it's been automatically loaded
    if automatic_workflow_boolean and nfo_info_var.get() != '':
        nfo_desc_entry.config(state=NORMAL)
        nfo_desc_entry.insert(END, 'NFO Loaded Internally')
        nfo_desc_entry.config(state=DISABLED)

    # misc options frame
    misc_options_frame = LabelFrame(upload_window, text=' Upload Options ', labelanchor="nw")
    misc_options_frame.grid(column=0, row=5, columnspan=3, padx=5, pady=(5, 3), sticky=E + W)
    misc_options_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, set_font_size + 1, 'bold'))
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
        chk_button_parser.set('live_release', 'value', str(save_checkbutton))
        with open(config_file, 'w') as c_b_config:
            chk_button_parser.write(c_b_config)

    live_checkbox = Checkbutton(misc_options_frame, text='Send to Drafts', variable=live_boolean, state=DISABLED,
                                onvalue=0, offvalue=1, command=update_checkbutton_info)
    live_checkbox.grid(row=0, column=0, padx=5, pady=(5, 3), sticky=E + W)
    live_checkbox.configure(background="#363636", foreground="white", activebackground="#363636",
                            activeforeground="white", selectcolor="#363636",
                            font=(set_font, set_font_size + 1))
    live_boolean.set(0)

    # parser to check for password and remember settings if enabled
    live_temp_parser = ConfigParser()
    live_temp_parser.read(config_file)
    # if sticky gives users the password to live release
    if live_temp_parser['live_release']['password'] == "StickySaidSo":
        live_checkbox.config(state=NORMAL)  # enable check button
        try:  # try to set check button based off of config
            live_boolean.set(int(live_temp_parser['live_release']['value']))
        except ValueError:  # if check button is blank or value error
            live_boolean.set(0)  # set it to the default 0

    anonymous_checkbox = Checkbutton(misc_options_frame, text='Anonymous', variable=anonymous_boolean, onvalue=1,
                                     offvalue=0)
    anonymous_checkbox.grid(row=0, column=1, padx=5, pady=(5, 3), sticky=W)
    anonymous_checkbox.configure(background="#363636", foreground="white", activebackground="#363636",
                                 activeforeground="white", selectcolor="#363636",
                                 font=(set_font, set_font_size + 1))
    anonymous_boolean.set(0)

    # upload to beyond hd api function
    def upload_to_api():
        # set config parser
        api_parser = ConfigParser()
        api_parser.read(config_file)

        # upload status window
        upload_status_window = Toplevel()
        upload_status_window.configure(background="#363636")
        upload_status_window.geometry(f'{460}x{200}+{str(int(upload_window.geometry().split("+")[1]) + 156)}+'
                                      f'{str(int(upload_window.geometry().split("+")[2]) + 230)}')
        upload_status_window.resizable(0, 0)
        upload_status_window.grab_set()
        upload_status_window.wm_overrideredirect(True)
        upload_window.wm_attributes('-alpha', 0.90)  # set parent window to be slightly transparent
        upload_status_window.grid_rowconfigure(0, weight=1)
        upload_status_window.grid_columnconfigure(0, weight=1)

        # encoder name frame
        upload_output_frame = Frame(upload_status_window, highlightbackground="white", highlightthickness=2,
                                    bg="#363636", highlightcolor='white')
        upload_output_frame.grid(column=0, row=0, columnspan=3, sticky=N + S + E + W)
        for e_n_f in range(3):
            upload_output_frame.grid_columnconfigure(e_n_f, weight=1)
            upload_output_frame.grid_rowconfigure(e_n_f, weight=1)

        # create label
        upload_status_info = scrolledtextwidget.ScrolledText(upload_output_frame, height=7, bg='#565656',
                                                             fg='white', bd=4)
        upload_status_info.grid(row=0, column=0, columnspan=3, pady=(2, 0), padx=5, sticky=E + W)
        upload_status_info.insert(END, 'Uploading, please wait...')
        upload_status_info.config(state=DISABLED)

        # function to save new name to config.ini
        def encoder_okay_func():
            upload_window.wm_attributes('-alpha', 1.0)  # restore transparency
            upload_status_window.destroy()  # close window

        # create 'OK' button
        uploader_okay_btn = HoverButton(upload_output_frame, text="OK", command=encoder_okay_func,
                                        foreground="white", background="#23272A", borderwidth="3",
                                        activeforeground="#3498db", width=8, activebackground="#23272A")
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
        api_link = f"https://beyond-hd.me/api/upload/{api_parser['bhd_upload_api']['key']}"

        # define upload params for BHD
        upload_payload_params = {"name": title_input_entry_box.get().strip(),
                                 "category_id": 1, "type": type_choices[type_var.get()],
                                 "source": source_choices[source_var.get()], "internal": 1,
                                 "imdb_id": imdb_id_var.get(), "tmdb_id": tmdb_id_var.get(),
                                 "description": nfo_info_var.get(), "nfo": nfo_info_var.get(),
                                 "live": live_release, "anon": anonymous_release,
                                 "stream": "optimized", "promo": 2}

        # if any preset edition selections are selected add the params and value
        if edition_var.get() != 'N/A':
            upload_payload_params.update({"edition": edition_choices[edition_var.get()]})

        # if a custom edition is typed add the params and value
        if edition_entry_box.get().strip() != '':
            upload_payload_params.update({"custom_edition": edition_entry_box.get().strip()})

        # upload function in a different thread
        def run_upload_in_different_thread():
            try:  # try to upload
                upload_job = requests.post(api_link, upload_payload_params,
                                           files={'file': open(pathlib.Path(torrent_file_path.get()), 'rb'),
                                                  "mediainfo": encode_media_info.get()})
            except requests.exceptions.ConnectionError:  # if there is a connection error show function
                encoder_okay_func()  # this runs the okay button function to close the window and restore transparency
                messagebox.showerror(parent=upload_window, title='Error', message='There is a connection error, check '
                                                                                  'your internet connection')
                return  # exit the function

            upload_status_info.config(state=NORMAL)  # enable scrolled text box
            upload_status_info.delete("1.0", END)  # delete all contents of the box
            if upload_job.status_code == 200:  # if upload returns a status code '200', assume success
                if upload_job.json()['status_code'] == 1 and 'saved' in upload_job.json()['status_message'] \
                        and upload_job.json()['success']:
                    upload_status_info.insert(END, 'Upload is successful!\n\nUpload has been successfully '
                                                   'saved as a draft on site')
                else:
                    upload_status_info.insert(END, f"There was an error:\n\n{upload_job.json()['status_message']}")
            elif upload_job.status_code == 404:  # if upload returns a status code '400', site error
                upload_status_info.insert(END, f"Upload failed! This is likely a problem with the site\n\n"
                                               f"{upload_job.json()['status_message']}")
            elif upload_job.status_code == 500:  # if upload returns a status code '400', critical site error
                upload_status_info.insert(END, "Error!\n\nThe site isn't returning the upload status.\n"
                                               "This is a critical error from the site.\n"
                                               f"Status code:{str(upload_job.status_code)}")
            else:  # if it returns any other status code, raise a pythonic error to be shown and print unknown error
                upload_status_info.insert(END, 'Unknown error!')
                upload_job.raise_for_status()
            upload_status_info.config(state=DISABLED)  # disable scrolled textbox

        # start upload in a thread
        threading.Thread(target=run_upload_in_different_thread).start()

    # enabled upload img
    decode_resize_tmdb_image = Image.open(BytesIO(base64.b64decode(bhd_upload_icon))).resize((120, 45))
    upload_img = ImageTk.PhotoImage(decode_resize_tmdb_image)

    # disabled upload img
    decode_resize_tmdb_image2 = Image.open(BytesIO(base64.b64decode(bhd_upload_icon_disabled))).resize((120, 45))
    upload_img_disabled = ImageTk.PhotoImage(decode_resize_tmdb_image2)

    upload_button = HoverButton(upload_window, text="Upload", image=upload_img_disabled,
                                background="#363636", borderwidth=0, activebackground="#363636",
                                cursor='question_arrow')
    upload_button.grid(row=5, column=3, padx=(5, 10), pady=(5, 10), sticky=E + S)
    upload_button.image = upload_img_disabled

    # function to define and display missing inputs
    def show_missing_input():
        missing_list = []  # create empty missing list
        if torrent_file_path.get() == '':
            missing_list.append('Torrent Input')
        if title_input_entry_box.get().strip() == '':
            missing_list.append('Title')
        if type_var.get() == '':
            missing_list.append('Type')
        if source_var.get() == '':
            missing_list.append('Source')
        if imdb_id_var.get().strip() == '':
            missing_list.append('IMDB ID')
        if tmdb_id_var.get().strip() == '':
            missing_list.append('TMDB ID')
        if encode_media_info.get() == '':
            missing_list.append('MediaInfo')
        if nfo_info_var.get() == '':
            missing_list.append('NFO/Description')

        # open messagebox with all the missing inputs
        messagebox.showinfo(parent=upload_window, title='Missing Input',
                            message=f"Missing inputs:\n\n{', '.join(missing_list)}")

    # function to check for missing variables and enable/change button and button commands
    def enable_disable_upload_button():
        # if everything is needed in the window, enable upload button
        if torrent_file_path.get() != '' and title_input_entry_box.get().strip() != '' and type_var.get() != '' and \
                source_var.get() != '' and imdb_id_var.get().strip() != '' and tmdb_id_var.get().strip() != '' and \
                encode_media_info.get() != '' and nfo_info_var.get() != '':
            upload_button.config(image=upload_img)
            upload_button.image = upload_img
            upload_button.config(command=upload_to_api, cursor='hand2')
        else:  # if 1 item is missing, disable upload button and enable show missing input function
            upload_button.config(image=upload_img_disabled)
            upload_button.image = upload_img_disabled
            upload_button.config(command=show_missing_input, cursor='question_arrow')
        upload_window.after(50, enable_disable_upload_button)  # loop to check this constantly

    # start loop
    enable_disable_upload_button()


# open torrent window button
open_uploader_button = HoverButton(manual_workflow, text="Uploader", state=DISABLED,
                                   command=lambda: [automatic_workflow_boolean.set(False),
                                                    open_uploader_window('manual')],
                                   foreground="white", background="#23272A", borderwidth="3", width=12,
                                   activeforeground="#3498db", activebackground="#23272A")
open_uploader_button.grid(row=0, column=2, columnspan=1, padx=(5, 10), pady=1, sticky=E + W)


# automatic work flow button
def auto_workflow():
    # check screens
    check_screens = parse_screen_shots()
    if not check_screens:  # if returned false, show error message and exit this function
        messagebox.showerror(parent=root, title='Error!', message='Missing or incorrectly formatted screenshots\n\n'
                                                                  'Screen shots need to be in multiples of 2')
        return
    torrent_function_window()  # if passed run torrent function
    if not automatic_workflow_boolean.get():  # if returned false, exit this function back to main GUI
        return
    open_nfo_viewer()  # if passed run nfo viewer function
    if not automatic_workflow_boolean.get():  # if returned false, exit this function back to main GUI
        return
    open_uploader_window('auto')  # if it passes all the automatic requirements, open upload window in 'auto' mode


# parse and upload button
parse_and_upload = HoverButton(automatic_workflow, text="Parse & Upload", state=DISABLED,
                               command=lambda: [automatic_workflow_boolean.set(True), auto_workflow()],
                               foreground="white", background="#23272A", borderwidth="3",
                               activeforeground="#3498db", width=1, activebackground="#23272A")
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
    screenshot_scrolledtext.delete("1.0", END)
    clear_all_variables()


# ----------------------------------------------------------------------------------------------------------- reset gui

# reset config --------------------------------------------------------------------------------------------------------
def reset_config():
    ask_reset_config = messagebox.askyesno(title='Prompt', message='Are you sure you want to reset the config file?\n'
                                                                   'Note: This will remove all saved settings')
    if ask_reset_config:
        try:
            pathlib.Path(config_file).unlink()
            messagebox.showinfo(title='Prompt', message='Config is reset, please restart the program')
        except FileNotFoundError:
            messagebox.showerror(title='Error!', message='Config is already deleted, please restart the program')
        root.destroy()


# --------------------------------------------------------------------------------------------------------- reset config

# menu Items and Sub-Bars ---------------------------------------------------------------------------------------------
my_menu_bar = Menu(root, tearoff=0)
root.config(menu=my_menu_bar)

file_menu = Menu(my_menu_bar, tearoff=0, activebackground='dim grey')
my_menu_bar.add_cascade(label='File', menu=file_menu)

file_menu.add_command(label='Open Source File   [CTRL + O]', command=manual_source_input)
root.bind("<Control-s>", lambda event: manual_source_input())
file_menu.add_command(label='Open Encode File   [CTRL + E]', command=manual_encode_input)
root.bind("<Control-e>", lambda event: manual_encode_input())
file_menu.add_separator()
file_menu.add_command(label='Reset GUI              [CTRL + R]', command=reset_gui)
root.bind("<Control-r>", lambda event: reset_gui())
file_menu.add_command(label='Exit                        [ALT + F4]', command=root_exit_function)


# custom input box that accepts parent window, label, config option, and config key
def custom_input_prompt(parent_window, label_input, config_option, config_key):
    # set parser
    custom_input_parser = ConfigParser()
    custom_input_parser.read(config_file)

    def custom_input_window_exit():
        encoder_okay_func()

    # encoder name window
    custom_input_window = Toplevel()
    custom_input_window.title('')
    custom_input_window.configure(background="#363636")
    custom_input_window.geometry(f'{260}x{140}+{str(int(parent_window.geometry().split("+")[1]) + 220)}+'
                                 f'{str(int(parent_window.geometry().split("+")[2]) + 230)}')
    custom_input_window.resizable(0, 0)
    custom_input_window.grab_set()
    custom_input_window.protocol('WM_DELETE_WINDOW', custom_input_window_exit)
    parent_window.wm_attributes('-alpha', 0.90)  # set parent window to be slightly transparent
    custom_input_window.grid_rowconfigure(0, weight=1)
    custom_input_window.grid_columnconfigure(0, weight=1)

    # encoder name frame
    custom_input_frame = Frame(custom_input_window, highlightbackground="white", highlightthickness=2, bg="#363636",
                               highlightcolor='white')
    custom_input_frame.grid(column=0, row=0, columnspan=3, sticky=N + S + E + W)
    for e_n_f in range(3):
        custom_input_frame.grid_columnconfigure(e_n_f, weight=1)
        custom_input_frame.grid_rowconfigure(e_n_f, weight=1)

    # create label
    custom_label = Label(custom_input_frame, text=label_input, background='#363636', fg="#3498db",
                         font=(set_font, set_font_size, "bold"))
    custom_label.grid(row=0, column=0, columnspan=3, sticky=W + N, padx=5, pady=(2, 0))

    # create entry box
    custom_entry_box = Entry(custom_input_frame, borderwidth=4, bg="#565656", fg='white')
    custom_entry_box.grid(row=1, column=0, columnspan=3, padx=10, pady=(0, 5), sticky=E + W)
    custom_entry_box.insert(END, custom_input_parser[config_option][config_key])

    # function to save new name to config.ini
    def encoder_okay_func():
        if custom_input_parser[config_option][config_key] != custom_entry_box.get().strip():
            custom_input_parser.set(config_option, config_key, custom_entry_box.get().strip())
            with open(config_file, 'w') as encoder_name_config_file:
                custom_input_parser.write(encoder_name_config_file)
        parent_window.wm_attributes('-alpha', 1.0)  # restore transparency
        custom_input_window.destroy()  # close window

    # create 'OK' button
    encoder_okay_btn = HoverButton(custom_input_frame, text="OK", command=encoder_okay_func, foreground="white",
                                   background="#23272A", borderwidth="3", activeforeground="#3498db", width=8,
                                   activebackground="#23272A")
    encoder_okay_btn.grid(row=2, column=0, columnspan=1, padx=7, pady=5, sticky=S + W)

    # create 'Cancel' button
    encoder_cancel_btn = HoverButton(custom_input_frame, text="Cancel", activeforeground="#3498db", width=8,
                                     command=lambda: [custom_input_window.destroy(),
                                                      root.wm_attributes('-alpha', 1.0)],
                                     foreground="white", background="#23272A", borderwidth="3",
                                     activebackground="#23272A")
    encoder_cancel_btn.grid(row=2, column=2, columnspan=1, padx=7, pady=5, sticky=S + E)

    custom_input_window.wait_window()


# # custom messagebox window that accepts parent window and text info
# def custom_input_prompt(parent_window, text_input):
#     # encoder name window
#     custom_input_window = Toplevel()
#     custom_input_window.configure(background="#363636")
#     custom_input_window.geometry(f'{460}x{200}+{str(int(parent_window.geometry().split("+")[1]) + 156)}+'
#                                  f'{str(int(parent_window.geometry().split("+")[2]) + 230)}')
#     custom_input_window.resizable(0, 0)
#     custom_input_window.grab_set()
#     custom_input_window.wm_overrideredirect(True)
#     parent_window.wm_attributes('-alpha', 0.90)  # set parent window to be slightly transparent
#     custom_input_window.grid_rowconfigure(0, weight=1)
#     custom_input_window.grid_columnconfigure(0, weight=1)
#
#     # encoder name frame
#     custom_input_frame = Frame(custom_input_window, highlightbackground="white", highlightthickness=2, bg="#363636",
#                                highlightcolor='white')
#     custom_input_frame.grid(column=0, row=0, columnspan=3, sticky=N + S + E + W)
#     for e_n_f in range(3):
#         custom_input_frame.grid_columnconfigure(e_n_f, weight=1)
#         custom_input_frame.grid_rowconfigure(e_n_f, weight=1)
#
#     # create label
#     custom_info_scrolled = scrolledtextwidget.ScrolledText(custom_input_frame, height=7, bg='#565656', fg='white',
#                                                            bd=4)
#     custom_info_scrolled.grid(row=0, column=0, columnspan=3, pady=(2, 0), padx=5, sticky=E + W)
#     custom_info_scrolled.insert(END, text_input)
#     custom_info_scrolled.config(state=DISABLED)
#
#     # function to save new name to config.ini
#     def encoder_okay_func():
#         parent_window.wm_attributes('-alpha', 1.0)  # restore transparency
#         custom_input_window.destroy()  # close window
#
#     # create 'OK' button
#     encoder_okay_btn = HoverButton(custom_input_frame, text="OK", command=encoder_okay_func, foreground="white",
#                                    background="#23272A", borderwidth="3", activeforeground="#3498db", width=8,
#                                    activebackground="#23272A")
#     encoder_okay_btn.grid(row=2, column=2, columnspan=1, padx=7, pady=5, sticky=E)
#
#     custom_input_window.wait_window()


options_menu = Menu(my_menu_bar, tearoff=0, activebackground='dim grey')
my_menu_bar.add_cascade(label='Options', menu=options_menu)
options_menu.add_command(label='Encoder Name',
                         command=lambda: [custom_input_prompt(root, 'Encoder Name:', 'encoder_name', 'name')])
options_menu.add_command(label='API Key',
                         command=lambda: [custom_input_prompt(root, 'BHD Upload Key:', 'bhd_upload_api', 'key')])
options_menu.add_separator()
options_menu.add_command(label='Reset Configuration File', command=reset_config)

tools_menu = Menu(my_menu_bar, tearoff=0, activebackground='dim grey')
my_menu_bar.add_cascade(label='Tools', menu=tools_menu)
tools_menu.add_command(label='Manual Uploader', accelerator="[Ctrl+U]",
                       command=lambda: open_uploader_window('custom_advanced'))
root.bind("<Control-u>", lambda event: open_uploader_window('custom_advanced'))

help_menu = Menu(my_menu_bar, tearoff=0, activebackground="dim grey")
my_menu_bar.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="Documentation                 [F1]",  # Open GitHub wiki
                      command=lambda: webbrowser.open('https://github.com/jlw4049/BHDStudio-Upload-Tool/wiki'))
root.bind("<F1>", lambda event: webbrowser.open('https://github.com/jlw4049/BHDStudio-Upload-Tool/wiki'))  # hotkey
help_menu.add_command(label="Project Page",  # Open GitHub project page
                      command=lambda: webbrowser.open('https://github.com/jlw4049/BHDStudio-Upload-Tool'))
help_menu.add_command(label="Report Error / Feature Request",  # Open GitHub tracker link
                      command=lambda: webbrowser.open('https://github.com/jlw4049/BHDStudio-Upload-Tool'
                                                      '/issues/new/choose'))
help_menu.add_separator()
help_menu.add_command(label="Info", command=lambda: openaboutwindow(main_root_title))  # Opens about window


# function to enable/disable main GUI buttons
def generate_button_checker():
    if source_file_path.get() != '' and encode_file_path.get() != '':  # if source/encode is not empty strings
        generate_nfo_button.config(state=NORMAL)
        open_torrent_window_button.config(state=NORMAL)
        check_screens = parse_screen_shots()
        if check_screens:
            parse_and_upload.config(state=NORMAL)
            if nfo_info_var.get() != '':
                open_uploader_button.config(state=NORMAL)
    else:  # if source/encode is empty stringsN
        generate_nfo_button.config(state=DISABLED)
        open_torrent_window_button.config(state=DISABLED)
        parse_and_upload.config(state=DISABLED)
        open_uploader_button.config(state=DISABLED)
    root.after(50, generate_button_checker)  # loop to constantly check


generate_button_checker()

root.mainloop()
