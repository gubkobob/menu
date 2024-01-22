class NotFoundException(Exception):
    def __init__(self, error_type: str, error_message: str, *args, **kwargs):
        self.error_type = error_type
        self.error_message = error_message

    def __repr__(self):
        return {
            "detail": self.error_message,
        }

    def answer(self):
        return {
            "detail": self.error_message,
        }
