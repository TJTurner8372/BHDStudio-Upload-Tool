import qbittorrentapi
import pathlib
from configparser import ConfigParser
from deluge_client import DelugeRPCClient, client
import deluge_client
import torf
import base64


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

        # do a short time out login session to see if qBittorrent is running
        try:
            qbt_client.auth_log_in(requests_args={"timeout": 0.35})
        except qbittorrentapi.exceptions.APIConnectionError:
            return (
                "Injection failed:\nqBittorrent is most likely not running\n\nIf qBittorrent was running check "
                "hostname, port, user and password before trying automatic injection again"
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

    def deluge(self):
        pass
