from flask import Flask, request
from flask_socketio import SocketIO, emit
from uuid import uuid4
import json

app = Flask(__name__)
socketio = SocketIO(app)

# 储存已连接的用户及其标识
clients = {}

# 存储消息关系
relations = {}

punishment_duration = 5  # 默认发送时间1秒

punishment_time = 1  # 默认一秒发送1次

# 存储客户端和发送计时器关系
client_timers = {}

# 定义心跳消息
heartbeat_msg = {
    "type": "heartbeat",
    "clientId": "",
    "targetId": "",
    "message": "200"
}

@socketio.on('connect')
def handle_connect():
    # 生成唯一的标识符
    client_id = str(uuid4())

    print('新的 WebSocket 连接已建立，标识符为:', client_id)

    # 存储
    clients[client_id] = request.sid

    # 发送标识符给客户端（格式固定，双方都必须获取才可以进行后续通信：比如浏览器和APP）
    emit('message', {'type': 'bind', 'clientId': client_id, 'message': 'targetId', 'targetId': ''})

@socketio.on('message')
def handle_message(message):
    print("收到消息：" + message)
    data = None
    try:
        data = json.loads(message)
    except json.JSONDecodeError:
        # 非JSON数据处理
        emit('message', {'type': 'msg', 'clientId': "", 'targetId': "", 'message': '403'})
        return

    # 非法消息来源拒绝
    if clients.get(data['clientId']) != request.sid and clients.get(data['targetId']) != request.sid:
        emit('message', {'type': 'msg', 'clientId': "", 'targetId': "", 'message': '404'})
        return

    if data.get('type') and data.get('clientId') and data.get('message') and data.get('targetId'):
        # 优先处理绑定关系
        if data['type'] == "bind":
            # 服务器下发绑定关系
            if data['clientId'] in clients and data['targetId'] in clients:
                # relations的双方都不存在这俩id
                if not any(id in relations or id in relations.values() for id in [data['clientId'], data['targetId']]):
                    relations[data['clientId']] = data['targetId']
                    emit('message', {'type': "bind", 'clientId': data['clientId'], 'targetId': data['targetId'], 'message': "200"}, room=clients[data['clientId']])
                    emit('message', {'type': "bind", 'clientId': data['clientId'], 'targetId': data['targetId'], 'message': "200"}, room=clients[data['targetId']])
                else:
                    emit('message', {'type': "bind", 'clientId': data['clientId'], 'targetId': data['targetId'], 'message': "400"}, room=clients[data['clientId']])
                    return
            else:
                emit('message', {'type': "bind", 'clientId': data['clientId'], 'targetId': data['targetId'], 'message': "401"}, room=clients[data['clientId']])
                return
        elif data['type'] in [1, 2, 3]:
            # 服务器下发APP强度调节
            if relations.get(data['clientId']) != data['targetId']:
                emit('message', {'type': "bind", 'clientId': data['clientId'], 'targetId': data['targetId'], 'message': "402"}, room=clients[data['clientId']])
                return
            if data['targetId'] in clients:
                send_type = data['type'] - 1
                send_channel = data.get('channel', 1)
                send_strength = data['strength'] if data['type'] >= 3 else 1  # 增加模式强度改成1
                msg = "strength-" + str(send_channel) + "+" + str(send_type) + "+" + str(send_strength)
                emit('message', {'type': "msg", 'clientId': data['clientId'], 'targetId': data['targetId'], 'message': msg}, room=clients[data['targetId']])
        elif data['type'] == 4:
            # 服务器下发指定APP强度
            if relations.get(data['clientId']) != data['targetId']:
                emit('message', {'type': "bind", 'clientId': data['clientId'], 'targetId': data['targetId'], 'message': "402"}, room=clients[data['clientId']])
                return
            if data['targetId'] in clients:
                emit('message', {'type': "msg", 'clientId': data['clientId'], 'targetId': data['targetId'], 'message': data['message']}, room=clients[data['targetId']])
        elif data['type'] == "clientMsg":
            # 服务端下发给客户端的消息
            if relations.get(data['clientId']) != data['targetId']:
                emit('message', {'type': "bind", 'clientId': data['clientId'], 'targetId': data['targetId'], 'message': "402"}, room=clients[data['clientId']])
                return
            if 'message2' not in data:
                emit('message', {'type': "error", 'clientId': data['clientId'], 'targetId': data['targetId'], 'message': "501"}, room=clients[data['clientId']])
                return
            if data['targetId'] in clients:
                send_time_a = data.get('time1', punishment_duration)
                send_time_b = data.get('time2', punishment_duration)
                target = clients[data['targetId']]  # 发送目标
                send_data_a = {'type': "msg", 'clientId': data['clientId'], 'targetId': data['targetId'], 'message': "pulse-" + data['message']}
                send_data_b = {'type': "msg", 'clientId': data['clientId'], 'targetId': data['targetId'], 'message': "pulse-" + data['message2']}
                total_sends_a = punishment_time * send_time_a
                total_sends_b = punishment_time * send_time_b
                time_space = 1000 / punishment_time

                print("消息发送中，总消息数A：" + str(total_sends_a) + "总消息数B：" + str(total_sends_b) + "持续时间A：" + str(send_time_a) + "持续时间B：" + str(send_time_b))
                if data['clientId'] in client_timers:
                    # 计时器尚未工作完毕, 清除计时器且发送清除APP队列消息，延迟150ms重新发送新数据
                    # 新消息覆盖旧消息逻辑
                    emit('message', "当前有正在发送的消息，覆盖之前的消息", room=clients[data['clientId']])

                    timer_id = client_timers[data['clientId']]
                    socketio.clear_timeout(timer_id)  # 清除定时器
                    del client_timers[data['clientId']]  # 清除 Map 中的对应项

                    # 发送APP波形队列清除指令
                    clear_data_a = {'clientId': data['clientId'], 'targetId': data['targetId'], 'message': "clear-1", 'type': "msg"}
                    clear_data_b = {'clientId': data['clientId'], 'targetId': data['targetId'], 'message': "clear-2", 'type': "msg"}
                    emit('message', clear_data_a, room=clients[data['targetId']])
                    emit('message', clear_data_b, room=clients[data['targetId']])
                    socketio.start_background_task(delay_send_msg, data['clientId'], request.sid, target, send_data_a, send_data_b, total_sends_a, total_sends_b, time_space)
                else:
                    # 不存在未发完的消息 直接发送
                    delay_send_msg(data['clientId'], request.sid, target, send_data_a, send_data_b, total_sends_a, total_sends_b, time_space)
        else:
            # 未定义的普通消息
            if relations.get(data['clientId']) != data['targetId']:
                emit('message', {'type': "bind", 'clientId': data['clientId'], 'targetId': data['targetId'], 'message': "402"}, room=clients[data['clientId']])
                return
            if data['clientId'] in clients:
                emit('message', {'type': data['type'], 'clientId': data['clientId'], 'targetId': data['targetId'], 'message': data['message']}, room=clients[data['clientId']])
            else:
                # 未找到匹配的客户端
                emit('message', {'clientId': data['clientId'], 'targetId': data['targetId'], 'message': "404", 'type': "msg"}, room=clients[data['clientId']])

