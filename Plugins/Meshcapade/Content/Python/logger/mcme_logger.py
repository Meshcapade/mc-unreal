# MCMELogger.py

import logging
from .unreal_log_handler import UnrealLogHandler  # the class from step 1

# 1) Grab (or create) your named logger
logger = logging.getLogger("MeshcapadeME")  # Use a unique name for your logger

# 2) Only configure once
if not any(isinstance(h, UnrealLogHandler) for h in logger.handlers):
    # a) Prevent messages bubbling up to the root logger
    logger.propagate = False

    # b) Create & configure your UnrealLogHandler
    handler = UnrealLogHandler()
    fmt = logging.Formatter("[%(asctime)s][%(name)s] %(levelname)s: %(message)s",
                            datefmt="%H:%M:%S")
    handler.setFormatter(fmt)

    # c) Attach & set level
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Export the logger for other modules to import
__all__ = ["logger"]
