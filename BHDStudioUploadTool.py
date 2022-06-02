import math
import os
import pathlib
import threading
import tkinter.scrolledtext as scrolledtextwidget
from configparser import ConfigParser
from ctypes import windll
from idlelib.tooltip import Hovertip
from tkinter import filedialog, StringVar, ttk, messagebox, NORMAL, DISABLED, N, S, W, E, Toplevel, \
    LabelFrame, END, Label, Checkbutton, OptionMenu, Entry, HORIZONTAL, SUNKEN, \
    Button, TclError, font, Menu

import torf
from TkinterDnD2 import *
from pymediainfo import MediaInfo
from torf import Torrent

# create runtime folder if it does not exist
pathlib.Path(pathlib.Path.cwd() / 'Runtime').mkdir(parents=True, exist_ok=True)

# define config file and settings
config_file = 'Runtime/config.ini'  # Creates (if doesn't exist) and defines location of config.ini
config = ConfigParser()
config.read(config_file)
if not config.has_section('torrent_settings'):
    config.add_section('torrent_settings')
if not config.has_option('torrent_settings', 'tracker_url'):
    config.set('torrent_settings', 'tracker_url', '')
with open(config_file, 'w') as configfile:
    config.write(configfile)

# root
root = TkinterDnD.Tk()
root.title('BHDStudio Upload Tool')
# root.iconphoto(True, PhotoImage(data=gui_icon))
root.configure(background="#363636")
# if config['save_window_locations']['ffmpeg audio encoder position'] == '' or \
#         config['save_window_locations']['ffmpeg audio encoder'] == 'no':
root_window_height = 650
root_window_width = 720
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_coordinate = int((screen_width / 2) - (root_window_width / 2))
y_coordinate = int((screen_height / 2) - (root_window_height / 2))
root.geometry(f"{root_window_width}x{root_window_height}+{x_coordinate}+{y_coordinate}")
# elif config['save_window_locations']['ffmpeg audio encoder position'] != '' and \
#         config['save_window_locations']['ffmpeg audio encoder'] == 'yes':
#     root.geometry(config['save_window_locations']['ffmpeg audio encoder position'])\

# root.protocol('WM_DELETE_WINDOW', root_exit_function)
# root_pid = os.getpid()  # Get root process ID

# Block of code to fix DPI awareness issues on Windows 7 or higher
try:
    windll.shcore.SetProcessDpiAwareness(2)  # if your Windows version >= 8.1
except(Exception,):
    windll.user32.SetProcessDPIAware()  # Windows 8.0 or less
# Block of code to fix DPI awareness issues on Windows 7 or higher

for n in range(4):
    root.grid_columnconfigure(n, weight=1)
for n in range(6):
    root.grid_rowconfigure(n, weight=1)


class HoverButton(Button):
    def __init__(self, master, **kw):
        Button.__init__(self, master=master, **kw)
        self.defaultBackground = self["background"]
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self['background'] = self['activebackground']

    def on_leave(self, e):
        self['background'] = self.defaultBackground


detect_font = font.nametofont("TkDefaultFont")  # Get default font value into Font object
set_font = detect_font.actual().get("family")
set_font_size = detect_font.actual().get("size")
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

# nfo_frame = LabelFrame(root, text=' NFO ', labelanchor="nw")
# nfo_frame.grid(column=0, row=2, columnspan=4, padx=5, pady=(5, 3), sticky=E + W)
# nfo_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 10))
# nfo_frame.grid_rowconfigure(0, weight=1)
# nfo_frame.grid_columnconfigure(0, weight=20)
# nfo_frame.grid_columnconfigure(1, weight=20)
# nfo_frame.grid_columnconfigure(2, weight=20)
# nfo_frame.grid_columnconfigure(3, weight=1)
source_file_path = StringVar()
encode_file_path = StringVar()
torrent_file_path = StringVar()


