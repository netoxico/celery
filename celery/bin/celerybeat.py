#!/usr/bin/env python
"""celerybeat

.. program:: celerybeat

.. cmdoption:: -s, --schedule

    Path to the schedule database. Defaults to `celerybeat-schedule`.
    The extension ".db" will be appended to the filename.

.. cmdoption:: -S, --scheduler

    Scheduler class to use. Default is celery.beat.PersistentScheduler

.. cmdoption:: -f, --logfile

    Path to log file. If no logfile is specified, `stderr` is used.

.. cmdoption:: -l, --loglevel

    Logging level, choose between `DEBUG`, `INFO`, `WARNING`,
    `ERROR`, `CRITICAL`, or `FATAL`.

"""
from __future__ import with_statement
from __future__ import absolute_import

from functools import partial

from ..platforms import detached

from .base import Command, Option, daemon_options


class BeatCommand(Command):
    supports_args = False

    def run(self, detach=False, logfile=None, pidfile=None, uid=None,
            gid=None, umask=None, working_directory=None, **kwargs):
        kwargs.pop("app", None)
        beat = partial(self.app.Beat,
                       logfile=logfile, pidfile=pidfile, **kwargs)
        workdir = working_directory

        if detach:
            with detached(logfile, pidfile, uid, gid, umask, workdir):
                return beat().run()
        else:
            return beat().run()

    def get_options(self):
        conf = self.app.conf

        return (
            Option('--detach',
                default=False, action="store_true", dest="detach",
                help="Detach and run in the background."),
            Option('-s', '--schedule',
                default=conf.CELERYBEAT_SCHEDULE_FILENAME,
                action="store", dest="schedule",
                help="Path to the schedule database. The extension "
                    "'.db' will be appended to the filename. Default: %s" % (
                            conf.CELERYBEAT_SCHEDULE_FILENAME, )),
            Option('--max-interval',
                default=3600.0, type="float", dest="max_interval",
                help="Max. seconds to sleep between schedule iterations."),
            Option('-S', '--scheduler',
                default=None,
                action="store", dest="scheduler_cls",
                help="Scheduler class. Default is "
                     "celery.beat.PersistentScheduler"),
            Option('-l', '--loglevel',
                default=conf.CELERYBEAT_LOG_LEVEL,
                action="store", dest="loglevel",
                help="Loglevel. One of DEBUG/INFO/WARNING/ERROR/CRITICAL."),
        ) + daemon_options(default_pidfile="celerybeat.pid",
                           default_logfile=conf.CELERYBEAT_LOG_FILE)


def main():
    beat = BeatCommand()
    beat.execute_from_commandline()

if __name__ == "__main__":      # pragma: no cover
    main()
