from StringIO import StringIO


########################################################################
class TransactionBuilder(object):

    trans_id = 0

    #----------------------------------------------------------------------
    def __init__(self, account, client, market, ticker):
        """"""
        self.__data = {
            'ACCOUNT': account,
            'CLIENT_CODE': client,
            'CLASSCODE': market,
            'SECCODE': ticker,
        }

    #----------------------------------------------------------------------
    def new_id(self):
        self.trans_id += 1
        return self.trans_id

    #----------------------------------------------------------------------
    def autogenerate(self, data):
        data.update(self.__data)
        data['TRANS_ID'] = self.new_id()
        return self.generate(data)

    #----------------------------------------------------------------------
    def limit(self, price, quantity):
        return self.autogenerate({
            'ACTION': 'NEW_ORDER',
            'TYPE': 'L',
            'OPERATION': 'B' if quantity > 0 else 'S',
            'PRICE': price,
            'QUANTITY': abs(quantity),
        })

    #----------------------------------------------------------------------
    def stop(self, stopprice, price, quantity):
        return self.autogenerate({
            'ACTION': 'NEW_STOP_ORDER',
            'TYPE': 'L',
            'OPERATION': 'B' if quantity > 0 else 'S',
            'STOPPRICE': stopprice,
            'PRICE': price,
            'QUANTITY': abs(quantity),
        })

    #----------------------------------------------------------------------
    @staticmethod
    def generate(data):
        result = StringIO()
        result.writelines("%s=%s;" % pair for pair in data.items())
        return result.getvalue()


