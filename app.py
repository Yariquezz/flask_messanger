from flask import Flask, request, Response
from config import Configuration, VIBER_TOKEN, WIT_TOKEN, TELEGRAM_TOKEN
from wit import Wit
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages import VideoMessage
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
from viberbot.api.viber_requests import ViberUnsubscribedRequest
import logging
import requests
import json


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

app = Flask(__name__)
app.config.from_object(Configuration)
client = Wit(WIT_TOKEN)
viber = Api(BotConfiguration(
    name='Yarique Pybot',
    avatar='',
    auth_token=VIBER_TOKEN
))
url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"


def wit(message):
    vit = client.message(
        msg=message
    )
    logger.debug("Wit response: %s" % vit)
    try:
        response = f"intent: {vit['intents'][0]['name']} \nconfidence: {vit['intents'][0]['confidence']}"
    except Exception as e:
        logger.warning("Error wit: %s" % e)
        response = "intent not identified"
    return response


def send_message(chat_id, text):
    if text:
        data = {
            'chat_id': chat_id,
            'text': text.encode('utf-8'),
            'disable_web_page_preview': 'true',
            'reply_markup': json.dumps(
                {
                    'inline_keyboard': [
                        [
                            {
                                'text': "Привет",
                                'callback_data': "Привет"
                            },
                            {
                                'text': "Пока",
                                'callback_data': "Пока"
                            }
                        ]
                    ]
                }
            ),
        }
    resp = requests.post(url, data=data)
    r = json.loads(resp.content)
    logger.debug("From telegram: %s" % r)
    return r['ok']


@app.route("/telegram/webhook", methods=["GET", "POST"])
def receive_update():
    if request.method == "POST":
        logger.debug("Got message from telegram: %s" % json.loads(request.data))
        try:
            chat_id = request.json["message"]["chat"]["id"]
            logger.debug("chat_id: %s" % chat_id)
            message = request.json["message"]["text"]
            logger.debug("message: %s" % message)
            response = wit(message)
            logger.debug("response: %s" % response)
            send_message(chat_id, response)
        except Exception as e:
            logger.warning("Error receive_update: %s" % e)

    return {"ok": True}


@app.route('/viber/webhook', methods=['POST'])
def incoming():
    logger.debug("received request. post data: {0}".format(request.get_data()))
    # every viber message is signed, you can verify the signature using this method
    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)

    # this library supplies a simple way to receive a request object
    viber_request = viber.parse_request(request.get_data())

    if isinstance(viber_request, ViberMessageRequest):
        message = viber_request.message
        response = wit(message.text)
        viber.send_messages(
            to=viber_request.sender.id,
            messages=[
                TextMessage(text=response)
            ]
        )
    elif isinstance(viber_request, ViberSubscribedRequest):
        viber.send_messages(viber_request.get_user.id, [
            TextMessage(text="thanks for subscribing!")
        ])
    elif isinstance(viber_request, ViberFailedRequest):
        logger.warning("client failed receiving message. failure: {0}".format(viber_request))

    return Response(status=200)


if __name__ == "__main__":
    app.run()