def drop_function(event):
    file_input = [x for x in root.splitlist(event.data)][0]
    widget_source = str(event.widget.cget('text')).strip()

    if widget_source == 'Source':

        media_info = MediaInfo.parse(pathlib.Path(file_input))
        video_track = media_info.video_tracks[0]
        update_source_label = f"Format:  {str(video_track.format)}   |   " \
                              f"Resolution:  {str(video_track.width)}x{str(video_track.height)}   |   " \
                              f"Frame rate:  {str(video_track.frame_rate)}   |   " \
                              f"Stream size:  {str(video_track.other_stream_size[3])}"
        hdr_string = ''
        if video_track.other_hdr_format:
            hdr_string = f"HDR format:  {str(video_track.hdr_format)} / {str(video_track.hdr_format_compatibility)}"
        elif not video_track.other_hdr_format:
            hdr_string = ''

        entry_box_selection = source_entry_box
        source_label.config(text=update_source_label)
        source_hdr_label.config(text=hdr_string)
        source_file_path.set(pathlib.Path(file_input))

    elif widget_source == 'Encode':

        media_info = MediaInfo.parse(pathlib.Path(file_input))
        video_track = media_info.video_tracks[0]
        if not media_info.general_tracks[0].count_of_audio_streams:
            messagebox.showerror(parent=root, title='Error', message='Audio track is missing from encoded file')
            delete_encode_entry()
            return
        audio_track = media_info.audio_tracks[0]
        if audio_track.channel_s == 1:
            audio_channels_string = '1.0'
        elif audio_track.channel_s == 2:
            audio_channels_string = '2.0'
        elif audio_track.channel_s == 6:
            audio_channels_string = '5.1'
        else:
            messagebox.showerror(parent=root, title='Error', message='Incorrect audio track format')
            return
        update_source_label = f"Format:  {str(video_track.format)}   |   " \
                              f"Resolution:  {str(video_track.width)}x{str(video_track.height)}   |   " \
                              f"Frame rate:  {str(video_track.frame_rate)}   |   " \
                              f"Audio:  {str(audio_track.format)}  /  {audio_channels_string}  /  " \
                              f"{str(audio_track.other_bit_rate[0])}"
        hdr_string = ''
        if video_track.other_hdr_format:
            hdr_string = f"HDR format:  {str(video_track.hdr_format)} / {str(video_track.hdr_format_compatibility)}"
        elif not video_track.other_hdr_format:
            hdr_string = ''

        entry_box_selection = encode_entry_box
        encode_label.config(text=update_source_label)
        encode_hdr_label.config(text=hdr_string)
        encode_file_path.set(pathlib.Path(file_input))

        # detect resolution
        encode_resolution = ''
        # if video_track.width <= 1280 and video_track.height <= 720:
        #     encode_resolution = '720p'
        # elif video_track.width <= 1920 and video_track.height <= 1080:
        #     encode_resolution = '1080p'
        # elif video_track.width <= 3840 and video_track.height <= 2160:
        #     encode_resolution = '2160p'

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

        # enable torrent button
        torrent_file_path.set(pathlib.Path(file_input).with_suffix('.torrent'))
        open_torrent_window_button.config(state=NORMAL)

    entry_box_selection.config(state=NORMAL)
    entry_box_selection.delete(0, END)
    entry_box_selection.insert(END, pathlib.Path(file_input).name)
    entry_box_selection.config(state=DISABLED)


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
        source_entry_box.delete(0, END)
        source_entry_box.insert(END, pathlib.Path(source_file_input).name)


source_button = HoverButton(source_frame, text="Open", command=manual_source_input, foreground="white",
                            background="#23272A", borderwidth="3", activebackground='grey')
source_button.grid(row=0, column=0, columnspan=1, padx=5, pady=(7, 0), sticky=N + S + E + W)

source_entry_box = Entry(source_frame, borderwidth=4, bg="#565656", fg='white', state=DISABLED,
                         disabledforeground='white', disabledbackground="#565656")
source_entry_box.grid(row=0, column=1, columnspan=2, padx=5, pady=(5, 0), sticky=N + S + E + W)

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


reset_source_input = HoverButton(source_frame, text="X", command=delete_source_entry, foreground="white",
                                 background="#23272A", borderwidth="3", activebackground='grey')
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
    encode_file_input = filedialog.askopenfilename(parent=root, title='Select Source', initialdir='/',
                                                   filetypes=[("Media Files", "*.*")])
    if encode_file_input:
        encode_entry_box.delete(0, END)
        encode_entry_box.insert(END, pathlib.Path(encode_file_input).name)


encode_button = HoverButton(encode_frame, text="Open", command=manual_encode_input, foreground="white",
                            background="#23272A", borderwidth="3", activebackground='grey')
encode_button.grid(row=0, column=0, columnspan=1, padx=5, pady=5, sticky=N + S + E + W)

encode_entry_box = Entry(encode_frame, borderwidth=4, bg="#565656", fg='white', state=DISABLED,
                         disabledforeground='white', disabledbackground="#565656")
encode_entry_box.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky=N + S + E + W)

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


reset_encode_input = HoverButton(encode_frame, text="X", command=delete_encode_entry, foreground="white",
                                 background="#23272A", borderwidth="3", activebackground='grey')
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
        release_notes_scrolled.insert(END, '\n-Forced English subtitle embedded for non English dialogue')
    elif forced_subtitles_burned_var.get() == 'off':
        delete_forced = release_notes_scrolled.search(
            "-Forced English subtitle embedded for non English dialogue", '1.0', END)
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
reset_screenshot_box = HoverButton(screenshot_frame, text="X",
                                   command=lambda: screenshot_scrolledtext.delete('1.0', END), foreground="white",
                                   background="#23272A", borderwidth="3", activebackground='grey', width=4)
