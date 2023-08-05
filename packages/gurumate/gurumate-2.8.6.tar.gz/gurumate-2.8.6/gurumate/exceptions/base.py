class EvalResultException(Exception):
    def __init__(self, status=0, message=None, metadata=None):
        self.status = status
        self.message = message
        self.metadata = metadata

class ValidationError(Exception):
    def __init__(self, hint):
        self._message = hint
        Exception.__init__(self, hint)
        
    def get_hint(self):
        return self._message
    
class ReturnException(Exception):
    def __init__(self, values):
        self._values = values

    def get_return_values(self):
        return self._values
