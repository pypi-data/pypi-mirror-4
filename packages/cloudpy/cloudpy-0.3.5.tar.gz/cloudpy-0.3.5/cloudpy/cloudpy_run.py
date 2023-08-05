#!/usr/bin/env python

import subprocess
import sys

eval_prog = "cloudpy-eval"


def run(package, noisy, clean, config):
    ENDLINE = "Connection to %s closed." % config.host.split("@")[1]
    target = config.host_sep.join([config.depository, package])

    eval_prog_args = []

    if not noisy:
        eval_prog_args.append("-q")
    if clean:
        eval_prog_args.append("-c")

    return subprocess.call(["ssh", "-t", config.host, eval_prog, " ".join(eval_prog_args), target], stdout=sys.stdout, stderr=sys.stderr)