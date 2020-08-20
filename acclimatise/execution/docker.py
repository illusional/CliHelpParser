from typing import List

from docker.utils.socket import consume_socket_output, demux_adaptor, frames_iter


import errno
import os
from select import select as original_select
import select
import socket as pysocket
import struct

import six

from . import Executor

from unittest.mock import patch

def timeout_select(rlist, wlist, xlist):
    return original_select(rlist, wlist, xlist, 5)

class DockerExecutor(Executor):
    """
    An executor that runs the commands on an already-running docker Container (not an Image!)
    """

    def __init__(self, container: "docker.models.containers.Container"):
        self.container = container

    @staticmethod
    def frames(socket):
        with patch.object(select, 'select', new=timeout_select):
            for frame in frames_iter(socket, tty=False):
                yield demux_adaptor(*frame)

    def execute(self, command: List[str]) -> str:
        _, socket = self.container.exec_run(
            command, stdout=True, stderr=True, demux=True, socket=True
        )
        socket._sock.settimeout(5)

        stdout, stderr = consume_socket_output(self.frames(socket), demux=True)
        return (stdout or stderr).decode()
