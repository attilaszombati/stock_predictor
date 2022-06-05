class UserModelNotFound(Exception):
    def __init__(self, user):
        self.user = user
        self.message = f"SQL Alchemy model not found for user: {self.user}"
        super().__init__(self.message)


class NewsScraperMissConfigured(Exception):
    def __init__(self, user):
        self.user = user
        self.message = f"SQL Alchemy model not found for user: {self.user}"
        super().__init__(self.message)
