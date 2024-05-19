class dglab_message:
    def __init__(self, type_, clientId, targetId, message):
        self.type_ = type_
        self.clientId = clientId
        self.targetId = targetId
        self.message = message