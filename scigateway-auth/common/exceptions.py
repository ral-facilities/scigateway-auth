class APIError(Exception):
    pass


class MissingMnemonicError(APIError):
    pass

class BadMnemonicError(APIError):
    pass

class AuthenticationError(APIError):
    pass
