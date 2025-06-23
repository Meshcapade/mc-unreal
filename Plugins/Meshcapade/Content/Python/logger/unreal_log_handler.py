import logging
import unreal

class UnrealLogHandler(logging.Handler):
    """
    A logging.Handler that sends log messages into the Unreal Output Log.
    Depending on record.levelno, it will call unreal.log, unreal.log_warning, or unreal.log_error.
    """
    def __init__(self):
        super().__init__()

    def emit(self, record):
        try:
            msg = self.format(record)
            level = record.levelno

            # Map Python logging levels to Unreal log calls
            if level >= logging.ERROR:
                unreal.log_error(msg)
            elif level >= logging.WARNING:
                unreal.log_warning(msg)
            else:
                unreal.log(msg)
        except Exception as e:
            # If something goes wrong in logging, fallback to printing
            print(f"[UnrealLogHandler] failed to emit record: {e}")
