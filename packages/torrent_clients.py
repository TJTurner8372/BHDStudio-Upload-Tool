import qbittorrentapi
import pathlib
from configparser import ConfigParser


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

        # add torrent file to qBittorrent
        try:
            add_torrent = qbt_client.torrents_add(
                torrent_files=torrent_file_path,
                save_path=pathlib.Path(encode_file_path).parent,
                use_auto_torrent_management=False,
                is_skip_checking=True,
                content_layout="Original",
            )
        except qbittorrentapi.exceptions.APIConnectionError:
            raise ValueError(
                "There was an error adding torrent file to qBittorrent via WebUI"
            )

        if add_torrent == "Ok.":
            return "qBittorrent torrent injection successful!"
        elif add_torrent == "Fails.":
            return "qBittorrent torrent injection was not successful"
