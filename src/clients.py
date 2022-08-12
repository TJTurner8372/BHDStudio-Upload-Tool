from torf import Torrent
import xmlrpc.client
import bencode
import os
import base64
import errno
import asyncio
import ssl
import shutil

class Clients():
    """
    Used to add torrents to client
    """
    