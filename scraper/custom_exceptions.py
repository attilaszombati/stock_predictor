
class UserModelNotFound(Exception):
    def __init__(self, user):
        self.user = user
        self.message = f"Peewee model not found for user: {self.user}"
        super().__init__(self.message)
