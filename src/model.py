class dglab_message:
    def __init__(self, type_: str, clientId: str, targetId: str, message: str):
        self.type_ = type_
        self.clientId = clientId
        self.targetId = targetId
        self.message = message

class local_data:
    def __init__(self, clientId: str):
        self.clientId = clientId
        self.targetId = None
        self.limitA = 200
        self.limitB = 200
        self.limitAInit = 0
        self.limitBInit = 0
        self.channelAStrength = 0
        self.channelBStrength = 0
        self.channelAWave = []
        self.channelBWave = []

code = {
    200: ("Heartbeat received", True),
    209: ("对方客户端已断开", False),
    210: ("二维码中没有有效的clientID", False),
    211: ("socket连接上了，但服务器迟迟不下发app端的id来绑定", False),
    400: ("此id已被其他客户端绑定关系", False),
    401: ("要绑定的目标客户端不存在", False),
    402: ("收信方和寄信方不是绑定关系", False),
    403: ("发送的内容不是标准json对象", False),
    404: ("未找到收信人（离线）", False),
    405: ("下发的message长度大于1950", False),
    500: ("服务器内部异常", False)
}