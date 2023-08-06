#!/usr/bin/env python2.7

import logging
import shlex
import subprocess
import sys
import time

from apscheduler.scheduler import Scheduler



def parse_cron_spec (cron_spec):
    s = {}
    s["minute"], s["hour"], s["day"], s["month"], s["day_of_week"] = cron_spec.split(" ")
    return s


def process_wrapper(argv):
    return lambda: subprocess.call(argv)

def run_scheduler(jobs):


    # Set up scheduler
    sched = Scheduler()

    for cron_spec, argv in jobs:

        # Convert cron style spec inot apscheduler spec
        spec = parse_cron_spec(cron_spec)
        method = process_wrapper(argv)

        sched.add_cron_job(method, **spec)


    # Run scheduler
    sched.start()

    # Infinatly sleep
    while (True):
        time.sleep(15.0)



def main():

    logging.basicConfig()

    if not len(sys.argv) >= 2:
        print "cronsingleton: cronsingleton cron_spec command [args ...]"
        print "cronsingleton: cronsingleton cronfile"
        return -1

    jobs = []

    if len(sys.argv) == 2:
        cronfile = sys.argv[1]
        jobs_in = open(cronfile, "r")

        for line in jobs_in:
            line = line.strip()
            if len(line) > 0 and line[0] != '#':
                job_args = shlex.split(line)
                cron_spec = " ".join(job_args[:5])
                argv = job_args[5:]
                jobs.append((cron_spec, argv))
    else:
        cron_spec = sys.argv[1]
        argv = sys.argv[2:]
        jobs.append((cron_spec, argv))

    run_scheduler(jobs)

    return 0


