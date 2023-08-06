# Copyright 2013 tsuru-circus authors. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from circus.plugins import CircusPlugin
from circus.client import CircusClient
from zmq.eventloop import ioloop
from honcho.procfile import Procfile

import json
import os


class ProcfileWatcher(CircusPlugin):
    name = "procfile_watcher"

    def __init__(self, *args, **config):
        super(ProcfileWatcher, self).__init__(*args, **config)
        self.loop_rate = config.get("loop_rate", 60)  # in seconds
        self.procfile_path = config.get("app_path", "/home/application/current/Procfile")
        self.working_dir = config.get("working_dir", "/home/application/current")
        self.apprc = config.get("apprc", "/home/application/apprc")
        self.port = config.get("port", "8888")
        self.uid = config.get("uid", "ubuntu")
        self.stderr_stream = {"class": config.get("stderr_stream", "tsuru.stream.Stream")}
        self.stdout_stream = {"class": config.get("stdout_stream", "tsuru.stream.Stream")}
        self.period = ioloop.PeriodicCallback(self.look_after, self.loop_rate * 1000, self.loop)
        self.circus_client = CircusClient()

    def envs(self):
        environs = {}
        with open(self.apprc) as file:
            for line in file.readlines():
                if "export" in line:
                    line = line.replace("export ", "")
                    k, v = line.split("=")
                    v = v.replace("\n", "").replace('"', '')
                    environs[k] = v
        return environs

    def handle_init(self):
        self.period.start()

    def handle_stop(self):
        self.period.stop()

    def handle_recv(self, data):
        pass

    def add_watcher(self, name, cmd):
        env = {"port": self.port}
        env.update(self.envs())
        options = {
            "env": env,
            "copy_env": True,
            "working_dir": self.working_dir,
            "stderr_stream": self.stderr_stream,
            "stdout_stream": self.stdout_stream,
            "uid": self.uid,
        }
        self.circus_client.call(json.dumps({
            "command": "add",
            "properties": {
            "cmd":  cmd,
            "name": name,
            "args": [],
            "options": options,
            "start": True,
        }}))

    def remove_watcher(self, name):
        self.call("rm", name=name)

    def commands(self, procfile):
        cmds = set(self.call("status")["statuses"].keys())
        new_cmds = set(procfile.commands.keys())
        to_remove = cmds.difference(new_cmds)
        to_add = new_cmds.difference(cmds)
        return to_add, to_remove

    def look_after(self):
        if os.path.exists(self.procfile_path):
            with open(self.procfile_path) as file:
                procfile = Procfile(file.read())
                to_add, to_remove = self.commands(procfile)

                for name in to_remove:
                    self.remove_watcher(name)

                for name in to_add:
                    self.add_watcher(name=name, cmd=procfile.commands[name])
