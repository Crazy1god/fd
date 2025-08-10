import logging

class MaxLevelFilter(logging.Filter):
    """Пропускает только записи с уровнем <= заданного."""
    def __init__(self, level='INFO'):
        super().__init__()
        self.max_level = logging._nameToLevel.get(level, logging.INFO)

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno <= self.max_level


class ExactLevelFilter(logging.Filter):
    """Пропускает только записи с точным уровнем."""
    def __init__(self, level='WARNING'):
        super().__init__()
        self.level = logging._nameToLevel.get(level, logging.WARNING)

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno == self.level