import datetime

import requests


async def test_build_and_deploy(ops_test):
    my_charm = await ops_test.build_charm(".")
    await ops_test.model.deploy(
        my_charm,
        resources={"node-image": "node:lts"},
        application_name="clock"
    )
    await ops_test.model.wait_for_idle(status="active")


async def test_add_ingress_relation(ops_test):
    await ops_test.model.deploy("nginx-ingress-integrator", "ingress")
    await ops_test.model.add_relation("clock", "ingress")
    await ops_test.model.wait_for_idle(status="active")


async def test_clock(ops_test):
    response = requests.get("http://127.0.0.1/", headers={"Host": "clock"})
    assert response.status_code == 200
    time = datetime.datetime.strptime(
        response.text.split("(")[0].strip(),
        "%a %b %d %Y %H:%M:%S GMT%z"
    )
    assert time.tzinfo == datetime.timezone.utc


async def test_update_config(ops_test):
    await ops_test.model.applications["clock"].set_config({
        "timezone": "Asia/Hong_Kong"
    })
    await ops_test.model.wait_for_idle()
    response = requests.get("http://127.0.0.1/", headers={"Host": "clock"})

    assert response.status_code == 200
    time = datetime.datetime.strptime(
        response.text.split("(")[0].strip(),
        "%a %b %d %Y %H:%M:%S GMT%z"
    )
    assert time.tzinfo.utcoffset(None) == datetime.timedelta(hours=8)
