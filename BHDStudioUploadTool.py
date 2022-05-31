from TkinterDnD2 import *
from tkinter import filedialog, StringVar, ttk, messagebox, PhotoImage, Menu, NORMAL, DISABLED, N, S, W, E, Toplevel, \
    LabelFrame, END, INSERT, Label, Checkbutton, Spinbox, CENTER, GROOVE, OptionMenu, Entry, HORIZONTAL, SUNKEN, \
    Button, TclError, font, Frame, Scrollbar, VERTICAL, Listbox, EXTENDED
import pathlib
import tkinter.scrolledtext as scrolledtextwidget
import webbrowser
from pymediainfo import MediaInfo
from torf import Torrent

root = TkinterDnD.Tk()
root.title('BHDStudio Upload Tool')
# root.iconphoto(True, PhotoImage(data=gui_icon))
root.configure(background="#363636")
# if config['save_window_locations']['ffmpeg audio encoder position'] == '' or \
#         config['save_window_locations']['ffmpeg audio encoder'] == 'no':
window_height = 720
window_width = 720
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_coordinate = int((screen_width / 2) - (window_width / 2))
y_coordinate = int((screen_height / 2) - (window_height / 2))
root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")
# elif config['save_window_locations']['ffmpeg audio encoder position'] != '' and \
#         config['save_window_locations']['ffmpeg audio encoder'] == 'yes':
#     root.geometry(config['save_window_locations']['ffmpeg audio encoder position'])\

# root.protocol('WM_DELETE_WINDOW', root_exit_function)
# root_pid = os.getpid()  # Get root process ID

for n in range(4):
    root.grid_columnconfigure(n, weight=1)
for n in range(5):
    root.grid_rowconfigure(n, weight=1)

class HoverButton(Button):
    def __init__(self, master, **kw):
        Button.__init__(self, master=master,**kw)
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
# custom_style = ttk.Style()
# custom_style.theme_create('jlw_style', parent='alt', settings={
#     # Notebook Theme Settings -------------------
#     "TNotebook": {"configure": {"tabmargins": [5, 5, 5, 0], 'background': "#565656"}},
#     "TNotebook.Tab": {
#         "configure": {"padding": [5, 1], "background": 'grey', 'foreground': 'white', 'focuscolor': ''},
#         "map": {"background": [("selected", '#434547')], "expand": [("selected", [1, 1, 1, 0])]}},
#     # Notebook Theme Settings -------------------
#     # ComboBox Theme Settings -------------------
#     'TCombobox': {'configure': {'selectbackground': '#23272A', 'fieldbackground': '#23272A',
#                                 'background': 'white', 'foreground': 'white'}}}
#                           # ComboBox Theme Settings -------------------
#                           )
# custom_style.theme_use('jlw_style')  # Enable the use of the custom theme

# ------------------------------------------ Custom Tkinter Theme

# nfo_frame = LabelFrame(root, text=' NFO ', labelanchor="nw")
# nfo_frame.grid(column=0, row=2, columnspan=4, padx=5, pady=(5, 3), sticky=E + W)
# nfo_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 10))
# nfo_frame.grid_rowconfigure(0, weight=1)
# nfo_frame.grid_columnconfigure(0, weight=20)
# nfo_frame.grid_columnconfigure(1, weight=20)
# nfo_frame.grid_columnconfigure(2, weight=20)
# nfo_frame.grid_columnconfigure(3, weight=1)

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

    if widget_source == 'Encode':

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
        if 'HDR10' in str(video_track.hdr_format_compatibility):
            release_notes_scrolled.insert(END, '\n-HDR10 compatible')
            release_notes_scrolled.insert(END, '\n-Screenshots tone mapped for comparison')
        release_notes_scrolled.config(state=DISABLED)

        enable_clear_all_checkbuttons()

    entry_box_selection.config(state=NORMAL)
    entry_box_selection.delete(0, END)
    entry_box_selection.insert(END, pathlib.Path(file_input).name)
    entry_box_selection.config(state=DISABLED)

# source --------------------------------------------------------------------------------------------------------------
source_frame = LabelFrame(root, text=' Source ', labelanchor="nw")
source_frame.grid(column=0, row=0, columnspan=4, padx=5, pady=(5, 3), sticky=E + W)
source_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 10))
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

reset_source_input = HoverButton(source_frame, text="X", command=delete_source_entry, foreground="white",
                                 background="#23272A", borderwidth="3", activebackground='grey')
