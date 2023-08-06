import argparse
from smssluzbacz_api.post import SmsGateApi


parser = argparse.ArgumentParser(description='Processes login, password and receiver telephone number')
parser.add_argument('login', metavar='login', type=str, help='sms.sluzba.cz login')
parser.add_argument('password', metavar='password', type=str, help='sms.sluzba.cz password')
parser.add_argument('tel_number', metavar='tel_number', type=str, help='number of SMS receiver')
parser.add_argument('--use-ssl', metavar='use_ssl', type=bool, help='whether to use ssl over HTTP', default=False,
                    required=False)
parser.add_argument('--timeout', metavar='timeout', type=float, help='http connection timeout', default=2,
                    required=False)
args = vars(parser.parse_args())

api = SmsGateApi(args['login'], args['password'], args['timeout'], args['use_ssl'])
api.send(args['tel_number'], 'test SMS message')