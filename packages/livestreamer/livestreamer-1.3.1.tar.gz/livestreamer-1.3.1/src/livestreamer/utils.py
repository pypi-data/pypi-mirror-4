from .compat import is_win32
from .plugins import PluginError

import argparse
import hashlib
import hmac
import os
import requests
import tempfile
import zlib

if is_win32:
    from ctypes import windll, cast, c_ulong, c_void_p, byref

SWFKey = b"Genuine Adobe Flash Player 001"
RequestsConfig = { "danger_mode": True }

class ArgumentParser(argparse.ArgumentParser):
    def convert_arg_line_to_args(self, line):
        if len(line) == 0:
            return

        if line[0] == "#":
            return

        split = line.find("=")
        if split > 0:
            key = line[:split].strip()
            val = line[split+1:].strip()
            yield "--%s=%s" % (key, val)
        else:
            yield "--%s" % line

class NamedPipe(object):
    def __init__(self, name):
        self.fifo = None
        self.pipe = None

        if is_win32:
            self.path = os.path.join("\\\\.\\pipe", name)
            self.pipe = self._create_named_pipe(self.path)
        else:
            self.path = os.path.join(tempfile.gettempdir(), name)
            self._create_fifo(self.path)

    def _create_fifo(self, name):
        os.mkfifo(name, 0o660)

    def _create_named_pipe(self, path):
        PIPE_ACCESS_OUTBOUND = 0x00000002
        PIPE_TYPE_BYTE = 0x00000000
        PIPE_READMODE_BYTE = 0x00000000
        PIPE_WAIT = 0x00000000
        PIPE_UNLIMITED_INSTANCES = 255
        INVALID_HANDLE_VALUE = -1
        bufsize = 8192

        pipe = windll.kernel32.CreateNamedPipeA(path,
                                                PIPE_ACCESS_OUTBOUND,
                                                PIPE_TYPE_BYTE | PIPE_READMODE_BYTE | PIPE_WAIT,
                                                PIPE_UNLIMITED_INSTANCES,
                                                bufsize,
                                                bufsize,
                                                0,
                                                None)

        if pipe == INVALID_HANDLE_VALUE:
            raise IOError(("error code 0x{0:08X}").format(windll.kernel32.GetLastError()))

        return pipe

    def open(self, mode):
        if not self.pipe:
            self.fifo = open(self.path, mode)

    def write(self, data):
        if self.pipe:
            windll.kernel32.ConnectNamedPipe(self.pipe, None)
            written = c_ulong(0)
            windll.kernel32.WriteFile(self.pipe, cast(data, c_void_p),
                                      len(data), byref(written),
                                      None)
            return written
        else:
            return self.fifo.write(data)

    def close(self):
        if self.pipe:
            windll.kernel32.DisconnectNamedPipe(self.pipe)
        else:
            os.unlink(self.path)

def urlopen(url, method="get", exception=PluginError, **args):
    if "data" in args and args["data"] is not None:
        method = "post"

    try:
        res = requests.request(method, url, config=RequestsConfig, timeout=15, **args)
    except (requests.exceptions.RequestException, IOError) as err:
        raise exception(("Unable to open URL: {url} ({err})").format(url=url, err=str(err)))

    return res

def urlget(url, prefetch=True, **args):
    return urlopen(url, method="get", prefetch=prefetch,
                   **args)

def swfverify(url):
    res = urlopen(url)
    swf = res.content

    if swf[:3] == b"CWS":
        swf = b"F" + swf[1:8] + zlib.decompress(swf[8:])

    h = hmac.new(SWFKey, swf, hashlib.sha256)

    return h.hexdigest(), len(swf)

def verifyjson(json, key):
    if not key in json:
        raise PluginError(("Missing '{0}' key in JSON").format(key))

    return json[key]

__all__ = ["ArgumentParser", "urlopen", "urlget", "swfverify", "verifyjson"]
