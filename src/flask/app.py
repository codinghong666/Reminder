from flask import Flask, request, jsonify, make_response, render_template
import os
import sys

# 保证可以复用 src/main/datebase.py
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MAIN_DIR = os.path.join(BASE_DIR, 'main')
if MAIN_DIR not in sys.path:
    sys.path.insert(0, MAIN_DIR)

from datebase import iter_data, remove_data, init_database, insert_data  # noqa: E402
from datebase import get_next_message_id_for_group_1  # noqa: E402


app = Flask(__name__)
@app.route('/')
def home():
    return render_template('index.html')


# 简单 CORS（如需更严格控制可替换为 flask-cors）
@app.after_request
def add_cors_headers(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET,DELETE,OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return resp


# 确保数据库表存在
init_database()


@app.route('/api/messages', methods=['GET', 'OPTIONS'])
def api_list_messages():
    if request.method == 'OPTIONS':
        return make_response('', 204)
    rows = iter_data()
    # rows: (id, group_id, message_id, message, time)
    data = [
        {
            'group_id': r[1],
            'message_id': r[2],
            'message': r[3],
            'time': r[4],
            'display': f"{r[4]}: {r[3]}",
        }
        for r in rows
    ]
    return jsonify({
        'count': len(data),
        'items': data,
    })


@app.route('/api/messages', methods=['DELETE', 'OPTIONS'])
def api_delete_message():
    if request.method == 'OPTIONS':
        return make_response('', 204)
    payload = request.get_json(silent=True) or {}
    group_id = payload.get('group_id') or request.args.get('group_id', '')
    message_id = payload.get('message_id') or request.args.get('message_id', '')
    if not group_id or not message_id:
        return jsonify({'ok': False, 'error': 'group_id and message_id are required'}), 400
    remove_data(group_id, message_id)
    return jsonify({'ok': True})


@app.route('/api/messages', methods=['POST', 'OPTIONS'])
def api_create_message():
    if request.method == 'OPTIONS':
        return make_response('', 204)
    payload = request.get_json(silent=True) or {}
    # 固定 group_id='1'
    group_id = '1'
    message = (payload.get('message') or '').strip()
    time_str = (payload.get('time') or '').strip()
    if not message or not time_str:
        return jsonify({'ok': False, 'error': 'time and message are required'}), 400
    message_id = get_next_message_id_for_group_1()
    insert_data(group_id, message_id, message, time_str)
    return jsonify({'ok': True, 'group_id': group_id, 'message_id': message_id})


if __name__ == "__main__":
    # 绑定 0.0.0.0 方便外部访问，如需可改端口
    app.run(host="0.0.0.0", port=5000, debug=False)


