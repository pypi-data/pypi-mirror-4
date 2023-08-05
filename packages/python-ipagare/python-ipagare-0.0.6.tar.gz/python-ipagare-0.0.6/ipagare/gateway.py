# coding: utf-8
import hashlib
import requests
import simplexml
from ipagare.error import IPagareError
from ipagare.model import Request


# meios de pagamento
# (codigo, (nome, convenio, instituicao))
IPagarePaymentOption = (
    (1,  (u'Diners', 'Komerci', 'Redecard')),
    (2,  (u'Mastercard', 'Komerci', 'Redecard')),
    (3,  (u'Cartões Bradesco (Pagamento Fácil)', 'Comércio Eletrônico (SPS)',
           'Banco Bradesco')),
    (11, (u'American Express', 'WebPOS', 'American Express')),
    (14, (u'Cartões Itaucard', 'Itaú Shopline', 'Banco Itaú')),
    (25, (u'Diners', 'Komerci WebService', 'Redecard')),
    (26, (u'Mastercard', 'Komerci WebService', 'Redecard')),
    (28, (u'American Express', 'WebPOS Webservice', 'American Express')),
    (34, (u'Visa', 'Komerci', 'Redecard')),
    (35, (u'Visa', 'Komerci Webservice', 'Redecard')),
    (36, (u'Visa', 'Buy Page Cielo', 'Cielo')),
    (38, (u'Visa', 'Buy Page Loja', 'Cielo')),
    (40, (u'Mastercard', 'Buy Page Cielo', 'Cielo')),
    (41, (u'Mastercard', 'Buy Page Loja', 'Cielo')),
    (44, (u'Elo', 'Buy Page Cielo', 'Cielo')),
    (45, (u'Elo', 'Buy Page Loja', 'Cielo')),
    (48, (u'Diners', 'Buy Page Cielo', 'Cielo')),
    (49, (u'Diners', 'Buy Page Loja', 'Cielo')),
    (17, (u'Cartões Real (Visa)', 'Real Pague Internet', 'Banco Real')),
    (32, (u'Mastercard', 'Moset', 'Cielo')),
    (27, (u'Visa', 'Moset', 'Cielo')),
    (7,  (u'Visa', 'Verified by Visa', 'Cielo')),
    (31, (u'Hipercard', 'Hipercommerce', 'Hipercard')),
    (39, (u'Mastercard', 'Verified by Visa', 'Cielo')),
    (46, (u'Discover', 'Buy Page Cielo', 'Cielo')),
    (47, (u'Discover', 'Buy Page Loja', 'Cielo'))
)


# formas de pagamento
IPagarePaymentForm = (
    ('A01', u'à vista'),
    ('A02', u'2x sem juros'),
    ('A03', u'3x sem juros'),
    ('A04', u'4x sem juros'),
    ('A03', u'3x sem juros'),
    ('A06', u'6x sem juros'),
    ('A07', u'7x sem juros'),
    ('A08', u'8x sem juros'),
    ('A09', u'9x sem juros'),
    ('A10', u'10x sem juros'),
    ('A11', u'11x sem juros'),
    ('A12', u'12x sem juros'),
    ('B02', u'2x com juros'),
    ('B03', u'3x com juros'),
    ('B04', u'4x com juros'),
    ('B05', u'5x com juros'),
    ('B06', u'6x com juros'),
    ('B07', u'7x com juros'),
    ('B08', u'8x com juros'),
    ('B09', u'9x com juros'),
    ('B10', u'10x com juros'),
    ('B11', u'11x com juros'),
    ('B12', u'12x com juros')
)


class IPagareAction:
    """Define iPagare action numbers
    """
    PROCESS_PAYMENT = 2
    PAYMENT_OPTIONS = 5