reset_screenshot_box.grid(row=0, column=3, columnspan=1, padx=5, pady=5, sticky=N + E + W)


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

            screenshot_scrolledtext.delete('1.0', END)  # DELETE
            screenshot_scrolledtext.insert(END, 'Screenshots successfully parsed!')
            return sorted_screenshots
        else:
            screenshot_scrolledtext.delete('1.0', END)  # SHOW ERROR BOX MESSAGE
            screenshot_scrolledtext.insert(END, 'Error, screenshots cannot be parsed!\nYou '
                                                'must add an even number of screenshots...')


# add_screenshots = HoverButton(screenshot_frame, text="Check", command=parse_screen_shots, foreground="white",
#                               background="#23272A", borderwidth="3", activebackground='grey', width=6)
# add_screenshots.grid(row=0, column=3, columnspan=1, padx=5, pady=5, sticky=S + E + W)


# generate nfo
def open_nfo_viewer():  # !!WORK IN PROGRESS!!
    if not pathlib.Path(source_file_path.get()).is_file():
        messagebox.showerror(parent=root, title='Error!', message='Source file is missing!')
        return
    if not pathlib.Path(encode_file_path.get()).is_file():
        messagebox.showerror(parent=root, title='Error!', message='Encode file is missing!')
        return
    parse_screenshots = parse_screen_shots()
    if not parse_screenshots:
        messagebox.showerror(parent=root, title='Error!', message='You must add screenshots before generating nfo')
    print(parse_screenshots)


generate_nfo_button = HoverButton(root, text="Generate NFO", command=open_nfo_viewer, foreground="white",
                                  background="#23272A", borderwidth="3", activebackground='grey', width=1)
generate_nfo_button.grid(row=4, column=3, columnspan=1, padx=10, pady=(3, 0), sticky=E + W)


def generate_button_checker():
    if source_file_path.get() != '' and encode_file_path.get() != '':
        generate_nfo_button.config(state=NORMAL)
    else:
        generate_nfo_button.config(state=DISABLED)
    root.after(50, generate_button_checker)


generate_button_checker()


# torrent creation ----------------------------------------------------------------------------------------------------
def torrent_function_window():
    # torrent window exit function
    def torrent_window_exit_function():
        if '/announce' in torrent_tracker_url_entry_box.get().strip():
            torrent_parser = ConfigParser()
            torrent_parser.read(config_file)
            torrent_parser.set('torrent_settings', 'tracker_url', torrent_tracker_url_entry_box.get().strip())
            with open(config_file, 'w') as configfile:
                torrent_parser.write(configfile)
        torrent_window.destroy()  # destroy torrent window
        open_all_toplevels()  # open all top levels that was open
        advanced_root_deiconify()  # re-open root

    hide_all_toplevels()  # hide all top levels
    root.withdraw()  # hide root

    # create new toplevel window
    torrent_window = Toplevel()
    torrent_window.configure(background="#363636")  # Set color of torrent_window background
    torrent_window.title('Torrent Creator')
    window_height = 330  # win height
    window_width = 520  # win width
    # open near the center of root
    torrent_window.geometry(f'{window_width}x{window_height}+'
                            f'{str(int(root.geometry().split("+")[1]) + 100)}+'
                            f'{str(int(root.geometry().split("+")[2]) + 210)}')
    # torrent_window.resizable(0, 0)  # makes window not resizable
    torrent_window.protocol('WM_DELETE_WINDOW', torrent_window_exit_function)

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
                                 background="#23272A", borderwidth="3", activebackground='grey')
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
            check_overwrite = messagebox.askyesno(parent=root, title='File Already Exists',
                                                  message=f'"{pathlib.Path(torrent_file_path.get()).name}"\n\n'
                                                          f'File already exists.\n\nWould you like to overwrite the '
                                                          f'file?')
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
    create_torrent_button = HoverButton(torrent_window, text="Create",
                                        command=lambda: threading.Thread(target=create_torrent).start(),
                                        foreground="white", background="#23272A", borderwidth="3",
                                        activebackground='grey', width=12)
    create_torrent_button.grid(row=4, column=9, columnspan=1, padx=5, pady=(5, 0), sticky=E + S + N)

    # cancel torrent button
    cancel_torrent_button = HoverButton(torrent_window, text="Cancel", command=torrent_window_exit_function,
                                        foreground="white", background="#23272A", borderwidth="3",
                                        activebackground='grey', width=12)
    cancel_torrent_button.grid(row=4, column=0, columnspan=1, padx=5, pady=(5, 0), sticky=W + S + N)


# open torrent window button
open_torrent_window_button = HoverButton(root, text="Create Torrent", command=torrent_function_window,
                                         foreground="white", background="#23272A", borderwidth="3",
                                         activebackground='grey', width=1, state=DISABLED)
open_torrent_window_button.grid(row=4, column=0, columnspan=1, padx=10, pady=(3, 0), sticky=E + W)


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


root.mainloop()
