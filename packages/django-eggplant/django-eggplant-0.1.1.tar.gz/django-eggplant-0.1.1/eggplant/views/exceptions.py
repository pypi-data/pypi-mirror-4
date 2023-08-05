class ViewError(Exception):
    def __init__(self, status_code, message=None):
        if message is None: message = 'Something goes wrong ...'
        self.status_code = status_code
        self.message = message
        self.error_handler = None

class LackOfRequiredKeyError(ViewError):
    def __init__(self, key):
        status_code = 400
        message = 'Key "%s" is required.'%key
        super(LackOfRequiredKeyError, self).__init__(status_code, message)
        self.key = key

class KeyValidationError(ViewError):
    def __init__(self, key, messages):
        status_code = 400
        message = 'Key "%s" is invalid.' % key
        super(KeyValidationError, self).__init__(status_code, message)
        self.key = key
        self.raw_messages = messages
