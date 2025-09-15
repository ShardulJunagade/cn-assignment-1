import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional


def setup_logging(script_name: str, level: int = logging.INFO, logs_dir: Optional[str] = None) -> logging.Logger:
    """
    Configure root logging to both console and a rotating file under logs/.
    - script_name: used to name the log file <script_name>.log
    - level: logging level (e.g., logging.INFO)
    - logs_dir: custom logs directory; defaults to ./logs next to this file
    Returns the configured root logger.
    """
    if logs_dir is None:
        logs_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(logs_dir, exist_ok=True)

    log_path = os.path.join(logs_dir, f"{script_name}.log")

    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    root = logging.getLogger()
    root.setLevel(level)

    # Clear existing handlers to avoid duplication on repeated setup
    for h in list(root.handlers):
        root.removeHandler(h)

    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)

    fh = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=5, encoding='utf-8')
    fh.setLevel(level)
    fh.setFormatter(formatter)

    root.addHandler(ch)
    root.addHandler(fh)

    return root
