import time
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

robot_state = {
    "db": 42,
    "state": "NORMAL",      # Trạng thái hiện tại của lớp
    "voice_enabled": True,  # Lệnh bật/tắt giọng nói nhắc nhở từ xa
    "violations": 0,
    "last_seen": 0
}

@app.route("/")
def index():
    return render_template("index.html")

# ESP32-S3 gọi API này mỗi 0.5s để gửi mức dB, trạng thái và nhận lệnh từ web
@app.route("/api/robot", methods=["POST"])
def robot_sync():
    data = request.get_json(silent=True) or {}
    if "db" in data:
        robot_state["db"] = int(data["db"])
    if "state" in data:
        new_state = data["state"]
        if new_state != robot_state["state"]:
            robot_state["state"] = new_state
            if new_state in ("WARN1", "WARN2"):
                robot_state["violations"] += 1
    
    robot_state["last_seen"] = time.time()
    
    # Trả về lệnh cho chip: trạng thái hiện tại và cấu hình giọng nói từ web
    return jsonify({
        "state": robot_state["state"],
        "voice_enabled": robot_state["voice_enabled"]
    })

# Trình duyệt Web gọi để lấy thông tin hiển thị lên màn hình
@app.route("/api/status", methods=["GET"])
def web_status():
    is_online = (time.time() - robot_state["last_seen"]) < 5.0
    return jsonify({
        "db": robot_state["db"],
        "state": robot_state["state"],
        "violations": robot_state["violations"],
        "voice_enabled": robot_state["voice_enabled"],
        "online": is_online
    })

# Giáo viên bấm nút bật/tắt giọng nói nhắc nhở trên web
@app.route("/api/toggle-voice", methods=["POST"])
def toggle_voice():
    robot_state["voice_enabled"] = not robot_state["voice_enabled"]
    return jsonify({"voice_enabled": robot_state["voice_enabled"]})

@app.route("/api/reset", methods=["POST"])
def reset_counter():
    robot_state["violations"] = 0
    robot_state["state"] = "NORMAL"
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
