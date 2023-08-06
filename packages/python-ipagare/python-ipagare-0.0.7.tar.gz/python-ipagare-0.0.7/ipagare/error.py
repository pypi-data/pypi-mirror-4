#coding: utf-8


class IPagareError(Exception):

    def __init__(self, error):
        self.code = error.get('codigo').encode('utf-8')
        self.description = error.get('descricao').encode('utf-8')

        error_text = 'IPagare Error {}: {}'.format(self.code, self.description)

        super(IPagareError, self).__init__(error_text)
