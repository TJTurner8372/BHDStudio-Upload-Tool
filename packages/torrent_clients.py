import qbittorrentapi
import pathlib
from configparser import ConfigParser
from subprocess import Popen as subprocess_Popen
from subprocess import CREATE_NO_WINDOW


class Clients:
    """
    Used to add torrents to client
    """

    def __init__(self):
        """define config"""
        self.client_config = ConfigParser()
        self.client_config.read("runtime/config.ini")

    def qbittorrent(self, encode_file_path, torrent_file_path):
        """check qBittorrent client injection type"""
        print(self.client_config["qbit_client"]["qbit_injection_type"])
        if self.client_config["qbit_client"]["qbit_injection_type"] == "cli":
            self.qbittorrent_cli(
                encode_file_path=encode_file_path, torrent_file_path=torrent_file_path
            )
        elif self.client_config["qbit_client"]["qbit_injection_type"] == "webui":
            self.qbittorrent_webui(
                encode_file_path=encode_file_path, torrent_file_path=torrent_file_path
            )

    def qbittorrent_webui(self, encode_file_path, torrent_file_path):
        # qBittorrent client instance
        qbt_client = qbittorrentapi.Client(
            host=self.client_config["qbit_url"],
            port=self.client_config["qbit_port"],
            username=self.client_config["qbit_user"],
            password=self.client_config["qbit_pass"],
        )
        # console.print("[bold yellow]Adding and rechecking torrent")
        try:
            qbt_client.auth_log_in()
        except qbittorrentapi.LoginFailed:
            # console.print("[bold red]INCORRECT QBIT LOGIN CREDENTIALS")
            return
        qbt_client.torrents_add(
            torrent_files=torrent_file_path.dump(),
            save_path=pathlib.Path(encode_file_path).parent,
            use_auto_torrent_management=False,
            is_skip_checking=True,
            content_layout="Original",
        )
        qbt_client.torrents_resume(torrent_file_path.infohash)
        # if client.get('qbit_tag', None) != None:
        # qbt_client.torrents_add_tags(tags=client.get('qbit_tag'), torrent_hashes=torrent.infohash)

    def qbittorrent_cli(self, encode_file_path, torrent_file_path):
        """qbittorrent cli injection mode"""

        # check if skip_check is true or false
        if self.client_config["qbit_client"]["qbit_cli_skip_check"] == "true":
            skip_hash = "--skip-hash-check "
        elif self.client_config["qbit_client"]["qbit_cli_skip_check"] == "false":
            skip_hash = ""

        # create command to be sent to subprocess_run
        cli_command = (
            f'"{self.client_config["qbit_client"]["qbit_path"]}" --skip-dialog=true --no-splash '
            f'--save-path="{str(pathlib.Path(encode_file_path).parent)}" '
            f'{skip_hash}--add-paused={self.client_config["qbit_client"]["qbit_cli_paused"]} '
            f'"{str(pathlib.Path(torrent_file_path))}"'
        )

        # run the command with subprocess Popen
        subprocess_Popen(cli_command, creationflags=CREATE_NO_WINDOW)