@socketio.on('disconnect')
def handle_disconnect():
    # 连接关闭时，清除对应的 clientId 和 WebSocket 实例
    print('WebSocket 连接已关闭')
    # 遍历 clients Map，找到并删除对应的 clientId 条目
    for client_id, sid in clients.items():
        if sid == request.sid:
            # 拿到断开的客户端id
            print("断开的client id:" + client_id)
            if client_id in relations:
                # 网页断开 通知app
                app_id = relations[client_id]
                socketio.emit('message', {'type': "break", 'clientId': client_id, 'targetId': app_id, 'message': "209"}, room=sid)
                socketio.disconnect(app_id)
                del relations[client_id]  # 清除关系
                print("对方掉线，关闭" + app_id)
            elif client_id in relations.values():
                # app断开 通知网页
                web_sid = clients[client_id]
                socketio.emit('message', {'type': "break", 'clientId': client_id, 'targetId': client_id, 'message': "209"}, room=web_sid)
                socketio.disconnect(web_sid)
                del relations[client_id]  # 清除关系
                print("对方掉线，关闭" + client_id)
            del clients[client_id]  # 清除ws客户端
            print("已清除" + client_id + " ,当前size: " + str(len(clients)))

@socketio.on_error_default
def handle_error(e):
    # 错误处理
    print('WebSocket 异常:', str(e))
    # 在此通知用户异常，通过 WebSocket 发送消息给双方
    client_id = None
    # 查找当前 WebSocket 实例对应的 clientId
    for cid, sid in clients.items():
        if sid == request.sid:
            client_id = cid
            break
    if not client_id:
        print('无法找到对应的 clientId')
        return
    # 构造错误消息
    error_message = 'WebSocket 异常: ' + str(e)

    for cid, aid in relations.items():
        # 遍历关系 Map，找到并通知没掉线的那一方
        if cid == client_id:
            # 通知app
            socketio.emit('message', {'type': "error", 'clientId': client_id, 'targetId': aid, 'message': "500"}, room=clients[cid])
        if aid == client_id:
            # 通知网页
            socketio.emit('message', {'type': "error", 'clientId': cid, 'targetId': client_id, 'message': error_message}, room=clients[cid])

def delay_send_msg(client_id, sid, target, send_data_a, send_data_b, total_sends_a, total_sends_b, time_space):
    # 发信计时器 AB通道会分别发送不同的消息和不同的数量 必须等全部发送完才会取消这个消息 新消息可以覆盖旧消息
    target.emit('message', send_data_a)  # 立即发送一次AB通道的消息
    target.emit('message', send_data_b)
    total_sends_a -= 1
    total_sends_b -= 1
    if total_sends_a > 0 or total_sends_b > 0:
        # 按频率发送消息给特定的客户端
        def send_messages():
            nonlocal total_sends_a, total_sends_b
            if total_sends_a > 0:
                target.emit('message', send_data_a)
                total_sends_a -= 1
            if total_sends_b > 0:
                target.emit('message', send_data_b)
                total_sends_b -= 1
            # 如果达到发送次数上限，则停止定时器
            if total_sends_a <= 0 and total_sends_b <= 0:
                socketio.emit('message', "发送完毕", room=sid)
                del client_timers[client_id]  # 删除对应的定时器

        # 使用 eventlet 提供的延迟函数
        socketio.start_background_task(send_messages)
        socketio.sleep(time_space / 1000)  # 每隔频率倒数触发一次定时器

if __name__ == '__main__':
    socketio.run(app, debug=True)
