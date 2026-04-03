class DCVError(Exception):
    def __init__(self, message, line=None):
        self.message = message
        self.line = line
        super().__init__(self.format_message())

    def format_message(self):
        if self.line:
            return f"Line {self.line} → {self.message}"
        return self.message
