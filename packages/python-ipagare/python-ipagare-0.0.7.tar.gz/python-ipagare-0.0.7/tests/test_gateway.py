#coding:utf-8
import unittest
import sure
import fudge
from ipagare.gateway import IPagareGateway
from datetime import datetime

ESTABLISHMENT_ID = ''
SECURITY_CODE = ''


class IPagateGatewayTestCase(unittest.TestCase):

    def test_generat_auth_key(self):

        ipagare = IPagareGateway(ESTABLISHMENT_ID, SECURITY_CODE, sandbox=True)
        auth_key = ipagare._generate_auth_key(action='2', total='10000',
            version='1')

        auth_key.should.be.eql('d33794447f339952f290f47910c58adf')

    def test_get_payment_options(self):
        ipagare = IPagareGateway(ESTABLISHMENT_ID, SECURITY_CODE, sandbox=True)
        payment_options = ipagare.payment_options(total=10000)

        payment_options.should.have.length_of(3)

    def test_process_payment(self):
        ipagare = IPagareGateway(ESTABLISHMENT_ID, SECURITY_CODE, sandbox=True)

        ipagare._make_request = fudge.Fake().is_callable().returns({u'pedido':
            {u'status': u'3', u'codigo': u'1234', u'uid': u'10800300000334',
            u'data-status': u'04102012', u'pagamento': {
                u'hora': u'162427', u'capturado': u'1', u'forma': u'A02',
                u'codigo': u'28', u'parametros': {
                    u'numero-cartao': u'444433XXXXXX1111',
                    u'numero-cv': u'071016317+++',
                    u'numero-autorizacao': u'25085+',
                    u'codigo-retorno': u'0',
                    u'numero-transacao': u'1080030000033401'
                }, u'total': u'12000', u'data': u'04102012'
            }, u'teste': u'1', u'total': u'12000', u'hora-status': u'162426'}
        })

        ipagare_request = ipagare.process_payment(total=12000,
            payment_option='28',
            payment_form_code='A02',
            card_number='4444333322221111',
            card_expires_month='10',
            card_expires_year='2015',
            card_security_code='123',
            request_code='1234')

        ipagare_request.uid.should.be.eql('10800300000334')
        ipagare_request.code.should.be.eql('1234')
        ipagare_request.status.should.be.eql('3')
        ipagare_request.status_time.should.be.eql(datetime(2012, 10, 4, 16, 24,
            26))
        ipagare_request.payment.captured.should.be.true
        ipagare_request.payment.option_code.should.be.eql('28')
        ipagare_request.payment.form_code.should.be.eql('A02')
        ipagare_request.payment.total.should.be.eql('12000')
        ipagare_request.payment.created_at.should.be.eql(datetime(2012, 10, 4,
            16, 24, 27))
