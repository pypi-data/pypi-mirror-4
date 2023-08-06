#!/usr/bin/env python
#coding:utf-8
import tornado.ioloop
import tornado.web
from hashlib import md5

class Handler(tornado.web.RequestHandler):
    def check(self, key):
        arguments = {}
        for arg in (
            'draw_id', 
            'input_charset', 
            'op_name', 
            'op_time', 
            'package_id', 
            'partner', 
            'pay_amt', 
            'retcode', 
            'retmsg', 
            'serial', 
            'service_version', 
            'sign_key_index', 
            'sign_type', 
            'sign'
        ):
            arguments[arg] = self.get_argument(arg, '')
        sign = arguments['sign'].lower()
        del arguments['sign']
        arguments = ['%s=%s' % (k, v) for k, v in list(arguments.items())]
        arguments.sort()
        arguments.append('key=%s' % key)
        arg_string = '&'.join(arguments)
        sign_local = md5(arg_string).hexdigest()
        return sign == sign_local

    def get(self):
        package_id = self.get_argument('package_id', '')
        if self.check(key='abcdefg'):
            self.write("success")


if __name__ == "__main__":
    application = tornado.web.Application([
        (r"/", Handler),
    ])
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