class IPagareGateway(object):

    def __init__(self, establishment_id, security_code, sandbox=False,
        endpoint='https://ww2.ipagare.com.br/service/process.do'):
        assert isinstance(establishment_id, str)
        assert isinstance(security_code, str)
        assert isinstance(sandbox, bool)

        self.establishment_id = establishment_id
        self.security_code = security_code
        self.endpoint = endpoint
        self.sandbox = sandbox
        self.version = '2'

    def _generate_auth_key(self, action, total, version):
        assert isinstance(action, str)
        assert isinstance(total, str)

        authkey = [
            self.establishment_id,
            hashlib.md5(self.security_code).hexdigest(),
            action,
            total
        ]

        if version == '2':
            authkey.append(self.version)

        return hashlib.md5("".join(authkey)).hexdigest()

    def _make_request(self, action, total, params=None, version=None):
        params = params or {}
        version = version or self.version

        assert isinstance(action, str)
        assert isinstance(total, str)
        assert isinstance(params, dict)

        default_params = {
            'estabelecimento': self.establishment_id,
            'acao': action,
            'chave': self._generate_auth_key(action, total, version),
            'valor_total': total,
            'versao': self.version
        }
        if self.sandbox:
            default_params['teste'] = '1'

        params.update(default_params)

        response = requests.post(self.endpoint, params=params)

        response_data = simplexml.loads(response.text\
            .encode(response.encoding))

        if 'erro' in response_data:
            raise IPagareError(response_data['erro'])

        return response_data

    def payment_options(self, total):
        """Recupera as formas de pagamento configuradas no painel do iPagare

        exemplo de retorno:
        >>> [{
        >>>   'formas': [u'\xe0 vista', u'2x sem juros'],
        >>>   'instituicao': 'American Express',
        >>>   'convenio': 'WebPOS Webservice',
        >>>   'nome': 'American Express'
        >>> }]

        :Parameter:
          - `total`: valor total da compra como inteiro.
             por exemplo: R$110,10 ficaria 11110
        """
        assert isinstance(total, int)

        total = str(total)
        action = str(IPagareAction.PAYMENT_OPTIONS)

        response = self._make_request(action=action, total=total, version='1')

        PAYMENT_OPTIONS = dict(IPagarePaymentOption)
        PAYMENT_FORMS = dict(IPagarePaymentForm)

        prepared_payment_options = []
        for payment_option in response['pedido']['opcoes-pagamento']:
            nome, convenio, instituicao = PAYMENT_OPTIONS.get(
                int(payment_option['codigo']))

            forms = []

            payment_forms = payment_option['formas']
            if not isinstance(payment_forms, list):
                payment_forms = [payment_forms['forma']]

            for payment_form in payment_forms:
                codigo = str(payment_form['codigo'])
                forms.append((codigo, PAYMENT_FORMS.get(codigo)))

            prepared_payment_options.append({
                'nome': nome,
                'convenio': convenio,
                'instituicao': instituicao,
                'codigo': payment_option['codigo'],
                'formas': forms
            })

        return prepared_payment_options

    def process_payment(self, total, payment_option, payment_form_code,
        card_number=None, card_expires_month=None, card_expires_year=None,
        card_security_code=None, request_code=None, **kw):
        """Processar pagamentos pela Integração Webservice

        :Parameters:
          - `total`: valor total da compra como inteiro.
             por exemplo: R$110,10 ficaria 11110
          - `payment_option`: codigo do meio de pagamento
          - `payment_form_code`: codigo da forma de pagamento
          - `card_number`: Número do cartão de crédito, somente números,
            sem separadores. Ex: 4444333322221111.
          - `card_expires_month`: Mês da validade do cartão com 2 dígitos.
            Ex: 05.
          - `card_expires_year`: Ano da validade do cartão com 4 dígitos.
            Ex: 2008.
          - `card_security_code`: Código de segurança do cartão
            (3 dígitos para Visa, Mastercard e Diners;
            4 dígitos para American Express).
          - `request_code`: (optional) código ou chave ÚNICA do pedido no Site
          - `kw`: qualquer parametro opcional
        """
        total = str(total)
        action = str(IPagareAction.PROCESS_PAYMENT)

        params = {
            'codigo_pagamento': payment_option,
            'forma_pagamento': payment_form_code,
            'numero_cartao': card_number,
            'mes_validade_cartao': card_expires_month,
            'ano_validade_cartao': card_expires_year,
            'codigo_seguranca_cartao': card_security_code
        }

        if request_code:
            params['codigo_pedido'] = request_code

        params.update(kw)

        response = self._make_request(action=action, total=total,
            params=params, version='2')

        return Request.create_from_dict(**response.get('pedido'))
