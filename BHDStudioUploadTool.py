from TkinterDnD2 import *
from tkinter import filedialog, StringVar, ttk, messagebox, PhotoImage, Menu, NORMAL, DISABLED, N, S, W, E, Toplevel, \
    LabelFrame, END, INSERT, Label, Checkbutton, Spinbox, CENTER, GROOVE, OptionMenu, Entry, HORIZONTAL, SUNKEN, \
    Button, TclError, font, Frame, Scrollbar, VERTICAL, Listbox, EXTENDED
import pathlib
import tkinter.scrolledtext as scrolledtextwidget
import webbrowser

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
for n in range(4):
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
color1 = "#434547"

def drop_function(event):
    file_input = [x for x in root.splitlist(event.data)][0]
    widget_source = str(event.widget.cget('text')).strip()

    if widget_source == 'Source':
        entry_box_selection = source_entry_box
    if widget_source == 'Encode':
        entry_box_selection = encode_entry_box

    entry_box_selection.config(state=NORMAL)
    entry_box_selection.delete(0, END)
    entry_box_selection.insert(END, pathlib.Path(file_input).name)
    entry_box_selection.config(state=DISABLED)

# source --------------------------------------------------------------------------------------------------------------
source_frame = LabelFrame(root, text=' Source ', labelanchor="nw")
source_frame.grid(column=0, row=0, columnspan=4, padx=5, pady=(5, 3), sticky=E + W)
source_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 10))
source_frame.grid_rowconfigure(0, weight=1)
source_frame.grid_columnconfigure(0, weight=2)
source_frame.grid_columnconfigure(1, weight=20)
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
source_button.grid(row=0, column=0, columnspan=1, padx=5, pady=5, sticky=N + S + E + W)

source_entry_box = Entry(source_frame, borderwidth=4, bg="#565656", fg='white', state=DISABLED,
                         disabledforeground='white', disabledbackground="#565656")
source_entry_box.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky=N + S + E + W)

def delete_source_entry():
    source_entry_box.config(state=NORMAL)
    source_entry_box.delete(0, END)
    source_entry_box.config(state=DISABLED)

reset_source_input = HoverButton(source_frame, text="X", command=delete_source_entry, foreground="white",
                                 background="#23272A", borderwidth="3", activebackground='grey')
reset_source_input.grid(row=0, column=3, columnspan=1, padx=5, pady=5, sticky=N + S + E + W)


# encode --------------------------------------------------------------------------------------------------------------
encode_frame = LabelFrame(root, text=' Encode ', labelanchor="nw")
encode_frame.grid(column=0, row=1, columnspan=4, padx=5, pady=(5, 3), sticky=E + W)
encode_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 10))
encode_frame.grid_rowconfigure(0, weight=1)
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

def delete_source_entry():
    encode_entry_box.config(state=NORMAL)
    encode_entry_box.delete(0, END)
    encode_entry_box.config(state=DISABLED)

reset_source_input = HoverButton(encode_frame, text="X", command=delete_source_entry, foreground="white",
                                 background="#23272A", borderwidth="3", activebackground='grey')
reset_source_input.grid(row=0, column=3, columnspan=1, padx=5, pady=5, sticky=N + S + E + W)

# screenshots ---------------------------------------------------------------------------------------------------------

screenshot_frame = LabelFrame(root, text=' Sreenshots ', labelanchor="nw")
screenshot_frame.grid(column=0, row=2, columnspan=4, padx=5, pady=(5, 3), sticky=E + W)
screenshot_frame.configure(fg="#3498db", bg="#363636", bd=3, font=(set_font, 10))
screenshot_frame.grid_rowconfigure(0, weight=1)
screenshot_frame.grid_columnconfigure(0, weight=20)
screenshot_frame.grid_columnconfigure(1, weight=20)
screenshot_frame.grid_columnconfigure(2, weight=20)
screenshot_frame.grid_columnconfigure(3, weight=1)


# screenshot_scrolledtext = Entry(screenshot_frame, borderwidth=4, bg="#565656", fg='white', disabledforeground='white',
#                              disabledbackground="#565656")
# screenshot_scrolledtext.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky=N + S + E + W)
def test():
    if screenshot_scrolledtext.edit_modified():
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

            print(sorted_screenshots)
        else:
            print('screen shots are not even!!!')


screenshot_scrolledtext = scrolledtextwidget.ScrolledText(screenshot_frame, height=4)
screenshot_scrolledtext.grid(row=0, column=0, columnspan=3, pady=(0, 6), padx=10, sticky=E + W)
screenshot_scrolledtext.config(bg='#565656', fg='#CFD2D1', bd=8)


add_screenshots = HoverButton(screenshot_frame, text=">", command=test, foreground="white",
                                 background="#23272A", borderwidth="3", activebackground='grey', width=4)
add_screenshots.grid(row=0, column=3, columnspan=1, padx=5, pady=5, sticky=N + E + W)

def delete_source_entry():
    screenshot_scrolledtext.delete(1.0, END)

reset_screenshot_box = HoverButton(screenshot_frame, text="X", command=delete_source_entry, foreground="white",
                                 background="#23272A", borderwidth="3", activebackground='grey', width=4)
reset_screenshot_box.grid(row=0, column=3, columnspan=1, padx=5, pady=5, sticky=S + E + W)

# def test():
#     if screenshot_scrolledtext.edit_modified():
#         add_screenshots.config(state=NORMAL)
#     else:
#         add_screenshots.config(state=DISABLED)
#     root.after(50, test)
# test()



root.mainloop()