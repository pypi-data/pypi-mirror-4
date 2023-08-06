
class HttpResponseMock(object):
    pass


class TransportMock(object):

    def __init__(self, url, timeout=2, additional_handlers=None):
        pass

    def process(self, params=None):
        return TransportMock.process_return_value

    @classmethod
    def process_returns(cls, data):
        cls.process_return_value = data