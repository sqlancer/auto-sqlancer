import logging
import os
import sys
from datetime import datetime
import subprocess
import logging

def run_command(cmd, logger: logging.Logger, check=True):
    logger.debug("Running: %s", " ".join(cmd))
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1) as p:
        assert p.stdout is not None
        for line in p.stdout:
            logger.debug(line.rstrip("\n"))
        rc = p.wait()
        if check and rc != 0:
            raise subprocess.CalledProcessError(rc, cmd)
        return rc

def setup_logging(log_dir="logs"):
    run_dir = os.path.join(log_dir, datetime.now().strftime("%y-%m-%d-%H-%M-%S"))
    os.makedirs(run_dir, exist_ok=True)

    file_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    console_fmt = logging.Formatter("%(message)s")

    def _mk_logger(name, filename, to_console=False, console_level=logging.INFO):
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        fh = logging.FileHandler(os.path.join(run_dir, filename))
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(file_fmt)
        logger.addHandler(fh)

        if to_console:
            ch = logging.StreamHandler(sys.stdout)
            ch.setLevel(console_level)
            ch.setFormatter(console_fmt)
            logger.addHandler(ch)

        return logger

    script_logger = _mk_logger("script", "script.log", to_console=True, console_level=logging.INFO)
    docker_logger = _mk_logger("docker", "docker.log")
    sqlancer_logger = _mk_logger("sqlancer", "sqlancer.log", console_level=logging.DEBUG)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    for h in list(root.handlers):
        root.removeHandler(h)
    err_console = logging.StreamHandler(sys.stderr)
    err_console.setLevel(logging.WARNING)
    err_console.setFormatter(file_fmt)
    root.addHandler(err_console)

    return script_logger, docker_logger, sqlancer_logger, run_dir
