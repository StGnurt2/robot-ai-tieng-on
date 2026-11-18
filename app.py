import time
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

robot_state = {
    "db": 42,
    "cmd": "NORMAL",
    "last_seen": 0
}

@app.route("/")
def index():
    return render_template("index.html")

# ESP32-S3 gọi API này mỗi 0.5s để gửi mức dB và nhận lệnh mặt OLED / còi
@app.route("/api/robot", methods=["POST"])
def robot_sync():
    data = request.get_json(silent=True) or {}
    if "db" in data:
        robot_state["db"] = int(data["db"])
    robot_state["last_seen"] = time.time()
    return jsonify({"cmd": robot_state["cmd"]})

# Trình duyệt Web gọi để lấy mức dB & trạng thái Online của Robot
@app.route("/api/status", methods=["GET"])
def web_status():
    is_online = (time.time() - robot_state["last_seen"]) < 5.0
    return jsonify({
        "db": robot_state["db"],
        "cmd": robot_state["cmd"],
        "online": is_online
    })

# Trình duyệt Web gửi lệnh NORMAL / WARN1 / WARN2 xuống cho Robot
@app.route("/api/cmd", methods=["POST"])
def web_command():
    data = request.get_json(silent=True) or {}
    cmd = data.get("cmd", "NORMAL")
    if cmd in ("NORMAL", "WARN1", "WARN2"):
        robot_state["cmd"] = cmd
    return jsonify({"ok": True, "cmd": robot_state["cmd"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)