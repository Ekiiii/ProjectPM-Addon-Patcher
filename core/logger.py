# -*- coding: utf-8 -*-
"""
logger.py
Physical On-Disk Persistent Logging Subsystem for ProjectPM Addon Patcher.
Records comprehensive diagnostic logs to disk:
- System & environment information
- Loaded ROM analysis & cryptographic SHA-1 hashes
- Detailed patching pipeline progress & xDelta commands
- Injected payloads, restored tables, and randomizer states
- Full stack traces upon any warning or error
"""
import os
import sys
import time
import datetime
import traceback
import threading
import platform

_log_lock = threading.RLock()
_current_log_file = None
_latest_log_file = None

def get_app_dir() -> str:
    """Returns the physical directory where the executable (or main script) lives."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_logs_dir() -> str:
    """Returns the dedicated logs/ directory, creating it if necessary."""
    app_dir = get_app_dir()
    logs_dir = os.path.join(app_dir, "logs")
    try:
        os.makedirs(logs_dir, exist_ok=True)
    except Exception:
        pass
    return logs_dir

def init_logging(app_version: str = "1.0.4"):
    """Initializes the physical log files for this application run."""
    global _current_log_file, _latest_log_file
    with _log_lock:
        try:
            logs_dir = get_logs_dir()
            today_str = datetime.datetime.now().strftime("%Y-%m-%d")
            _current_log_file = os.path.join(logs_dir, f"patcher_{today_str}.log")
            _latest_log_file = os.path.join(logs_dir, "patcher_latest.log")

            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            header = [
                "=" * 80,
                f"PROJECT PM ADDON PATCHER & RANDOMIZER - SESSION START",
                f"Timestamp       : {now_str}",
                f"Application Ver : {app_version}",
                f"Python Version  : {sys.version.split()[0]} ({platform.architecture()[0]})",
                f"Platform / OS   : {platform.system()} {platform.release()} (Build {platform.version()})",
                f"Executable Path : {sys.executable}",
                f"App Root Path   : {get_app_dir()}",
                f"Is Frozen (EXE) : {getattr(sys, 'frozen', False)}",
                f"Log File        : {_current_log_file}",
                "=" * 80,
                ""
            ]
            content = "\n".join(header) + "\n"

            # Append to daily log
            with open(_current_log_file, "a", encoding="utf-8") as f:
                f.write(content)

            # Overwrite or update latest log
            with open(_latest_log_file, "w", encoding="utf-8") as f:
                f.write(content)

        except Exception as e:
            print(f"[Logger Init Error] {e}")

def log(msg: str, level: str = "INFO"):
    """Writes a timestamped message to both physical log files and stdout."""
    global _current_log_file, _latest_log_file
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    line = f"[{now}] [{level.upper()}] {msg}\n"

    print(f"[{level.upper()}] {msg}")

    with _log_lock:
        if not _current_log_file or not _latest_log_file:
            init_logging()

        for target in (_current_log_file, _latest_log_file):
            if target:
                try:
                    with open(target, "a", encoding="utf-8") as f:
                        f.write(line)
                        f.flush()
                except Exception:
                    pass

def log_info(msg: str):
    log(msg, level="INFO")

def log_warning(msg: str):
    log(msg, level="WARN")

def log_error(msg: str, exc: Exception = None):
    err_text = str(msg)
    if exc:
        err_text += f"\nException: {exc}\n{traceback.format_exc()}"
    log(err_text, level="ERROR")

def get_physical_logger(extra_cb=None):
    """
    Returns a unified logging callback suitable for pipeline progress.
    Writes line to disk and calls extra_cb(msg) for UI mirroring.
    """
    def _cb(msg: str):
        level = "INFO"
        if "[ERREUR]" in msg or "[Error]" in msg or "failed" in msg.lower():
            level = "ERROR"
        elif "[Warning]" in msg or "[Notice]" in msg:
            level = "WARN"
        log(msg, level=level)
        if extra_cb:
            try:
                extra_cb(msg)
            except Exception:
                pass
    return _cb

def open_logs_folder():
    """Opens the logs folder in Windows Explorer."""
    logs_dir = get_logs_dir()
    try:
        if platform.system() == "Windows":
            os.startfile(logs_dir)
        else:
            import subprocess
            subprocess.Popen(["xdg-open", logs_dir])
    except Exception as e:
        log_error(f"Failed to open logs folder: {e}")
