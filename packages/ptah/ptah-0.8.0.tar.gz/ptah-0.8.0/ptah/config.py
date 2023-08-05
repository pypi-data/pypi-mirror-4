import sys
import logging
import signal
import traceback
from collections import defaultdict, namedtuple, OrderedDict
from pyramid.compat import NativeIO
from pyramid.registry import Introspectable
from pyramid.threadlocal import get_current_registry

import venusian
from venusian.advice import getFrameInfo

ATTACH_ATTR = '__ptah_actions__'
ID_SUBSCRIBER = 'ptah:subscriber'

__all__ = ('initialize', 'get_cfg_storage', 'StopException',
           'event', 'subscriber', 'shutdown', 'shutdown_handler',
           'Action', 'DirectiveInfo')

log = logging.getLogger('ptah')


class StopException(Exception):
    """ Special initialization exception means stop execution """

    def __init__(self, exc=None):
        self.exc = exc
        if isinstance(exc, BaseException):
            self.isexc = True
            self.exc_type, self.exc_value, self.exc_traceback = sys.exc_info()
        else:
            self.isexc = False

    def __str__(self):
        return ('\n{0}'.format(self.print_tb()))

    def print_tb(self):
        if self.isexc and self.exc_value:
            out = NativeIO()
            traceback.print_exception(
                self.exc_type, self.exc_value, self.exc_traceback, file=out)
            return out.getvalue()
        else:
            return self.exc


class ObjectEventNotify(object):

    def __init__(self, registry):
        self.registry = registry

    def __call__(self, event):
        self.registry.subscribers((event.object, event), None)


def get_cfg_storage(id, registry=None, default_factory=OrderedDict):
    """ Return current config storage """
    if registry is None:
        registry = get_current_registry()

    try:
        storage = registry.__ptah_storage__
    except AttributeError:
        storage = defaultdict(lambda: OrderedDict())
        registry.__ptah_storage__ = storage

    if id not in storage:
        storage[id] = default_factory()
    return storage[id]


def pyramid_get_cfg_storage(config, id):
    return get_cfg_storage(id, config.registry)


def subscriber(*args):
    """ Register event subscriber. """
    info = DirectiveInfo(allowed_scope=('module', 'function call'))

    def wrapper(func):
        required = tuple(args)
        discr = (ID_SUBSCRIBER, func, required)

        intr = Introspectable(
            ID_SUBSCRIBER, discr, 'Subscriber', 'ptah-subscriber')
        intr['required'] = required
        intr['handler'] = func
        intr['codeinfo'] = info.codeinfo

        def _register(cfg, func, required):
            cfg.registry.registerHandler(func, required)

        info.attach(
            Action(
                _register, (func, required),
                discriminator=discr, introspectables=(intr,))
            )
        return func

    return wrapper


class Action(object):

    hash = None

    def __init__(self, callable, args=(), kw={},
                 discriminator=None, order=0, introspectables=(), info=None):
        self.callable = callable
        self.args = args
        self.kw = kw
        self.order = order
        self.info = info
        self.introspectables = introspectables
        self.discriminator = discriminator

    def __hash__(self):
        return hash(self.hash)

    def __repr__(self):
        return '<%s "%s">'%(
            self.__class__.__name__,
            self.discriminator[0] if self.discriminator else None)

    def __call__(self, cfg):
        if self.callable:
            try:
                self.callable(cfg, *self.args, **self.kw)
            except:  # pragma: no cover
                log.exception(self.discriminator)
                raise


CodeInfo = namedtuple('Codeinfo', 'filename lineno function source module')


class AttachData(OrderedDict):
    """ container for Attach infos """


class DirectiveInfo(object):

    def __init__(self, depth=1, moduleLevel=False, allowed_scope=None):
        scope, module, f_locals, f_globals, codeinfo = \
            getFrameInfo(sys._getframe(depth + 1))

        if allowed_scope and scope not in allowed_scope: # pragma: no cover
            raise TypeError("This directive is not allowed "
                            "to run in this scope: %s" % scope)

        if scope == 'module':
            self.name = f_locals['__name__']
        else:
            self.name = codeinfo[2]

        self.locals = f_locals
        self.scope = scope
        self.module = module
        self.codeinfo = CodeInfo(
            codeinfo[0], codeinfo[1], codeinfo[2], codeinfo[3], module.__name__)

        if depth > 1:
            _, mod, _, _, ci = getFrameInfo(sys._getframe(2))
            self.hash = (module.__name__, codeinfo[1], mod.__name__, ci[1])
        else:
            self.hash = (module.__name__, codeinfo[1])

    @property
    def context(self): # pragma: no cover
        if self.scope == 'module':
            return self.module
        else:
            return getattr(self.module, self.name, None)

    def _runaction(self, action, cfg):
        cfg.__ptah_action__ = action
        action(cfg)

    def attach(self, action, cfg=None, depth=1):
        action.info = self
        if action.hash is None:
            action.hash = self.hash

        data = getattr(self.module, ATTACH_ATTR, None)
        if data is None:
            data = AttachData()
            setattr(self.module, ATTACH_ATTR, data)

        if cfg is None and action.hash in data:
            raise TypeError(
                "Directive registered twice: %s" % (action.discriminator,))
        data[action.hash] = action

        def callback(context, name, ob):
            config = context.config.with_package(self.module)

            config.info = action.info
            config.action(
                action.discriminator, self._runaction, (action, config),
                introspectables=action.introspectables,
                order=action.order)

        if cfg is not None:
            cfg.action(
                action.discriminator,
                self._runaction, (action, cfg),
                introspectables=action.introspectables, order=action.order)
        else:
            venusian.attach(data, callback, category='ptah', depth=depth+1)

    def __repr__(self):
        filename, line, function, source, module = self.codeinfo
        return ' File "%s", line %d, in %s\n' \
               '      %s\n' % (filename, line, function, source)


handlers = []
_handler_int = signal.getsignal(signal.SIGINT)
_handler_term = signal.getsignal(signal.SIGTERM)


def shutdown_handler(handler):
    """ register shutdown handler """
    handlers.append(handler)
    return handler


def shutdown():
    """ Execute all registered shutdown handlers """
    for handler in handlers:
        try:
            handler()
        except:
            log.exception("Showndown handler: %s"%handler)
            pass


def process_shutdown(sig, frame):
    """ os signal handler """
    shutdown()

    if sig == signal.SIGINT and callable(_handler_int):
        _handler_int(sig, frame)

    if sig == signal.SIGTERM and callable(_handler_term):  # pragma: no cover
        _handler_term(sig, frame)

    if sig == signal.SIGTERM:
        raise sys.exit()


def install_sigterm_handler(): # pragma: no cover
    try:
        import mod_wsgi
    except ImportError:
        signal.signal(signal.SIGINT, process_shutdown)
        signal.signal(signal.SIGTERM, process_shutdown)
