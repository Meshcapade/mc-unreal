import logging
import os
import platform
import sys
import subprocess


def get_python_path():
    base_dir = os.path.dirname(os.path.dirname(sys.executable))
    system = platform.system()

    if system == "Windows":
        return os.path.join(base_dir, "ThirdParty", "Python3", "Win64", "python.exe")
    elif system == "Linux":
        return os.path.join(
            base_dir, "ThirdParty", "Python3", "Linux", "bin", "python3"
        )
    elif system == "Darwin":  # macOS
        return os.path.join(base_dir, "ThirdParty", "Python3", "Mac", "bin", "python3")
    else:
        raise Exception(f"Unsupported OS: {system}")


def install_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    python_exec_path = get_python_path()
    try:
        subprocess.check_call(
            [python_exec_path, "-m", "pip", "install", "-r", requirements_path]
        )
        logging.info("✅ Installed requirements")
    except Exception as e:
        logging.error(f"❌ Failed to install requirements: {e}")


install_requirements()
