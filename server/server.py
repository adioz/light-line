from tornado import ioloop, web
import json
from datetime import datetime

import logic
import auth
import config
import transacsion_listener
import c_lightning

from classes import UserExists


class HowMuchHandler(web.RequestHandler):
    def get(self):
        self.write("Hello, world")

    def post(self):
        data = json.loads(self.request.body)
        ride_code = data['ride_code']
        user_token = data['user_token']
        amount_to_pay, saved = logic.calculate_amount_and_saved(user_token, ride_code)
        payment_request = c_lightning.get_payment_request(amount_to_pay)
        data = {'success': True,
                'data': {'amount': amount_to_pay,
                         'saved': saved,
                         'payment_request': payment_request}
                }
        self.write(json.dumps(data))


class MainHandler(web.RequestHandler):
    def get(self):
        self.write("Hello, world")


class RegisterHandler(web.RequestHandler):
    def get(self):
        self.write("nothing here")

    def post(self):
        data = json.loads(self.request.body)
        try:
            success, token = auth.register_new_user(data['username'], data['password'])
            data = {'success': success, 'data': token}
        except UserExists as e:
            data = {'success': False, 'error': e},

        self.write(json.dumps(data))


class OnPaymentHandler(web.RequestHandler):
    def get(self):
        self.write("nothing here")

    def post(self):
        data = json.loads(self.request.body)
        transacsion_listener.on_payment_event(data)

        data = {'success': True,
                'data': data}
        self.write(json.dumps(data))


def make_app():
    return web.Application([
        # (r"/auth", AuthHandler),
        (r"/onpayment", OnPaymentHandler),
        (r"/register", RegisterHandler),
        (r"/howmuch", HowMuchHandler),
        (r"/", MainHandler),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    ioloop.IOLoop.current().start()