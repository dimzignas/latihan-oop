class UserError(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message


class UserNotFoundError(UserError):
    pass


class UserAlreadyRegisteredError(UserError):
    pass


class InvalidEmailError(UserError):
    pass


class IncorrectPasswordError(UserError):
    pass
