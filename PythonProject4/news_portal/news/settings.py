import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "filters": {
        # В консоль только при DEBUG = True
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
        # В general.log и письма только при DEBUG = False
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        # Для консоли: DEBUG/INFO в «простом» формате
        "max_info": {
            "()": "your_app.logging_filters.MaxLevelFilter",
            "level": "INFO",
        },
        # Для консоли: отдельный формат ровно для WARNING
        "only_warning": {
            "()": "your_app.logging_filters.ExactLevelFilter",
            "level": "WARNING",
        },
    },

    "formatters": {
        # Консоль: DEBUG/INFO — время, уровень, сообщение
        "console_basic": {
            "format": "%(asctime)s [%(levelname)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        # Консоль: WARNING — время, уровень, сообщение, путь
        "console_warning": {
            "format": "%(asctime)s [%(levelname)s] %(message)s — %(pathname)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        # Консоль: ERROR/CRITICAL — время, уровень, сообщение, путь, стек
        "console_error": {
            "format": "%(asctime)s [%(levelname)s] %(message)s — %(pathname)s %(exc_text)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },

        # general.log: время, уровень, модуль, сообщение
        "general": {
            "format": "%(asctime)s [%(levelname)s] %(module)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },

        # errors.log: время, уровень, сообщение, путь, стек
        "errors": {
            "format": "%(asctime)s [%(levelname)s] %(message)s — %(pathname)s %(exc_text)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },

        # security.log: время, уровень, модуль, сообщение
        "security": {
            "format": "%(asctime)s [%(levelname)s] %(module)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },

        # Письма: как errors.log, но без стека
        "mail_no_exc": {
            "format": "%(asctime)s [%(levelname)s] %(message)s — %(pathname)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },

    "handlers": {
        # Консоль: DEBUG/INFO
        "console_debug": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "filters": ["require_debug_true", "max_info"],
            "formatter": "console_basic",
        },
        # Консоль: WARNING (ровно)
        "console_warning": {
            "class": "logging.StreamHandler",
            "level": "WARNING",
            "filters": ["require_debug_true", "only_warning"],
            "formatter": "console_warning",
        },
        # Консоль: ERROR/CRITICAL
        "console_error": {
            "class": "logging.StreamHandler",
            "level": "ERROR",
            "filters": ["require_debug_true"],
            "formatter": "console_error",
        },

        # Файл general.log (только при DEBUG = False)
        "general_file": {
            "class": "logging.FileHandler",
            "level": "INFO",
            "filters": ["require_debug_false"],
            "formatter": "general",
            "filename": os.fspath(LOG_DIR / "general.log"),
            "encoding": "utf-8",
        },

        # Файл errors.log (ERROR/CRITICAL)
        "errors_file": {
            "class": "logging.FileHandler",
            "level": "ERROR",
            "formatter": "errors",
            "filename": os.fspath(LOG_DIR / "errors.log"),
            "encoding": "utf-8",
        },

        # Файл security.log (только из django.security)
        "security_file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "security",
            "filename": os.fspath(LOG_DIR / "security.log"),
            "encoding": "utf-8",
        },

        # Письма администраторам (ERROR+, только при DEBUG = False)
        "mail_admins": {
            "class": "django.utils.log.AdminEmailHandler",
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "formatter": "mail_no_exc",
            # "include_html": True,  # по желанию
        },
    },

    "loggers": {
        # Основной логгер Django -> консоль и general.log
        "django": {
            "handlers": ["console_debug", "console_warning", "console_error", "general_file"],
            "level": "DEBUG",
            "propagate": False,
        },

        # Ошибки запросов/сервера -> errors.log и email; также пойдут наверх в "django"
        "django.request": {
            "handlers": ["errors_file", "mail_admins"],
            "level": "NOTSET",
            "propagate": True,
        },
        "django.server": {
            "handlers": ["errors_file", "mail_admins"],
            "level": "NOTSET",
            "propagate": True,
        },

        # Шаблоны и БД -> только errors.log; также пойдут наверх в "django"
        "django.template": {
            "handlers": ["errors_file"],
            "level": "NOTSET",
            "propagate": True,
        },
        "django.db.backends": {
            "handlers": ["errors_file"],
            "level": "NOTSET",
            "propagate": True,
        },

        # Безопасность -> только security.log
        "django.security": {
            "handlers": ["security_file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}