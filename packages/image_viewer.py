import pathlib
import re
from tkinter import (
    ttk,
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
    Frame,
    Scrollbar,
    VERTICAL,
    PhotoImage,
    Listbox,
    SINGLE,
)

from PIL import Image, ImageTk
from custom_hovertip import CustomTooltipLabel
from pymediainfo import MediaInfo

from packages.default_config_params import *
from packages.hoverbutton import HoverButton


class ImageViewer:
    def __init__(
        self,
        custom_window_bg_color,
        custom_frame_bg_colors,
        set_font,
        set_font_size,
        custom_label_frame_colors,
        custom_label_colors,
        custom_button_colors,
        custom_listbox_color,
        set_fixed_font,
        screenshot_selected_var,
        screenshot_comparison_var,
        screenshot_sync_var,
    ):

        # define ui vars
        self.custom_window_bg_color = custom_window_bg_color
        self.custom_frame_bg_colors = custom_frame_bg_colors
        self.set_font = set_font
        self.set_font_size = set_font_size
        self.custom_label_frame_colors = custom_label_frame_colors
        self.custom_label_colors = custom_label_colors
        self.custom_button_colors = custom_button_colors
        self.custom_listbox_color = custom_listbox_color
        self.set_fixed_font = set_fixed_font

        # define storage vars
        self.screenshot_selected_var = screenshot_selected_var
        self.screenshot_comparison_var = screenshot_comparison_var
        self.screenshot_sync_var = screenshot_sync_var

        # define global vars
        self.comparison_index = 0
        self.selected_index_var = 0
        self.return_output = {
            "synced": True,
            "images": [],
            "offset": None,
            "operator": None,
        }
        self.media_info_img_next = None
        self.image_track_next = None
        self.media_info_img_back = None
        self.image_track_back = None
        self.resized_image1 = None
        self.media_info_img_rem = None
        self.image_track_rem = None
        self.media_info_img_add = None
        self.image_track_add = None
        self.undo_image_list = []

        # define parser
        self.auto_screenshot_parser = ConfigParser()
        self.auto_screenshot_parser.read(config_file)

        # create image viewer
        self.image_viewer = Toplevel()
        self.image_viewer.title("Image Viewer")
        self.image_viewer.configure(background=self.custom_window_bg_color)
        if self.auto_screenshot_parser["save_window_locations"]["image_viewer"] != "":
            self.image_viewer.geometry(
                self.auto_screenshot_parser["save_window_locations"]["image_viewer"]
            )

        # row and column configure
        self.image_viewer.grid_rowconfigure(0, weight=1)
        self.image_viewer.grid_columnconfigure(0, weight=1)

        # notebook tabs
        self.tabs = ttk.Notebook(self.image_viewer)
        self.tabs.grid(
            row=0, column=0, columnspan=5, sticky=E + W + N + S, padx=0, pady=0
        )
        self.tabs.grid_columnconfigure(0, weight=1)
        self.tabs.grid_rowconfigure(0, weight=1)

        # image selection tab
        self.image_tab = Frame(self.tabs, bg=self.custom_frame_bg_colors["specialbg"])
        self.tabs.add(self.image_tab, text=" Images ")

        # row and column configure
        for i_v_r in range(3):
            self.image_tab.grid_rowconfigure(i_v_r, weight=1)
        for i_v_c in range(5):
            self.image_tab.grid_columnconfigure(i_v_c, weight=1)

        # sync selection tab
        self.sync_tab = None
        self.nested_sync_frame = None
        self.sync_tabs = None
        self.reference_tab_1 = None
        self.reference_tab_2 = None
        self.rf1_image = None
        self.resized_rf1_image = None
        self.image_sync_label1 = None
        self.sync_images1 = []
        self.sync_img_select = 0
        self.sync_images2 = []
        self.rf1_sync_image = None
        self.rf2_image = None
        self.rf2_sync_image = None
        self.image_sync_label2 = None
        self.resized_rf2_image = None
        self._sync_tab_ui()

        # image info frame
        self.image_info_frame = LabelFrame(
            self.image_tab,
            text=" Image Info ",
            labelanchor="nw",
            bd=3,
            font=(self.set_font, self.set_font_size + 1, "bold"),
            fg=self.custom_label_frame_colors["foreground"],
            bg=self.custom_frame_bg_colors["specialbg"],
        )
        self.image_info_frame.grid(
            column=0, row=0, columnspan=4, pady=2, padx=2, sticky=N + S + E + W
        )
        self.image_info_frame.grid_columnconfigure(0, weight=1)
        self.image_info_frame.grid_columnconfigure(1, weight=100)
        self.image_info_frame.grid_columnconfigure(2, weight=1)
        self.image_info_frame.grid_rowconfigure(0, weight=1)

        # create name label
        self.image_name_label = Label(
            self.image_info_frame,
            background=self.custom_frame_bg_colors["specialbg"],
            fg=self.custom_label_colors["foreground"],
            font=(self.set_font, self.set_font_size - 1),
        )
        self.image_name_label.grid(
            row=0, column=0, columnspan=1, sticky=W, padx=5, pady=(2, 0)
        )

        # create image resolution label
        self.image_resolution_label = Label(
            self.image_info_frame,
            background=self.custom_frame_bg_colors["specialbg"],
            fg=self.custom_label_colors["foreground"],
            font=(self.set_font, self.set_font_size - 1),
        )
        self.image_resolution_label.grid(
            row=0, column=1, columnspan=1, sticky=E, padx=10, pady=(2, 0)
        )

        # create image number label
        self.image_number_label = Label(
            self.image_info_frame,
            background=self.custom_frame_bg_colors["specialbg"],
            fg=self.custom_label_colors["foreground"],
            font=(self.set_font, self.set_font_size - 1),
        )
        self.image_number_label.grid(
            row=0, column=2, columnspan=1, sticky=E, padx=5, pady=(2, 0)
        )

        # create image preview frame
        self.image_preview_frame = LabelFrame(
            self.image_tab,
            text=" Image Preview ",
            labelanchor="nw",
            bd=3,
            font=(self.set_font, self.set_font_size + 1, "bold"),
            fg=self.custom_label_frame_colors["foreground"],
            bg=self.custom_frame_bg_colors["specialbg"],
        )
        self.image_preview_frame.grid(
            column=0, row=1, columnspan=4, pady=2, padx=2, sticky=N + S + E + W
        )
        self.image_preview_frame.grid_columnconfigure(0, weight=1)
        self.image_preview_frame.grid_rowconfigure(0, weight=1)

        # create image list
        self.comparison_img_list = sorted(
            [
                x_img
                for x_img in pathlib.Path(self.screenshot_comparison_var).glob("*.png")
            ]
        )

        # update image name label with first image from list
        self.image_name_label.config(
            text=f"{pathlib.Path(self.comparison_img_list[self.comparison_index]).name}"
        )

        # parse first image from list to get resolution
        self.media_info_img = MediaInfo.parse(
            pathlib.Path(self.comparison_img_list[self.comparison_index])
        )
        self.image_track = self.media_info_img.image_tracks[0]

        # update image resolution label
        self.image_resolution_label.config(
            text=f"{self.image_track.width}x{self.image_track.height}"
        )

        # label to print what photo of amount of total photos you are on
        self.image_number_label.config(
            text=f"{self.comparison_index + 1} of {len(self.comparison_img_list)}"
        )

        # create image instance and resize the photo
        self.loaded_image = Image.open(self.comparison_img_list[self.comparison_index])
        self.loaded_image.thumbnail((1000, 562), Image.LANCZOS)
        self.resized_image = ImageTk.PhotoImage(self.loaded_image)

        # put resized image into label
        self.image_preview_label = Label(
            self.image_preview_frame,
            image=self.resized_image,
            background=self.custom_frame_bg_colors["specialbg"],
            cursor="hand2",
        )
        self.image_preview_label.image = self.resized_image
        self.image_preview_label.grid(column=0, row=0, columnspan=1)

        # add a left click function to open the photo in your default os viewer
        self.image_preview_label.bind(
            "<Button-1>",
            lambda event: Image.open(
                self.comparison_img_list[self.comparison_index]
            ).show(),
        )

        # create image button frame
        self.img_button_frame = Frame(
            self.image_tab, bg=self.custom_frame_bg_colors["specialbg"]
        )
        self.img_button_frame.grid(
            column=0, row=2, columnspan=4, pady=2, padx=2, sticky=N + S + E + W
        )
        self.img_button_frame.grid_columnconfigure(0, weight=1000)
        self.img_button_frame.grid_columnconfigure(1, weight=1000)
        self.img_button_frame.grid_rowconfigure(0, weight=1)

        # button to run next image function
        self.next_img = HoverButton(
            self.img_button_frame,
            text=">>",
            command=self.load_next_image,
            borderwidth="3",
            width=4,
            foreground=self.custom_button_colors["foreground"],
            background=self.custom_button_colors["background"],
            activeforeground=self.custom_button_colors["activeforeground"],
            activebackground=self.custom_button_colors["activebackground"],
            disabledforeground=self.custom_button_colors["disabledforeground"],
        )
        self.next_img.grid(row=0, column=1, columnspan=1, padx=5, pady=(7, 0), sticky=W)

        # bind right arrow key (on key release) to load the next image
        self.image_viewer.bind("<KeyRelease-Right>", self.load_next_image)

        # hover tip tool-tip
        CustomTooltipLabel(
            anchor_widget=self.next_img,
            hover_delay=1000,
            background=self.custom_window_bg_color,
            foreground=self.custom_label_frame_colors["foreground"],
            font=(self.set_fixed_font, self.set_font_size, "bold"),
            text="Use hotkey 'Right Arrow' to view next image",
        )

        # button to run last image function
        self.back_img = HoverButton(
            self.img_button_frame,
            text="<<",
            command=self.load_last_image,
            borderwidth="3",
            width=4,
            foreground=self.custom_button_colors["foreground"],
            background=self.custom_button_colors["background"],
            activeforeground=self.custom_button_colors["activeforeground"],
            activebackground=self.custom_button_colors["activebackground"],
            disabledforeground=self.custom_button_colors["disabledforeground"],
        )
        self.back_img.grid(row=0, column=0, columnspan=1, padx=5, pady=(7, 0), sticky=E)

        # bind the left arrow key (on key release)
        self.image_viewer.bind("<KeyRelease-Left>", self.load_last_image)

        # hover tip tool-tip
        CustomTooltipLabel(
            anchor_widget=self.back_img,
            hover_delay=1000,
            background=self.custom_window_bg_color,
            foreground=self.custom_label_frame_colors["foreground"],
            font=(self.set_fixed_font, self.set_font_size, "bold"),
            text="Use hotkey 'Left Arrow' to view previous image",
        )

        # info frame for the image viewer
        self.set_info_frame = LabelFrame(
            self.image_tab,
            text=" Info ",
            labelanchor="nw",
            bd=3,
            font=(self.set_font, self.set_font_size + 1, "bold"),
            fg=self.custom_label_frame_colors["foreground"],
            bg=self.custom_frame_bg_colors["specialbg"],
        )
        self.set_info_frame.grid(
            column=4, row=0, columnspan=1, pady=2, padx=2, sticky=N + S + E + W
        )
        self.set_info_frame.grid_columnconfigure(0, weight=1)
        self.set_info_frame.grid_columnconfigure(1, weight=100)
        self.set_info_frame.grid_columnconfigure(2, weight=1)
        self.set_info_frame.grid_rowconfigure(0, weight=1)

        # image viewer frame
        self.img_viewer_frame = Frame(
            self.image_tab, bg=self.custom_frame_bg_colors["specialbg"], bd=0
        )
        self.img_viewer_frame.grid(
            column=4,
            columnspan=1,
            row=1,
            rowspan=1,
            pady=(3, 2),
            padx=4,
            sticky=W + E + N + S,
        )
        self.img_viewer_frame.grid_columnconfigure(0, weight=1)
        self.img_viewer_frame.grid_rowconfigure(0, weight=200)
        self.img_viewer_frame.grid_rowconfigure(1, weight=200)
        self.img_viewer_frame.grid_rowconfigure(2, weight=100)

        # create image name label
        self.image_name_label2 = Label(
            self.set_info_frame,
            text="0 sets (0 images)",
            background=self.custom_frame_bg_colors["specialbg"],
            fg=self.custom_label_colors["foreground"],
            font=(self.set_font, self.set_font_size - 1),
        )
        self.image_name_label2.grid(
            row=0, column=0, columnspan=1, sticky=E, padx=5, pady=(2, 0)
        )

        # create image info label
        self.image_name1_label = Label(
            self.set_info_frame,
            text="6 sets (12 images) required",
            background=self.custom_frame_bg_colors["specialbg"],
            fg=self.custom_label_colors["foreground"],
            font=(self.set_font, self.set_font_size - 1, "italic"),
        )
        self.image_name1_label.grid(
            row=0, column=1, columnspan=1, sticky=E, padx=5, pady=(2, 0)
        )

        # right scroll bar for selected listbox
        self.image_v_right_scrollbar = Scrollbar(self.img_viewer_frame, orient=VERTICAL)

        # create selected list box
        self.img_viewer_listbox = Listbox(
            self.img_viewer_frame,
            bg=self.custom_listbox_color["background"],
            fg=self.custom_listbox_color["foreground"],
            selectbackground=self.custom_listbox_color["selectbackground"],
            selectforeground=self.custom_listbox_color["selectforeground"],
            highlightthickness=0,
            width=40,
            yscrollcommand=self.image_v_right_scrollbar.set,
            selectmode=SINGLE,
            bd=4,
            activestyle="none",
            font=(self.set_fixed_font, self.set_font_size - 2),
        )
        self.img_viewer_listbox.grid(
            row=0, column=0, rowspan=2, sticky=N + E + S + W, pady=(8, 0)
        )
        self.image_v_right_scrollbar.config(command=self.img_viewer_listbox.yview)
        self.image_v_right_scrollbar.grid(
            row=0, column=2, rowspan=2, sticky=N + W + S, pady=(8, 0)
        )

        # create mini preview frame
        self.mini_preview_frame = LabelFrame(
            self.img_viewer_frame,
            text=" Preview ",
            labelanchor="nw",
            bd=3,
            font=(self.set_font, self.set_font_size + 1, "bold"),
            fg=self.custom_label_frame_colors["foreground"],
            bg=self.custom_frame_bg_colors["specialbg"],
        )
        self.mini_preview_frame.grid(
            column=0, columnspan=3, row=2, sticky=N + S + E + W
        )
        self.mini_preview_frame.grid_columnconfigure(0, weight=1)
        self.mini_preview_frame.grid_rowconfigure(0, weight=1)

        # bind listbox select event to the thumbnail update function
        self.img_viewer_listbox.bind("<<ListboxSelect>>", self.update_thumbnail)

        # define zero image to fill label
        self.zero_img = PhotoImage()

        # put resized image into label
        self.mini_image_preview_label = Label(
            self.mini_preview_frame,
            background=self.custom_frame_bg_colors["specialbg"],
            cursor="hand2",
            image=self.zero_img,
            width=348,
            height=160,
        )
        self.mini_image_preview_label.image = self.zero_img
        self.mini_image_preview_label.grid(column=0, row=0, sticky=N + S + E + W)

        # image button frame for selected list box
        self.img_button2_frame = Frame(
            self.image_tab, bg=self.custom_frame_bg_colors["specialbg"]
        )
        self.img_button2_frame.grid(
            column=4, row=2, columnspan=1, pady=2, padx=2, sticky=N + S + E + W
        )
        self.img_button2_frame.grid_columnconfigure(0, weight=100)
        self.img_button2_frame.grid_columnconfigure(1, weight=100)
        self.img_button2_frame.grid_columnconfigure(2, weight=1)
        self.img_button2_frame.grid_rowconfigure(0, weight=1)

        # create minis/reverse button
        self.minus_btn = HoverButton(
            self.img_button2_frame,
            text="<<<",
            command=self.remove_pair_from_listbox,
            borderwidth="3",
            width=4,
            foreground=self.custom_button_colors["foreground"],
            background=self.custom_button_colors["background"],
            activeforeground=self.custom_button_colors["activeforeground"],
            activebackground=self.custom_button_colors["activebackground"],
            disabledforeground=self.custom_button_colors["disabledforeground"],
        )
        self.minus_btn.grid(row=0, column=0, padx=5, pady=(7, 0), sticky=E)
        self.image_viewer.bind(
            "<Shift-Down>", lambda event: self.hotkey_remove_pair_from_listbox()
        )

        # hover tip tool-tip
        CustomTooltipLabel(
            anchor_widget=self.minus_btn,
            hover_delay=1000,
            background=self.custom_window_bg_color,
            foreground=self.custom_label_frame_colors["foreground"],
            font=(self.set_fixed_font, self.set_font_size, "bold"),
            wraplength=220,
            text="Use hotkeys 'Shift + Down Arrow' to remove previously loaded images",
        )

        # move right button
        self.move_right = HoverButton(
            self.img_button2_frame,
            text=">>>",
            command=self.add_pair_to_listbox,
            borderwidth="3",
            width=4,
            foreground=self.custom_button_colors["foreground"],
            background=self.custom_button_colors["background"],
            activeforeground=self.custom_button_colors["activeforeground"],
            activebackground=self.custom_button_colors["activebackground"],
            disabledforeground=self.custom_button_colors["disabledforeground"],
        )
        self.move_right.grid(row=0, column=1, padx=5, pady=(7, 0), sticky=W)
        self.image_viewer.bind("<Shift-Up>", lambda event: self.add_pair_to_listbox())

        # hover tip tool-tip
        CustomTooltipLabel(
            anchor_widget=self.move_right,
            hover_delay=1000,
            background=self.custom_window_bg_color,
            foreground=self.custom_label_frame_colors["foreground"],
            font=(self.set_fixed_font, self.set_font_size, "bold"),
            wraplength=220,
            text="Use hotkeys 'Shift + Up Arrow' to select current set of images",
        )

        # add to image list box button
        self.add_images_to_listbox = HoverButton(
            self.img_button2_frame,
            text="Apply",
            command=self.add_images_to_listbox_func,
            state=DISABLED,
            borderwidth="3",
            width=10,
            foreground=self.custom_button_colors["foreground"],
            background=self.custom_button_colors["background"],
            activeforeground=self.custom_button_colors["activeforeground"],
            activebackground=self.custom_button_colors["activebackground"],
            disabledforeground=self.custom_button_colors["disabledforeground"],
        )
        self.add_images_to_listbox.grid(row=0, column=2, padx=5, pady=(7, 0), sticky=E)

        # change 'X' button on image viewer (use the Apply button function)
        self.image_viewer.protocol("WM_DELETE_WINDOW", self.add_images_to_listbox_func)

        # start loop for button checker
        self.enable_disable_buttons_by_index()

        # focus image viewer window for keybinding
        self.image_viewer.focus_force()

        # wait for image viewer to be closed
        self.image_viewer.wait_window()

    def load_next_image(self, *_):
        """function to load next image"""

        # if next image is not disabled (this prevents the keystrokes from doing anything when it should be disabled)
        if self.next_img.cget("state") != DISABLED:
            # increase the comparison index value by 1
            self.comparison_index += 1

            # open the image in the viewer
            im = Image.open(self.comparison_img_list[self.comparison_index])
            im.thumbnail((1000, 562), Image.LANCZOS)
            photo = ImageTk.PhotoImage(im)
            self.image_preview_label.config(image=photo)
            self.image_preview_label.image = photo

            # update the left click photo to open in OS photo viewer
            self.image_preview_label.bind(
                "<Button-1>",
                lambda event: Image.open(
                    self.comparison_img_list[self.comparison_index]
                ).show(),
            )

            # update all the labels
            self.image_name_label.config(
                text=f"{pathlib.Path(self.comparison_img_list[self.comparison_index]).name}"
            )
            self.media_info_img_next = MediaInfo.parse(
                pathlib.Path(self.comparison_img_list[self.comparison_index])
            )
            self.image_track_next = self.media_info_img_next.image_tracks[0]
            self.image_resolution_label.config(
                text=f"{self.image_track_next.width}x{self.image_track_next.height}"
            )
            self.image_number_label.config(
                text=f"{self.comparison_index + 1} of {len(self.comparison_img_list)}"
            )

    def load_last_image(self, *_):
        """function to load last image"""

        # if back image is not disabled (this prevents the keystrokes from doing anything when it should be disabled)
        if self.back_img.cget("state") != DISABLED:
            # subtract the comparison index by 1
            self.comparison_index -= 1

            # update the image in the image viewer
            im = Image.open(self.comparison_img_list[self.comparison_index])
            im.thumbnail((1000, 562), Image.LANCZOS)
            photo = ImageTk.PhotoImage(im)
            self.image_preview_label.config(image=photo)
            self.image_preview_label.image = photo

            # load new image to be opened when left-clicked in OS native viewer
            self.image_preview_label.bind(
                "<Button-1>",
                lambda event: Image.open(
                    self.comparison_img_list[self.comparison_index]
                ).show(),
            )

            # update all the labels
            self.image_name_label.config(
                text=f"{pathlib.Path(self.comparison_img_list[self.comparison_index]).name}"
            )
            self.media_info_img_back = MediaInfo.parse(
                pathlib.Path(self.comparison_img_list[self.comparison_index])
            )
            self.image_track_back = self.media_info_img_back.image_tracks[0]
            self.image_resolution_label.config(
                text=f"{self.image_track_back.width}x{self.image_track_back.height}"
            )
            self.image_number_label.config(
                text=f"{self.comparison_index + 1} of {len(self.comparison_img_list)}"
            )

    def update_thumbnail(self, event):
        """update small thumbnail in image viewer window when something in the list box is selected"""

        img_selection = event.widget.curselection()  # get current selection
        # if there is a selection
        if img_selection:
            # define index of selection
            cur_selection_index = img_selection[0]
            img_data = event.widget.get(cur_selection_index)

            # create image instance and resize the photo
            thumbnail_img = Image.open(
                pathlib.Path(pathlib.Path(self.screenshot_selected_var) / img_data)
            )
            thumbnail_img.thumbnail((348, 158), Image.LANCZOS)
            self.resized_image1 = ImageTk.PhotoImage(thumbnail_img)

            # update the label with the selected image
            self.mini_image_preview_label.config(image=self.resized_image1)
            self.mini_image_preview_label.image = self.resized_image1
            self.mini_image_preview_label.bind(
                "<Button-1>",
                lambda b_event: Image.open(
                    pathlib.Path(pathlib.Path(self.screenshot_selected_var) / img_data)
                ).show(),
            )

    def hotkey_remove_pair_from_listbox(self):
        """Selects last moved image to be removed from listbox"""
        try:
            listbox_list = [x for x in self.img_viewer_listbox.get(0, END)].index(
                self.undo_image_list[-1]
            )
            self.img_viewer_listbox.selection_clear(0, END)
            self.img_viewer_listbox.selection_set(listbox_list)
            self.remove_pair_from_listbox()
        except IndexError:
            return

    def remove_pair_from_listbox(self):
        """remove pair from listbox function"""
        get_prefix_number = None

        # if something is selected in the list box
        if self.img_viewer_listbox.curselection():
            # get the selected item from list box
            for i in self.img_viewer_listbox.curselection():
                get_prefix_number = re.search(
                    r"(\d{1,3})[a|b]_.+__.+", str(self.img_viewer_listbox.get(i))
                )

            # get the frame number to match the pairs
            for images_with_prefix in self.img_viewer_listbox.get(0, END):
                get_pair = re.findall(
                    rf"{get_prefix_number.group(1)}[a|b]_.+__.+\.png",
                    images_with_prefix,
                )
                # once pair is found
                if get_pair:
                    # use pathlib rename feature to move the file back to the comparison directory/out of the listbox
                    pathlib.Path(
                        pathlib.Path(self.screenshot_selected_var) / get_pair[0]
                    ).rename(
                        pathlib.Path(
                            pathlib.Path(self.screenshot_comparison_var) / get_pair[0]
                        )
                    )

                    # update undo image list
                    self.undo_image_list.remove(get_pair[0])

            # delete the list box and update it with what ever is left
            self.img_viewer_listbox.delete(0, END)

            # update the listbox
            for x in sorted(pathlib.Path(self.screenshot_selected_var).glob("*.png")):
                self.img_viewer_listbox.insert(END, x.name)

            # clear the comparison image list
            self.comparison_img_list.clear()

            # update the comparison image list with everything in the directory
            self.comparison_img_list = sorted(
                [
                    x_img
                    for x_img in pathlib.Path(self.screenshot_comparison_var).glob(
                        "*.png"
                    )
                ]
            )

            # if there is at least 1 item in the list
            if self.comparison_img_list:
                # find index of current item
                # refresh the image viewer with the updated list while retaining current position
                try:
                    self.comparison_index = int(
                        self.comparison_img_list.index(
                            pathlib.Path(
                                pathlib.Path(self.screenshot_comparison_var)
                                / self.image_name_label.cget("text")
                            )
                        )
                    )
                except ValueError:
                    self.comparison_index = 0

                im = Image.open(self.comparison_img_list[self.comparison_index])
                im.thumbnail((1000, 562), Image.LANCZOS)
                photo = ImageTk.PhotoImage(im)
                self.image_preview_label.grid()
                self.image_preview_label.config(image=photo)
                self.image_preview_label.image = photo
                self.image_preview_label.bind(
                    "<Button-1>",
                    lambda event: Image.open(
                        self.comparison_img_list[self.comparison_index]
                    ).show(),
                )

                # update labels
                self.image_name_label.config(
                    text=f"{pathlib.Path(self.comparison_img_list[self.comparison_index]).name}"
                )
                self.media_info_img_rem = MediaInfo.parse(
                    pathlib.Path(self.comparison_img_list[self.comparison_index])
                )
                self.image_track_rem = self.media_info_img_rem.image_tracks[0]
                self.image_resolution_label.config(
                    text=f"{self.image_track_rem.width}x{self.image_track_rem.height}"
                )
                self.image_number_label.config(
                    text=f"{self.comparison_index + 1} of {len(self.comparison_img_list)}"
                )
                self.image_name_label2.config(
                    text=f"{int(self.img_viewer_listbox.size() * .5)} sets "
                    f"({self.img_viewer_listbox.size()} images)"
                )

    def add_pair_to_listbox(self):
        """add pair to the selected listbox"""
        selected_index_var = None

        # find the prefix
        try:
            get_file_prefix = re.search(
                r"(\d{1,3})[a|b]_.+__.+",
                str(pathlib.Path(self.comparison_img_list[self.comparison_index]).name),
            )
        except IndexError:
            return

        for full_name in self.comparison_img_list:
            get_pair = re.findall(
                rf"{get_file_prefix.group(1)}[b|a]_.+__.+\.png", full_name.name
            )
            # once a pair is found use pathlib rename to move them from the comparison list/dir to the selected dir/list
            if get_pair:
                pathlib.Path(
                    pathlib.Path(self.screenshot_comparison_var) / get_pair[0]
                ).rename(
                    pathlib.Path(self.screenshot_selected_var)
                    / pathlib.Path(get_pair[0]).name
                )

                # update added images list
                self.undo_image_list.append(get_pair[0])

                # take the last item that is moved and update the selected index var
                selected_index_var = (
                    int(
                        self.comparison_img_list.index(
                            pathlib.Path(self.screenshot_comparison_var) / get_pair[0]
                        )
                    )
                    - 1
                )

        # clear the listbox
        self.img_viewer_listbox.delete(0, END)

        # update the listbox
        for x_l in sorted(pathlib.Path(self.screenshot_selected_var).glob("*.png")):
            self.img_viewer_listbox.insert(END, x_l.name)

        # clear the comparison image list
        self.comparison_img_list.clear()

        # update the comparison image list with everything in the directory
        self.comparison_img_list = sorted(
            [
                x_img
                for x_img in pathlib.Path(self.screenshot_comparison_var).glob("*.png")
            ]
        )

        # if there is anything left in the comparison img list
        if self.comparison_img_list:
            # attempt to use the same index (to keep position the same/close to the same) and update the image viewer
            try:
                self.comparison_index = selected_index_var
                im = Image.open(self.comparison_img_list[self.comparison_index])
            # if unable to use that index, subtract 2 from it (this prevents errors at the end of the list)
            except IndexError:
                self.comparison_index = selected_index_var - 2
                im = Image.open(self.comparison_img_list[self.comparison_index])
            im.thumbnail((1000, 562), Image.LANCZOS)
            photo = ImageTk.PhotoImage(im)
            self.image_preview_label.config(image=photo)
            self.image_preview_label.image = photo
            self.image_preview_label.bind(
                "<Button-1>",
                lambda event: Image.open(
                    self.comparison_img_list[self.comparison_index]
                ).show(),
            )

            # update the labels
            self.image_name_label.config(
                text=f"{pathlib.Path(self.comparison_img_list[self.comparison_index]).name}"
            )
            self.media_info_img_add = MediaInfo.parse(
                pathlib.Path(self.comparison_img_list[self.comparison_index])
            )
            self.image_track_add = self.media_info_img_add.image_tracks[0]
            self.image_resolution_label.config(
                text=f"{self.image_track_add.width}x{self.image_track_add.height}"
            )
            self.image_number_label.config(
                text=f"{self.comparison_index + 1} of {len(self.comparison_img_list)}"
            )
            self.image_name_label2.config(
                text=f"{int(self.img_viewer_listbox.size() * .5)} sets "
                f"({self.img_viewer_listbox.size()} images)"
            )
        # if there is nothing left in the comparison image box, clear the box and all the labels
        else:
            self.image_preview_label.grid_forget()
            self.image_name_label.config(text="")
            self.image_resolution_label.config(text="")
            self.image_number_label.config(text="")

    # add images to list box function
    def add_images_to_listbox_func(self):
        # define parser
        add_img_exit_parser = ConfigParser()
        add_img_exit_parser.read(config_file)

        # save window position to config if different
        if self.image_viewer.wm_state() == "normal":
            if (
                add_img_exit_parser["save_window_locations"]["image_viewer"]
                != self.image_viewer.geometry()
            ):
                add_img_exit_parser.set(
                    "save_window_locations",
                    "image_viewer",
                    self.image_viewer.geometry(),
                )
                with open(config_file, "w") as nfo_configfile:
                    add_img_exit_parser.write(nfo_configfile)

        # create list of images to autoload into the program
        list_of_selected_images = []
        for selected_img in pathlib.Path(self.screenshot_selected_var).glob("*.png"):
            list_of_selected_images.append(selected_img)

        # close image viewer window
        self.image_viewer.destroy()

        # return list of selected screenshots to main script
        self.return_output.update({"images": list_of_selected_images})

    # loop to enable/disable buttons depending on index
    def enable_disable_buttons_by_index(self):
        # disable both buttons if list is empty
        if not self.comparison_img_list:
            self.back_img.config(state=DISABLED)
            self.next_img.config(state=DISABLED)
        # enable back or next button depending on the list
        elif self.comparison_img_list:
            # enable or disable back button
            if self.comparison_index == 0:
                self.back_img.config(state=DISABLED)
            else:
                self.back_img.config(state=NORMAL)
            # enable or disable next button
            if self.comparison_index == len(self.comparison_img_list) - 1:
                self.next_img.config(state=DISABLED)
            else:
                self.next_img.config(state=NORMAL)

        # enable apply button (check label to see if required amount of sets are met)
        if int(str(self.image_name_label2.cget("text"))[0]) >= 6:
            self.add_images_to_listbox.config(state=NORMAL)
        else:
            self.add_images_to_listbox.config(state=DISABLED)

        self.image_viewer.after(50, self.enable_disable_buttons_by_index)

    def _sync_tab_ui(self):
        # generate list of sync images
        self._generate_sync_images1()
        self._generate_sync_images2()
        self._select_next_sync_image()

        # main sync tab
        self.sync_tab = Frame(self.tabs, bg=self.custom_frame_bg_colors["specialbg"])
        self.tabs.add(self.sync_tab, text=" Sync ")
        self.sync_tab.grid_rowconfigure(0, weight=1)
        self.sync_tab.grid_rowconfigure(1, weight=1)
        self.sync_tab.grid_columnconfigure(0, weight=1)

        # frame for nested notebook tabs
        self.nested_sync_frame = Frame(self.sync_tab, bg=self.custom_window_bg_color)
        self.nested_sync_frame.grid(
            column=0,
            row=0,
            pady=(15, 5),
            padx=15,
            sticky=N + S + E + W,
            columnspan=5,
        )
        self.nested_sync_frame.grid_columnconfigure(0, weight=1)
        self.nested_sync_frame.grid_columnconfigure(1, weight=1)

        # notebook tabs
        self.sync_tabs = ttk.Notebook(self.nested_sync_frame)
        self.sync_tabs.grid(
            row=0, column=0, columnspan=5, sticky=E + W + N + S, padx=10, pady=10
        )
        self.sync_tabs.grid_columnconfigure(0, weight=1)
        self.sync_tabs.grid_rowconfigure(0, weight=1)

        # reference tab 1
        self.reference_tab_1 = Frame(
            self.sync_tabs, bg=self.custom_frame_bg_colors["specialbg"]
        )
        self.sync_tabs.add(self.reference_tab_1, text=" Reference 1 ")
        self.reference_tab_1.grid_rowconfigure(0, weight=1)
        self.reference_tab_1.grid_columnconfigure(0, weight=1)

        # image label for tab 1
        self.rf1_image = Image.open(self._locate_sync_img_encode(1))
        self.rf1_image.thumbnail((1000, 562), Image.LANCZOS)
        self.resized_rf1_image = ImageTk.PhotoImage(self.rf1_image)

        # put resized image into label
        self.image_sync_label1 = Label(
            self.reference_tab_1,
            image=self.resized_rf1_image,
            background=self.custom_frame_bg_colors["specialbg"],
            cursor="hand2",
        )
        self.image_sync_label1.image = self.resized_rf1_image
        self.image_sync_label1.grid(column=0, row=0, columnspan=5, sticky=N + S + E + W)

        # bind mouse event to update images
        self.image_sync_label1.bind("<Enter>", self._image_swap1)
        self.image_sync_label1.bind("<Leave>", self._image_swap_out1)

        # reference tab 2
        self.reference_tab_2 = Frame(
            self.sync_tabs, bg=self.custom_frame_bg_colors["specialbg"]
        )
        self.sync_tabs.add(self.reference_tab_2, text=" Reference 2 ")
        self.reference_tab_2.grid_rowconfigure(0, weight=1)
        self.reference_tab_2.grid_columnconfigure(0, weight=1)

        # image label for tab 2
        self.rf2_image = Image.open(self._locate_sync_img_encode(2))
        self.rf2_image.thumbnail((1000, 562), Image.LANCZOS)
        self.resized_rf2_image = ImageTk.PhotoImage(self.rf2_image)

        # put resized image into label
        self.image_sync_label2 = Label(
            self.reference_tab_2,
            image=self.resized_rf2_image,
            background=self.custom_frame_bg_colors["specialbg"],
            cursor="hand2",
        )
        self.image_sync_label2.image = self.resized_rf2_image
        self.image_sync_label2.grid(column=0, row=0, columnspan=5)

        # bind mouse event to update images
        self.image_sync_label2.bind("<Enter>", self._image_swap2)
        self.image_sync_label2.bind("<Leave>", self._image_swap_out2)

        # frame for buttons
        self.sync_img_button_frame = Frame(
            self.sync_tab, bg=self.custom_frame_bg_colors["specialbg"]
        )
        self.sync_img_button_frame.grid(
            column=0, row=2, columnspan=5, pady=2, padx=2, sticky=N + S + E + W
        )
        for s_i_b_f in range(6):
            self.sync_img_button_frame.grid_columnconfigure(s_i_b_f, weight=1000)
        self.sync_img_button_frame.grid_rowconfigure(0, weight=1)

        # next sync image
        self.next_img = HoverButton(
            self.sync_img_button_frame,
            text=">>",
            command=self._select_next_sync_image,
            borderwidth="3",
            width=4,
            foreground=self.custom_button_colors["foreground"],
            background=self.custom_button_colors["background"],
            activeforeground=self.custom_button_colors["activeforeground"],
            activebackground=self.custom_button_colors["activebackground"],
            disabledforeground=self.custom_button_colors["disabledforeground"],
        )
        self.next_img.grid(row=1, column=3, columnspan=1, padx=5, pady=(7, 0), sticky=W)

        # back sync image
        self.back_img = HoverButton(
            self.sync_img_button_frame,
            text="<<",
            command=self._select_back_sync_image,
            borderwidth="3",
            width=4,
            foreground=self.custom_button_colors["foreground"],
            background=self.custom_button_colors["background"],
            activeforeground=self.custom_button_colors["activeforeground"],
            activebackground=self.custom_button_colors["activebackground"],
            disabledforeground=self.custom_button_colors["disabledforeground"],
        )
        self.back_img.grid(row=1, column=2, columnspan=1, padx=5, pady=(7, 0), sticky=E)

        # apply sync
        self.apply_sync = HoverButton(
            self.sync_img_button_frame,
            text="Apply Sync",
            command=self._apply_sync,
            borderwidth="3",
            width=15,
            foreground=self.custom_button_colors["foreground"],
            background=self.custom_button_colors["background"],
            activeforeground=self.custom_button_colors["activeforeground"],
            activebackground=self.custom_button_colors["activebackground"],
            disabledforeground=self.custom_button_colors["disabledforeground"],
        )
        self.apply_sync.grid(
            row=1, column=5, columnspan=1, padx=5, pady=(7, 0), sticky=E
        )

        # sync position label
        self.sync_position = Label(
            self.sync_img_button_frame,
            text=f"Sync Image #1",
            background=self.custom_frame_bg_colors["specialbg"],
            fg=self.custom_label_colors["foreground"],
            font=(self.set_font, self.set_font_size - 1),
        )
        self.sync_position.grid(row=0, column=0, sticky=W, padx=5, pady=(7, 0))

    def _apply_sync(self):
        offset = 0
        operator = None
        reference_frame_number = re.search(
            r".+__(\d+).png", str(pathlib.Path(self._locate_sync_img_encode(1)).name)
        )
        find_frame_offset = re.search(
            r".+__(\d+).png",
            str(pathlib.Path(self.sync_images1[self.sync_img_select]).name),
        )

        if int(reference_frame_number.group(1)) > int(find_frame_offset.group(1)):
            offset = int(reference_frame_number.group(1)) - int(
                find_frame_offset.group(1)
            )
            operator = "-"
        elif int(reference_frame_number.group(1)) < int(find_frame_offset.group(1)):
            offset = int(
                find_frame_offset.group(1) - int(reference_frame_number.group(1))
            )
            operator = "+"

        self.return_output.update(
            {"synced": False, "images": None, "offset": offset, "operator": operator}
        )
        self.image_viewer.destroy()

    def _generate_sync_images1(self):
        sync_img_list = sorted(
            [
                x_img
                for x_img in pathlib.Path(
                    pathlib.Path(self.screenshot_sync_var) / "sync1"
                ).glob("*.png")
            ]
        )

        # get encode image
        for sync_images in sync_img_list:
            self.sync_images1.append(
                pathlib.Path(
                    pathlib.Path(self.screenshot_sync_var)
                    / "sync1"
                    / pathlib.Path(sync_images).name
                )
            )

    def _generate_sync_images2(self):
        sync_img_list = sorted(
            [
                x_img
                for x_img in pathlib.Path(
                    pathlib.Path(self.screenshot_sync_var) / "sync2"
                ).glob("*.png")
            ]
        )

        # get encode image
        for sync_images in sync_img_list:
            self.sync_images2.append(
                pathlib.Path(
                    pathlib.Path(self.screenshot_sync_var)
                    / "sync2"
                    / pathlib.Path(sync_images).name
                )
            )

    def _select_next_sync_image(self):
        if self.sync_img_select < len(self.sync_images1) - 1:
            self.sync_img_select += 1
            self.rf1_sync_image = self.sync_images1[self.sync_img_select]
            self.rf2_sync_image = self.sync_images2[self.sync_img_select]
            try:
                self.sync_position.config(text=f"Sync Image #{self.sync_img_select}")
            except AttributeError:
                pass

    def _select_back_sync_image(self):
        if self.sync_img_select > 1:
            self.sync_img_select -= 1
            self.rf1_sync_image = self.sync_images1[self.sync_img_select]
            self.rf2_sync_image = self.sync_images2[self.sync_img_select]
            try:
                self.sync_position.config(text=f"Sync Image #{self.sync_img_select}")
            except AttributeError:
                pass

    def _image_swap1(self, _):
        self.rf1_s_image = Image.open(self.rf1_sync_image)
        self.rf1_s_image.thumbnail((1000, 562), Image.LANCZOS)
        self.resized_rf1_s_image = ImageTk.PhotoImage(self.rf1_s_image)

        self.image_sync_label1.config(image=self.resized_rf1_s_image)
        self.image_sync_label1.image = self.resized_rf1_s_image

    def _image_swap_out1(self, _):
        self.image_sync_label1.config(image=self.resized_rf1_image)
        self.image_sync_label1.image = self.resized_rf1_image

    def _image_swap2(self, _):
        self.rf2_image = Image.open(self.rf2_sync_image)
        self.rf2_image.thumbnail((1000, 562), Image.LANCZOS)
        self.resized_rf2_s_image = ImageTk.PhotoImage(self.rf2_image)

        self.image_sync_label2.config(image=self.resized_rf2_s_image)
        self.image_sync_label2.image = self.resized_rf2_s_image

    def _image_swap_out2(self, _):
        self.image_sync_label2.config(image=self.resized_rf2_image)
        self.image_sync_label2.image = self.resized_rf2_image

    def _locate_sync_img_encode(self, ref_num):
        # create image list
        sync_img_list = sorted(
            [x_img for x_img in pathlib.Path(self.screenshot_sync_var).glob("*.png")]
        )

        # get encode image
        for sync_images in sync_img_list:
            sync_img = re.search(rf"0{str(ref_num)}b_encode_.+", str(sync_images))
            if sync_img:
                return pathlib.Path(
                    pathlib.Path(self.screenshot_sync_var) / sync_img.group()
                )

    def get_dict(self):
        return self.return_output
