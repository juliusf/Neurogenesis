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
            print("INFO: "),
        elif log_type == "debug":
            print("DEBUG: ")
        print(message),
        print(PrintColors.ENDC)


class PrintColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'