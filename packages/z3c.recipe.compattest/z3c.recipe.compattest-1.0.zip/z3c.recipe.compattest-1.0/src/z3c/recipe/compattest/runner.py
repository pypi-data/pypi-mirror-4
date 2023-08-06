import os.path
import subprocess
import sys
import time
import pickle

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


def usage():
    print("""
usage: %s [OPTIONS]

All given options will be passed to each test runner. To know which
options you can use, refer to the test runner documentation.
""" % sys.argv[0])

windoze = sys.platform.startswith('win')


class Job(object):

    def __init__(self, script, args):
        self.script = script
        self.args = args
        self.name = os.path.basename(script)
        self.output = StringIO()
        self.exitcode = None

    def start(self):
        self.start = time.time()

        cmd = [self.script]
        # We are dealing with two problems: windoze and virtualenv.
        if windoze:
            # Use zc.buildout internal to sniff a virtualenv.
            cmd = [self.script + '.exe']

        self.process = subprocess.Popen(
            cmd + ['--exit-with-status'] + self.args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            close_fds=not windoze,
        )

    def poll(self):
        self.exitcode = self.process.poll()
        if self.exitcode is not None:
            self.end = time.time()
            # We're done, get it all
            data = self.process.stdout.read()
        else:
            # We're not done, so just get some
            data = self.process.stdout.readline()
        self.output.write(data.replace(b'\r\n', b'\n').decode('utf-8'))


def main(max_jobs, *scripts, **options):
    argv = sys.argv[1:]
    if '-h' in argv or '--help' in argv:
        usage()
        return

    running = []
    completed = []
    scripts = list(scripts)

    # Read statistics from the last run and re-order testing to start
    # the slowest tests first.
    stat_file_name = os.path.join(os.path.expanduser('~'), '.zope.teststats')
    try:
        stat_file = open(stat_file_name, 'rb')
    except IOError:
        stats = {}
    else:
        stats = pickle.load(stat_file)
        stat_file.close()
    if stats:
        default_time = sum(stats.values()) / float(len(stats))
    else:
        default_time = 0
    scripts.sort(
        key=lambda package: -stats.get(os.path.basename(package), default_time)
        )

    # Main loop for controlling test runs
    while scripts or running:
        for job in running:
            job.poll()
            if job.exitcode is None:
                continue
            completed.append(job)
            running.remove(job)
            if job.exitcode:
                print("%s failed with:" % job.name)
                print(job.output.getvalue())

        while (len(running) < max_jobs) and scripts:
            script = scripts.pop(0)
            job = Job(script, sys.argv[1:])
            print("Running %s" % job.name)
            job.start()
            running.append(job)

    # Result output
    failures = [job for job in completed if job.exitcode]
    print("%d failure(s)." % len(failures))
    for job in failures:
        print("- %s" % job.name)

    # Store statistics
    for job in completed:
        stats[job.name] = job.end - job.start
    try:
        stat_file = open(stat_file_name, 'wb')
    except IOError:
        # Statistics aren't that important. Just ignore that.
        pass
    else:
        pickle.dump(stats, stat_file)

    if not options.get('no_exit_code') and failures:
        sys.exit(1)
