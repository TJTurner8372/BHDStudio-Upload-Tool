import base64
import pathlib
import socket
from configparser import ConfigParser

import deluge_client.client
import qbittorrentapi
import torf
from deluge_client import DelugeRPCClient


class Clients:
    """
    Used to add torrents to client
    """

    def __init__(self):
        """define config"""
        self.client_config = ConfigParser()
        self.client_config.read("runtime/config.ini")

    def qbittorrent(self, encode_file_path, torrent_file_path):
        """injection into qBittorrent via webui"""
        qbt_client = qbittorrentapi.Client(
            host=self.client_config["qbit_client"]["qbit_url"],
            port=self.client_config["qbit_client"]["qbit_port"],
            username=self.client_config["qbit_client"]["qbit_user"],
            password=self.client_config["qbit_client"]["qbit_password"],
        )

        # check if qBittorrent login works
        try:
            qbt_client.auth_log_in(requests_args={"timeout": 0.35})
        except qbittorrentapi.LoginFailed:
            return "Injection failed...\n\nCheck username and password and try again"
        except qbittorrentapi.exceptions.APIConnectionError:
            return (
                "qBittorrent is not detected. Ensure that it's running and try again.\n\nIf qBittorrent is "
                "running check host and port"
            )

        # change variables around depending on local vs remote injection
        if (
            self.client_config["qbit_client"]["qbit_url"] == "localhost"
            or self.client_config["qbit_client"]["qbit_url"] == "127.0.0.1"
        ):
            category_var = None
            save_path_var = pathlib.Path(encode_file_path).parent
            auto_management_var = False
        else:
            category_var = self.client_config["qbit_client"]["qbit_category"]
            save_path_var = None
            auto_management_var = True

        # add torrent file to qBittorrent
        try:
            add_torrent = qbt_client.torrents_add(
                torrent_files=torrent_file_path,
                save_path=save_path_var,
                use_auto_torrent_management=auto_management_var,
                is_skip_checking=True,
                category=category_var,
            )
        except qbittorrentapi.exceptions.APIConnectionError:
            raise ValueError(
                "There was an error adding torrent file to qBittorrent via WebUI"
            )

        if add_torrent == "Ok.":
            return "qBittorrent torrent injection successful!"
        elif add_torrent == "Fails.":
            return "qBittorrent torrent injection was not successful"

    @staticmethod
    def qbittorrent_test(host, port, username, password):
        """method to check qBittorrent's login settings"""
        qbt_client = qbittorrentapi.Client(
            host=host,
            port=port,
            username=username,
            password=password,
        )

        # check if qBittorrent login works
        try:
            qbt_client.auth_log_in(requests_args={"timeout": 0.35})
            return "Successful!\n\nAs long as category is setup correctly automatic injection will work!"
        except qbittorrentapi.LoginFailed as e:
            return "Injection failed...\n\nCheck username and password and try again"
        except qbittorrentapi.exceptions.APIConnectionError:
            return (
                "qBittorrent is not detected. Ensure that it's running and try again.\n\nIf qBittorrent is "
                "running check host and port"
            )

    def deluge(self, torrent_file_path):
        """injection for Deluge via WebUI"""
        deluge_client_inj = DelugeRPCClient(
            host=self.client_config["deluge_client"]["deluge_url"],
            port=int(self.client_config["deluge_client"]["deluge_daemon_port"]),
            username=self.client_config["deluge_client"]["deluge_user"],
            password=self.client_config["deluge_client"]["deluge_password"],
        )

        # connect to deluge client
        try:
            deluge_client_inj.connect()

            # if deluge_client does not return connected
            if not deluge_client_inj.connected:
                return (
                    "Failed to connect...\n\nEnsure that you followed all the steps to get it "
                    "working, if you have done so it's likely your host, port, username, and/or "
                    "password is incorrect"
                )

        # error returned if deluge can not be found
        except socket.timeout:
            return (
                "Could not access Deluge. This is likely due to host or port being incorrect, or "
                "Deluge/Deluge's daemon not running..."
            )

        # all other errors that deluge returns once connected
        except deluge_client.client.DelugeClientException as error:
            error_var = str(error)

            if "username does not exist" in error_var.lower():
                return "Username is incorrect"

            if "password does not match" in error_var.lower():
                return "Incorrect password"

        # if connected continue with injection
        if deluge_client_inj.connected:

            # create torrent instance to get torrent attributes
            read_torrent = torf.Torrent.read(torrent_file_path)

            # set injected torrent name to a variable
            injected_torrent_name = read_torrent.name

            # inject torrent name to client with specified settings
            try:
                deluge_client_inj.call(
                    "core.add_torrent_file",
                    torrent_file_path,
                    base64.b64encode(read_torrent.dump()),
                    {
                        "download_location": self.client_config["deluge_client"][
                            "deluge_remote_path"
                        ],
                        "seed_mode": True,
                    },
                )

            # deluge's api is awful, so catch all errors and raise a value error
            except deluge_client_inj.DelugeClientException as error:
                return f"Could not inject torrent to client...\nError:\n{error}"

            # parse client for torrent names
            parse_client = deluge_client_inj.call(
                "core.get_torrents_status", {}, ["name"]
            )

            # check if injected torrent is in the torrent names parse_client
            for x in parse_client.values():
                name_values = list(x.values())[0].decode("utf-8")
                if injected_torrent_name == name_values:
                    return "Successfully injected into Deluge!"

        # if connected fails
        else:
            return "Unable to access Deluge client"

    @staticmethod
    def deluge_test(host, port, username, password):
        """method to check Deluge login settings"""
        deluge_client_inj = DelugeRPCClient(
            host=host,
            port=int(port),
            username=username,
            password=password,
        )

        # connect to deluge client
        try:
            deluge_client_inj.connect()

            # if deluge_client does not return connected
            if not deluge_client_inj.connected:
                return (
                    "Failed to connect...\n\nEnsure that you followed all the steps to get it "
                    "working, if you have done so it's likely your host, port, username, and/or "
                    "password is incorrect"
                )

                # error returned if deluge can not be found
        except socket.timeout:
            return (
                "Could not access Deluge. This is likely due to host or port being incorrect, or "
                "Deluge/Deluge's daemon not running..."
            )

            # all other errors that deluge returns once connected
        except deluge_client.client.DelugeClientException as error:
            error_var = str(error)

            if "username does not exist" in error_var.lower():
                return "Username is incorrect"

            if "password does not match" in error_var.lower():
                return "Incorrect password"

        # if login passes all checks
        if deluge_client_inj.connected:
            return (
                "Connected to client!\n\nAs long as 'Save Directory' is configured correctly "
                "your torrent will inject automatically"
            )
