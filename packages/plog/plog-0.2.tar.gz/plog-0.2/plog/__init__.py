# Copyright 2013 Daniel Narvaez
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import queue
import subprocess
import threading


class LoggedProcess:
    def __init__(self, args, shell=False):
        self._args = args
        self._shell = shell

    def _stream_watcher(self, io_queue, name, stream):
        for line in iter(stream.readline, b""):
            io_queue.put((name, line))

        stream.close()

        io_queue.put((name, None))

    def _queue_logger(self, io_queue, stream_names):
        while len(stream_names) > 0:
            try:
                name, line = io_queue.get(True, 1)
            except queue.Empty:
                continue

            if line is None:
                stream_names.remove(name)
            else:
                logging.info(line.decode("utf-8")[:-1])

    def execute(self):
        process = subprocess.Popen(self._args,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   shell=self._shell)

        io_queue = queue.Queue()

        streams = {"stdout": process.stdout,
                   "stderr": process.stderr}

        for name, stream in streams.items():
            watcher = threading.Thread(target=self._stream_watcher,
                                       args=(io_queue, name, stream))
            watcher.start()

        logger = threading.Thread(target=self._queue_logger,
                                  args=(io_queue, list(streams.keys())))
        logger.start()

        try:
            process.wait()
        except KeyboardInterrupt:
            for name in streams.keys():
                io_queue.put((name, None))

        return process


def check_run(args, shell=False):
    returncode = run(args, shell)
    if returncode != 0:
        raise subprocess.CalledProcessError(returncode, args)


def run(args, shell=False):
    logging.info(args)

    logged_process = LoggedProcess(args, shell=shell)
    process = logged_process.execute()

    return process.returncode
