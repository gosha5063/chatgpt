from secret_keys import yooKassaShop
import yookassa

yookassa.Configuration.account_id = yooKassaShop["shopID"]
yookassa.Configuration.secret_key = yooKassaShop["token"]

paymentData = {
    "amount": {
        "value": "250.00",
        "currency": "RUB"},
    "capture": True,
    "confirmation": {
        "type": "redirect",
        "return_url": "#"
    }}


def createPayment():
    payment = dict(yookassa.Payment.create(paymentData))
    paymentId = payment["id"]
    url = payment["confirmation"]["confirmation_url"]
    return paymentId, url


def paymentStatus(paymentId):
    payment = dict(yookassa.Payment.find_one(paymentId))
    return payment["status"]
