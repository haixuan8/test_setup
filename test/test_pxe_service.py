import json
import os
from flask import Flask, request



app = Flask(__name__)


@app.route('/v1/task/pxe/notify', methods=['POST'])
def notify():
    data = request.get_data()
    json_data = json.loads(data)
    json.dump(json_data, "/tmp/notify1")
    mac = str(json_data[0]["mac"])
    ipaddress = str(json_data[0]["ipaddress"])
    print("mac:%s  ip:%s" % (mac, ipaddress))
    with open("/tmp/notify", "w") as f:
        f.write(f.write("%s %s" % (mac, ipaddress)))
        pass
    return json.dumps({"success": True, "error": ""})

@app.route('/task/callback', methods=['POST'])
def callback():
    data = request.get_json()
    state = "success" if data.get("success", None) else "failed"
    with open("/tmp/callback", "w") as f:
        f.write(state)
        pass
    return json.dumps({"success": True, "error": ""})


def get_pid():
    pid = os.getpid()
    with open("/tmp/pidfile", "w") as fp:
        fp.write(pid)

if __name__ == '__main__':
    get_pid()
    app.run(host='13.13.13.33', port='7070')
