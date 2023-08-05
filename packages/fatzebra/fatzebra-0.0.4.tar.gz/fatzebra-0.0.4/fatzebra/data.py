class Purchase(object):
    def __init__(self, data):
        self.id            = data["id"]
        self.authorization = data["authorization"]
        self.successful    = data["successful"]
        self.card_holder   = data["card_holder"]
        self.card_number   = data["card_number"]
        self.card_expiry   = data["card_expiry"]
        self.card_token    = data["card_token"]
        self.message       = data["message"]
        self.amount        = data["amount"]
        self.reference     = data["reference"]


class CreditCard(object):
    def __init__(self, data):
        self.token       = data["token"]
        self.card_number = data["card_number"]
        self.card_holder = data["card_holder"]
        self.expiry      = data["card_expiry"]


class Refund(object):
    def __init__(self, data):
        self.id             = data["id"]
        self.authorization  = data["authorization"]
        self.amount         = data["amount"]
        self.successful     = data["successful"]
        self.message        = data["message"]
