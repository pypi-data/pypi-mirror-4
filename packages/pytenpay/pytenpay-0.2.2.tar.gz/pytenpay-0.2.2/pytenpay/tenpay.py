#!/usr/bin/env python
#coding:utf-8

# 作者 : 张沈鹏
# 邮箱 : zsp042@gmail.com
# 主页 : http://zuroc.42qu.com

import requests
from base64 import b64encode
from hashlib import md5
from os.path import abspath,dirname,join
from mako.template import Template

PWD = dirname(abspath(__file__))


with open(join(PWD,"pay.xml")) as PAY:
    TEMPALTE_PAY = Template(PAY.read(),input_encoding="utf-8")

with open(join(PWD,"query.xml")) as QUERY:
    TEMPALTE_QUERY = Template(QUERY.read(),input_encoding="utf-8")

class Tenpay(object):

    def __init__(self, id, key, cert):
        self.id = id
        self.key = key
        self.verify = join(PWD, 'cacert.pem')
        self.cert = cert

    def post(self, xml):
        if type(xml) is not unicode:
            xml = xml.decode("utf-8","ignore")
        xml = xml.encode("gb18030","ignore")
        content = b64encode(xml)
        abstract = md5(md5(content).hexdigest()+self.key).hexdigest()
        req = requests.post("https://mch.tenpay.com/cgi-bin/mchbatchtransfer.cgi",\
            data=dict(content=content, abstract=abstract), verify=self.verify, cert=self.cert)
        return req.text

    def pay(self, op_code, op_name, op_user, op_passwd, op_time, sp_id, package_id, total_num, total_amt, client_ip, record_set):
            args = locals()
            del args['self']
            xml = TEMPALTE_PAY.render(**args)
            return self.post(xml)

    def query(self, op_code, op_name, service_version, op_user, op_passwd, op_time, sp_id, package_id, client_ip):
        args = locals()
        del args['self']
        xml = TEMPALTE_QUERY.render(**args)
        return self.post(xml)


if __name__ == "__main__":
    tenpay = Tenpay(1900000107,"82d2f8b9fd7695aec51415ab2900a755", join(PWD,'new.pem'))
    tenpay.pay( op_code=1013, op_name="batch_draw", op_user='1900000107', op_passwd=111111, op_time=20110823105511000, sp_id=1900000107, package_id='asfffwe', total_num=2, total_amt=3, client_ip="10.6.35.42", record_set = ( ('1', '6225887811111111', '1001', u'张三', '1', '1', '20', '755', u'招商银行深圳泰然金谷支行', u'代付测试', '13631511111'), ('2', '6225887822222222', '1001', u'李四', '2', '1', '20', '755', u'招商银行深圳泰然金谷支行', '', '')))
    #tenpay.query( op_code=1014, op_name="batch_draw_query", service_version='1.1', op_user=1900000107, op_passwd=111111, op_time=20110823105511000, sp_id=1900000107, package_id=20110823001, client_ip='10.6.35.42')  
