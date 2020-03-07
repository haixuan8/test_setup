# -*- coding:utf-8 -*-
import json
from flask import Flask, request
from database import Database_test
from configparser import ConfigParser

cp = ConfigParser()
cp.read("bms.ini")

app = Flask(__name__)


@app.route('/bms/v1/task/pxe/notify', methods=['POST'])
def notify():
    data = request.get_data()
    json_data = json.loads(data)
    mac = str(json_data[0]["mac"])
    ipaddress = str(json_data[0]["ipaddress"])
    ipmi_ip = str(json_data[0]["ipmi_ip"])
    print("mac:%s  ip:%s" % (mac, ipaddress))

    with Database_test() as data_t:
        taskuuid = data_t.select_info('create_bms', 'create_id', ipmi_ip=ipmi_ip)
        if taskuuid:
            data_t.update_info(ipaddress, attr="dhcp_ip", pk=taskuuid[0])
            data_t.update_info(mac.upper(), attr="dhcp_mac", pk=taskuuid[0])
        else:
            try:
                data_t.insert_dhcpinfo(ipmi_ip, ipaddress, mac)
            except:
                pass
    return json.dumps({"success": True, "error": ""})


@app.route('/task/callback', methods=['POST'])
def callback():
    taskuuid = request.headers['Taskuuid']
    step = request.headers["Step"]
    data = request.get_json()
    state = "success" if data.get("success", None) else "failed"

    if len(taskuuid) > 5:
        with Database_test() as data_t:
            data_t.update_create_bms(step, state, taskuuid)

    return json.dumps({"success": True, "error": ""})


def database_create():
    with Database_test() as data_t:
        data_t.create()
        data_t.create_host()
        data_t.create_dhcpinfo()
        data_t.create_host_conf()


if __name__ == '__main__':
    database_create()
    app.run(host=cp.get("rest", "rest_service"), port=cp.get("rest", "rest_service_port"), threaded=True)