reset_source_input.grid(row=0, column=3, columnspan=1, padx=5, pady=(7, 0), sticky=N + S + E + W)


# encode --------------------------------------------------------------------------------------------------------------
encode_frame = LabelFrame(root, text=' Encode ', labelanchor="nw")
encode_frame.grid(column=0, row=1, columnspan=4, padx=5, pady=(5, 3), sticky=E + W)
encode_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 10))
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

reset_encode_input = HoverButton(encode_frame, text="X", command=delete_encode_entry, foreground="white",
                                 background="#23272A", borderwidth="3", activebackground='grey')
reset_encode_input.grid(row=0, column=3, columnspan=1, padx=5, pady=5, sticky=N + S + E + W)


# release notes -------------------------------------------------------------------------------------------------------
release_notes_frame = LabelFrame(root, text=' Release Notes ', labelanchor="nw")
release_notes_frame.grid(column=0, row=2, columnspan=4, padx=5, pady=(5, 3), sticky=E + W)
release_notes_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 10))

for rl_row in range(3):
    release_notes_frame.grid_rowconfigure(rl_row, weight=0)
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
forced_subtitles_burned.grid(row=0, column=0, columnspan=1, rowspan=1, padx=5, pady=5, sticky=S + E + W + N)
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
balance_borders.grid(row=0, column=1, columnspan=1, rowspan=1, padx=5, pady=5, sticky=S + E + W + N)
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
fill_borders.grid(row=0, column=2, columnspan=1, rowspan=1, padx=5, pady=5, sticky=S + E + W + N)
fill_borders_var.set('off')

release_notes_scrolled = scrolledtextwidget.ScrolledText(release_notes_frame, height=6, bg="#565656", bd=8, fg='white')
release_notes_scrolled.grid(row=1, column=0, columnspan=4, pady=5, padx=5, sticky=E + W + N + S)
release_notes_scrolled.config(state=DISABLED)

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
screenshot_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 10))
screenshot_frame.grid_rowconfigure(0, weight=1)
screenshot_frame.grid_columnconfigure(0, weight=20)
screenshot_frame.grid_columnconfigure(1, weight=20)
screenshot_frame.grid_columnconfigure(2, weight=20)
screenshot_frame.grid_columnconfigure(3, weight=1)


def test():
    if screenshot_scrolledtext.compare("end-1c", "!=", "1.0"):  # if screenshot textbox is not empty
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

            screenshot_scrolledtext.delete('1.0', END)
            screenshot_scrolledtext.insert(END, 'Screenshots successfully parsed!')
        else:
            screenshot_scrolledtext.delete('1.0', END)
            screenshot_scrolledtext.insert(END, 'Error, screenshots cannot be parsed!\nYou '
                                                'must add an even number of screenshots...')


screenshot_scrolledtext = scrolledtextwidget.ScrolledText(screenshot_frame, height=4, bg='#565656', fg='white', bd=8)
screenshot_scrolledtext.grid(row=0, column=0, columnspan=3, pady=(0, 6), padx=10, sticky=E + W)


add_screenshots = HoverButton(screenshot_frame, text=">", command=test, foreground="white",
                                 background="#23272A", borderwidth="3", activebackground='grey', width=4)
add_screenshots.grid(row=0, column=3, columnspan=1, padx=5, pady=5, sticky=N + E + W)

def delete_source_entry():
    screenshot_scrolledtext.delete(1.0, END)

reset_screenshot_box = HoverButton(screenshot_frame, text="X", command=delete_source_entry, foreground="white",
                                 background="#23272A", borderwidth="3", activebackground='grey', width=4)
reset_screenshot_box.grid(row=0, column=3, columnspan=1, padx=5, pady=5, sticky=S + E + W)



# torrent creation
torrent_frame = LabelFrame(root, text=' Create Torrent ', labelanchor="nw")
torrent_frame.grid(column=0, row=4, columnspan=4, padx=5, pady=(5, 3), sticky=E + W)
torrent_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 10))

for rl_row in range(3):
    torrent_frame.grid_rowconfigure(rl_row, weight=0)
for rl_f in range(3):
    torrent_frame.grid_columnconfigure(rl_f, weight=1)



# t = Torrent(path='path/to/content',
#             trackers=['https://tracker1.example.org:1234/announce',
#                       'https://tracker2.example.org:5678/announce'],
#             comment='This is a comment')
# t.private = True
# t.generate()
# t.write('my.torrent')



root.mainloop()