import json
import os
import time
from flask import Flask, request
from DataBase import Database_test

app = Flask(__name__)

@app.route('/bms/v1/task/pxe/notify', methods=['POST'])
def notify():
    data = request.get_data()
    json_data = json.loads(data)
    mac = str(json_data[0]["mac"])
    ipaddress = str(json_data[0]["ipaddress"])
    print("mac:%s  ip:%s" % (mac, ipaddress))

    with Database_test() as data_t:
        result = data_t.select_mac(mac)
        if result:
            taskuuid = data_t.select_create_id(result[0])
            data_t.update_create_bms("dhcp_ip", ipaddress,taskuuid[0])
        else:
            data_t.insert_dhcpinfo(ipaddress, mac)

    with open("/tmp/notify", "w") as f:
        f.write("%s %s" % (mac, ipaddress))

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

    with open("/tmp/callback", "w") as f:
        f.write(state)

    return json.dumps({"success": True, "error": ""})

def get_pid():
    pid = os.getpid()
    with open("/tmp/pidfile", "w") as fp:
        fp.write(str(pid))
        time.sleep(1)

def database_create():
    with Database_test() as data_t:
        data_t.create()
        data_t.create_host()
        data_t.create_dhcpinfo()

if __name__ == '__main__':
    get_pid()
    database_create()
    app.run(host='13.13.13.33', port='7070')