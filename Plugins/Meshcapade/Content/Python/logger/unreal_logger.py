import unreal

from logger.base import Logger


class UnrealLogger(Logger):
    def debug(self, msg: str):
        unreal.log(msg)

    def info(self, msg: str):
        unreal.log(msg)

    def warning(self, msg: str):
        unreal.log_warning(msg)

    def error(self, msg: str):
        unreal.log_error(msg)

    def critical(self, msg: str):
        unreal.log_error(f"[CRITICAL] {msg}")
