from configparser import ConfigParser

# define config file and settings
config_file = "runtime/config.ini"  # Creates (if it doesn't exist) and defines location of config.ini
config = ConfigParser()
config.read(config_file)

# torrent settings
if not config.has_section("torrent_settings"):
    config.add_section("torrent_settings")
if not config.has_option("torrent_settings", "tracker_url"):
    config.set("torrent_settings", "tracker_url", "")
if not config.has_option("torrent_settings", "default_path"):
    config.set("torrent_settings", "default_path", "")

# qbit client settings
if not config.has_section("qbit_client"):
    config.add_section("qbit_client")
if not config.has_option("qbit_client", "qbit_injection_toggle"):
    config.set("qbit_client", "qbit_injection_toggle", "false")
if not config.has_option("qbit_client", "qbit_url"):
    config.set("qbit_client", "qbit_url", "localhost")
if not config.has_option("qbit_client", "qbit_port"):
    config.set("qbit_client", "qbit_port", "8080")
if not config.has_option("qbit_client", "qbit_user"):
    config.set("qbit_client", "qbit_user", "admin")
if not config.has_option("qbit_client", "qbit_password"):
    config.set("qbit_client", "qbit_password", "password")
if not config.has_option("qbit_client", "qbit_category"):
    config.set("qbit_client", "qbit_category", "")

# deluge client settings
if not config.has_section("deluge_client"):
    config.add_section("deluge_client")
if not config.has_option("deluge_client", "deluge_injection_toggle"):
    config.set("deluge_client", "deluge_injection_toggle", "false")
if not config.has_option("deluge_client", "deluge_url"):
    config.set("deluge_client", "deluge_url", "127.0.0.1")
if not config.has_option("deluge_client", "deluge_daemon_port"):
    config.set("deluge_client", "deluge_daemon_port", "58846")
if not config.has_option("deluge_client", "deluge_user"):
    config.set("deluge_client", "deluge_user", "")
if not config.has_option("deluge_client", "deluge_password"):
    config.set("deluge_client", "deluge_password", "")
if not config.has_option("deluge_client", "deluge_remote_path"):
    config.set("deluge_client", "deluge_remote_path", "")

# encoder name
if not config.has_section("encoder_name"):
    config.add_section("encoder_name")
if not config.has_option("encoder_name", "name"):
    config.set("encoder_name", "name", "")

# bhd upload api
if not config.has_section("bhd_upload_api"):
    config.add_section("bhd_upload_api")
if not config.has_option("bhd_upload_api", "key"):
    config.set("bhd_upload_api", "key", "")

# live release
if not config.has_section("live_release"):
    config.add_section("live_release")
if not config.has_option("live_release", "password"):
    config.set("live_release", "password", "")
if not config.has_option("live_release", "value"):
    config.set("live_release", "value", "")

# nfo font
if not config.has_section("nfo_pad_font_settings"):
    config.add_section("nfo_pad_font_settings")
if not config.has_option("nfo_pad_font_settings", "font"):
    config.set("nfo_pad_font_settings", "font", "")
if not config.has_option("nfo_pad_font_settings", "style"):
    config.set("nfo_pad_font_settings", "style", "")
if not config.has_option("nfo_pad_font_settings", "size"):
    config.set("nfo_pad_font_settings", "size", "")

# # nfo color scheme
if not config.has_section("nfo_pad_color_settings"):
    config.add_section("nfo_pad_color_settings")
if not config.has_option("nfo_pad_color_settings", "text"):
    config.set("nfo_pad_color_settings", "text", "")
if not config.has_option("nfo_pad_color_settings", "background"):
    config.set("nfo_pad_color_settings", "background", "")

# check for updates
if not config.has_section("check_for_updates"):
    config.add_section("check_for_updates")
if not config.has_option("check_for_updates", "value"):
    config.set("check_for_updates", "value", "True")
if not config.has_option("check_for_updates", "ignore_version"):
    config.set("check_for_updates", "ignore_version", "")

# window location settings
if not config.has_section("save_window_locations"):
    config.add_section("save_window_locations")
if not config.has_option("save_window_locations", "bhdstudiotool"):
    config.set("save_window_locations", "bhdstudiotool", "")
if not config.has_option("save_window_locations", "torrent_window"):
    config.set("save_window_locations", "torrent_window", "")
if not config.has_option("save_window_locations", "nfo_pad"):
    config.set("save_window_locations", "nfo_pad", "")
if not config.has_option("save_window_locations", "uploader"):
    config.set("save_window_locations", "uploader", "")
if not config.has_option("save_window_locations", "movie_info"):
    config.set("save_window_locations", "movie_info", "")
if not config.has_option("save_window_locations", "about_window"):
    config.set("save_window_locations", "about_window", "")
if not config.has_option("save_window_locations", "image_viewer"):
    config.set("save_window_locations", "image_viewer", "")

# screenshot settings
if not config.has_section("screenshot_settings"):
    config.add_section("screenshot_settings")
if not config.has_option("screenshot_settings", "semi_auto_count"):
    config.set("screenshot_settings", "semi_auto_count", "")

# last used folder
if not config.has_section("last_used_folder"):
    config.add_section("last_used_folder")
if not config.has_option("last_used_folder", "path"):
    config.set("last_used_folder", "path", "")

# themes
if not config.has_section("themes"):
    config.add_section("themes")
if not config.has_option("themes", "selected_theme"):
    config.set("themes", "selected_theme", "bhd_theme")

# write options to config if they do not exist
with open(config_file, "w") as configfile:
    config.write(configfile)
