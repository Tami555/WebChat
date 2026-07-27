import logging


class ColorFormatter(logging.Formatter):
    """Цветной форматер для консоли"""

    COLORS = {
        "DEBUG": "\033[94m",  # Синий
        "INFO": "\033[92m",  # Зеленый
        "WARNING": "\033[93m",  # Желтый
        "ERROR": "\033[91m",  # Красный
        "CRITICAL": "\033[1;91m",  # Ярко-красный
    }
    RESET = "\033[0m"

    def format(self, record):
        log_message = super().format(record)
        if record.levelname in self.COLORS:
            return f"{self.COLORS[record.levelname]}{log_message}{self.RESET}"
        return log_message
