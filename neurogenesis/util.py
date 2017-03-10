class Logger(object):
    log_level = 3
    @staticmethod
    def warning(message):
        if Logger.log_level > 1:
            Logger.log("warning", message)

    @staticmethod
    def error(message):
        Logger.log("error", message)

    @staticmethod
    def info(message):
        if Logger.log_level > 2:
            Logger.log("info", message)
    @staticmethod
    def debug(message):
        if Logger.log_level > 3:
            Logger.log("debug", message)
    @staticmethod
    def log(log_type, message):
        if log_type == "warning":
            print(PrintColors.WARNING),
            print("WARNING: "),
        elif log_type == "error":
            print(PrintColors.FAIL),
            print("ERROR: "),
        elif log_type == "info":
            print(PrintColors.DEFAULT),
            print("INFO: "),
        elif log_type == "debug":
            print(PrintColors.DEFAULT),
            print("DEBUG: "),
        print(message),
        print(PrintColors.ENDC)

    @staticmethod
    def printColor(color, text):
        print(color),
        print(text),
        print(PrintColors.ENDC)

class PrintColors:
    DEFAULT = '\033[99m'
    MAGENTA = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'