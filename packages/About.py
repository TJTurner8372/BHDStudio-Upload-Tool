from configparser import ConfigParser
from tkinter import (
    Toplevel,
    INSERT,
    Text,
    DISABLED,
    messagebox,
    FLAT,
    N,
    E,
    W,
    S,
    font,
    LabelFrame,
)


def openaboutwindow(
    main_root_title,
    main_root_color,
    frame_color_bg,
    frame_color_fg,
    text_color_fg,
    text_color_bg,
    set_font_size,
):
    global about_window

    # Defines the path to config.ini and opens it for reading/writing
    config_file = "runtime/config.ini"  # Creates (if doesn't exist) and defines location of config.ini
    config = ConfigParser()
    config.read(config_file)

    try:  # If "About" window is already opened, display a message, then close the "About" window
        if about_window.winfo_exists():
            messagebox.showinfo(
                title=f'"{about_window.wm_title()}" Info!',
                parent=about_window,
                message=f'"{about_window.wm_title()}" is already opened, closing window instead',
            )
            about_window.destroy()
            return
    except NameError:
        pass

    def about_exit_function():  # Exit function when hitting the 'X' button
        func_parser = ConfigParser()
        func_parser.read(config_file)
        if about_window.wm_state() == "normal":
            if (
                func_parser["save_window_locations"]["about_window"]
                != about_window.geometry()
            ):
                func_parser.set(
                    "save_window_locations", "about_window", about_window.geometry()
                )
                with open(config_file, "w") as configfile:
                    func_parser.write(configfile)

        about_window.destroy()  # Close window

    about_window = Toplevel()
    about_window.title("About")
    about_window.configure(background=main_root_color)
    if config["save_window_locations"]["about_window"] != "":
        about_window.geometry(config["save_window_locations"]["about_window"])
    about_window.resizable(False, False)
    about_window.protocol("WM_DELETE_WINDOW", about_exit_function)

    about_window.grid_columnconfigure(0, weight=1)
    about_window.grid_rowconfigure(0, weight=1)
    about_window.grid_rowconfigure(1, weight=1)

    detect_font = font.nametofont(
        "TkDefaultFont"
    )  # Get default font value into Font object
    set_font = detect_font.actual().get("family")

    about_information_frame = LabelFrame(
        about_window,
        text=" About ",
        labelanchor="nw",
        font=(set_font, set_font_size + 1, "bold"),
    )
    about_information_frame.grid(
        column=0, row=0, padx=5, pady=(0, 3), sticky=N + S + E + W
    )
    about_information_frame.configure(
        fg=frame_color_fg,
        bg=frame_color_bg,
        bd=3,
        font=(set_font, set_font_size, "bold"),
    )
    about_information_frame.grid_rowconfigure(0, weight=1)
    about_information_frame.grid_columnconfigure(0, weight=1)

    about_window_text = Text(
        about_information_frame,
        background=text_color_bg,
        foreground=text_color_fg,
        relief=FLAT,
        height=10,
        font=(set_font, set_font_size - 2),
    )
    about_window_text.grid(column=0, row=0, sticky=N + S + E + W)
    about_window_text.insert(INSERT, f"{main_root_title}\n")
    about_window_text.insert(INSERT, "\n")
    about_window_text.insert(
        INSERT,
        "Development:  jlw4049, thesb3\n"
        "Contributors: pilot538\n\n\n\n\n"
        "This product uses the TMDB API but is not endorsed or certified by TMDB.",
    )
    about_window_text.configure(state=DISABLED)

    about_information_frame2 = LabelFrame(
        about_window,
        text=" License ",
        labelanchor="nw",
        font=(set_font, set_font_size + 1, "bold"),
    )
    about_information_frame2.grid(
        column=0, row=1, padx=5, pady=(0, 10), sticky=N + S + E + W
    )
    about_information_frame2.configure(
        fg=frame_color_fg,
        bg=frame_color_bg,
        bd=3,
        font=(set_font, set_font_size, "bold"),
    )
    about_information_frame2.grid_rowconfigure(0, weight=1)
    about_information_frame2.grid_columnconfigure(0, weight=1)

    license_text = """
    Copyright (c) 2012-2022 Scott Chacon and others

    Permission is hereby granted, free of charge, to any person obtaining
    a copy of this software and associated documentation files (the
    "Software"), to deal in the Software without restriction, including
    without limitation the rights to use, copy, modify, merge, publish,
    distribute, sublicense, and/or sell copies of the Software, and to
    permit persons to whom the Software is furnished to do so, subject to
    the following conditions:
    
    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.
    
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
    LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
    OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
    WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
    """

    about_window_license = Text(
        about_information_frame2,
        background=text_color_bg,
        foreground=text_color_fg,
        relief=FLAT,
        height=22,
        font=(set_font, set_font_size - 2),
    )
    about_window_license.grid(column=0, row=0, sticky=N + S + E + W)
    about_window_license.insert(INSERT, license_text)
    about_window_license.configure(state=DISABLED)


# -------------------------------------------------------------------------------------------------------- About Window
