from torf import Torrent

import qbittorrentapi

import os


class Clients():
    """
    Used to add torrents to client
    """
    def __init__(self, config):
        self.config = config
        pass

    def add_to_client(self, meta):
        if os.path.exists(meta["torrent_path"]):
            torrent = Torrent.read(meta["torrent_path"])
        else:
            return
        


    def qbittorrent(self, path, torrent):
        # infohash = torrent.infohash

        qbt_client = qbittorrentapi.Client(host=self.config["qbit_url"], port=self.config["qbit_port"], username=self.config["qbit_user"], password=self.config["qbit_pass"])
        #console.print("[bold yellow]Adding and rechecking torrent")
        try:
            qbt_client.auth_log_in()
        except qbittorrentapi.LoginFailed:
            #console.print("[bold red]INCORRECT QBIT LOGIN CREDENTIALS")
            return
        qbt_client.torrents_add(torrent_files=torrent.dump(), save_path=path, use_auto_torrent_management=False, is_skip_checking=True, content_layout='Original')
        qbt_client.torrents_resume(torrent.infohash)
        #if client.get('qbit_tag', None) != None:
        #    qbt_client.torrents_add_tags(tags=client.get('qbit_tag'), torrent_hashes=torrent.infohash)
        
        #console.print(f"Added to: {path}")