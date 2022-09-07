# Copyright 2022 Weii Wang
# See LICENSE file for licensing details.

import unittest

from charm import ClockK8SCharm
from ops.model import ActiveStatus
from ops.testing import Harness
import ops.testing

ops.testing.SIMULATE_CAN_CONNECT = True


class TestCharm(unittest.TestCase):
    def setUp(self):
        self.harness = Harness(ClockK8SCharm)
        self.addCleanup(self.harness.cleanup)

    def test_httpbin_pebble_ready(self):
        self.harness.begin()
        self.harness.set_can_connect("node", True)
        initial_plan = self.harness.get_container_pebble_plan("node")
        self.assertEqual(initial_plan.to_dict(), {})
        container = self.harness.model.unit.get_container("node")
        self.harness.charm.on.node_pebble_ready.emit(container)
        current_plan = self.harness.get_container_pebble_plan("node").to_dict()
        self.assertEqual(current_plan["services"]["node"]["environment"]["TZ"],
                         self.harness.charm._stored.timezone)
        service = self.harness.model.unit.get_container("node").get_service("node")
        self.assertTrue(service.is_running())
        self.assertEqual(self.harness.model.unit.status, ActiveStatus())

    def test_ingress_relations(self):
        ingress_relation_id = self.harness.add_relation("ingress", "ingress")
        self.harness.add_relation_unit(ingress_relation_id, "ingress/0")
        self.harness.set_leader()
        self.harness.begin_with_initial_hooks()
        ingress_data = self.harness.get_relation_data(ingress_relation_id, self.harness.charm.app)
        self.assertEqual(ingress_data["service-port"], "8080")
