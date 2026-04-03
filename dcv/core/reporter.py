class Reporter:
    def __init__(self):
        self.messages = []
        self.errors = []

    def info(self, message):
        self.messages.append(("INFO", message))

    def warning(self, message):
        self.messages.append(("WARNING", message))

    def error(self, message):
        self.errors.append(message)

    def has_errors(self):
        return len(self.errors) > 0

    def print_report(self):
        for level, message in self.messages:
            print(f"[{level}] {message}")

        if self.errors:
            print("\nErrors:")
            for err in self.errors:
                print(f" - {err}")
