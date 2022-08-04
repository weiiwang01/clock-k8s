#!/usr/bin/env python3
# Copyright 2022 Weii Wang
# See LICENSE file for licensing details.

import logging
import textwrap
import urllib.request

import ops.model
from ops.charm import CharmBase
from ops.framework import StoredState
from ops.main import main
from ops.model import ActiveStatus, WaitingStatus

logger = logging.getLogger(__name__)


class ClockK8SCharm(CharmBase):
    """Charm the service."""

    _stored = StoredState()

    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.node_pebble_ready, self._on_node_pebble_ready)
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on.get_time_action, self._on_get_time)
        self._stored.set_default(timezone="UTC")

    @staticmethod
    def _node_js_script() -> str:
        return textwrap.dedent("""\
        const http = require('http');
        const requestListener = function (req, res) {
          res.writeHead(200);
          res.end(new Date().toString());
        }
        const server = http.createServer(requestListener);
        server.listen(8080);
        """)

    def _pebble_layer(self):
        return {
            "summary": "clock server layer",
            "description": "clock server by node.js",
            "services": {
                "node": {
                    "override": "replace",
                    "summary": "clock server",
                    "command": "node /srv/clock/server.js",
                    "startup": "enabled",
                    "environment": {"TZ": self.model.config["timezone"]},
                }
            },
        }

    def _on_node_pebble_ready(self, event):
        """Inject the node js script into the container then start the service
        Injecting the script on-the-fly to save uploading a new image
        """
        container: ops.model.Container = event.workload
        pebble_layer = self._pebble_layer()
        container.push(path="/srv/clock/server.js",
                       source=self._node_js_script(),
                       encoding="utf-8",
                       make_dirs=True)
        container.add_layer("clock-server", pebble_layer, combine=True)
        container.autostart()
        self.unit.status = ActiveStatus()

    def _on_config_changed(self, event: ops.charm.ConfigChangedEvent):
        current_timezone = self._stored.timezone
        new_timezone = self.config["timezone"]
        if self._stored.timezone == self.config["timezone"]:
            return
        container = self.unit.get_container("node")
        if container.can_connect():
            logger.info(f"timezone changes from {current_timezone} to {new_timezone}")
            container.add_layer("clock-server", self._pebble_layer(), combine=True)
            container.replan()
            self.unit.status = ActiveStatus()
        else:
            event.defer()
            self.unit.status = WaitingStatus("waiting for Pebble in workload container")

    def _on_get_time(self, event: ops.charm.ActionEvent):
        try:
            with urllib.request.urlopen("http://localhost:8080", timeout=1) as f:
                event.set_results({"time": f.read().decode("utf-8")})
        except TimeoutError:
            event.fail("connection timeout")


if __name__ == "__main__":
    main(ClockK8SCharm)
