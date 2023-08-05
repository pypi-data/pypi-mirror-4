import logging
from threading import local

from django.core.signals import request_finished
from django.utils.importlib import import_module

from signals import finished, process, warning

log = logging.getLogger('paranoia')

_locals = local()


def setup():
    if not hasattr(_locals, 'signals'):
        _locals.signals = []
        return True


def add_signal(signal, **kw):
    setup()
    # Let's not pickle the sender.
    kw['sender'] = kw['sender'].__name__
    _locals.signals.append(kw)

def reset(**kw):
    setup()
    _locals.signals = []


def process_signals(signal, **kw):
    # We need to batch up all signals here and then send them when the
    # request is finished. This allows us to pass through the request
    # to the reporters, allowing more detailed logs.
    if setup():
        return

    for data in _locals.signals:
        process.send(request=kw['request'], **data)


def config(reporters=None, *args, **kw):
    if not reporters:
        try:
            from django.conf import settings
            reporters = getattr(settings, 'DJANGO_PARANOIA_REPORTERS', [])
        except ImportError:
            # This can occur when running the tests, because at this time
            # the settings module isn't created. TODO: fix this.
            return

    for reporter in reporters:
        try:
            to = import_module(reporter).report
        except ImportError:
            log.error('Failed to register the reporter: %s' % reporter)
            continue

        # Each reporter gets connected to the process signal.
        process.connect(to, dispatch_uid='paranoia.reporter.%s' % reporter)

    # The warning signal is sent by forms, sessions etc when they
    # encounter something.
    warning.connect(add_signal, dispatch_uid='paranoia.warning')
    # The finished signal is sent by the middleware when the request is
    # finished. This then processes all the warning signals built up so far
    # on that request.
    finished.connect(process_signals, dispatch_uid='paranoia.finished')
