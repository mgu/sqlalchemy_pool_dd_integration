import sqlalchemy
from wrapt import wrap_function_wrapper as _w
import ddtrace
from ddtrace.pin import Pin
from ddtrace.contrib.trace_utils import unwrap


def patch():
    if getattr(sqlalchemy.pool, "__datadog_patch", False):
        return

    sqlalchemy.pool.__datadog_patch = True
    _w("sqlalchemy.pool.base", "_ConnectionRecord._ConnectionRecord__connect", _wrap_connection_record_connect)
    _w("sqlalchemy.pool.base", "_ConnectionRecord._ConnectionRecord__close", _wrap_connection_record_close)
    _w("sqlalchemy.pool.base", "Pool.connect", _wrap_pool_connect)
    _w("sqlalchemy.pool.base", "Pool._return_conn", _wrap_pool_return_conn)

def unpatch():
    # unpatch sqlalchemy
    if getattr(sqlalchemy.pool, "__datadog_patch", False):
        sqlalchemy.pool.__datadog_patch = False
        unwrap(sqlalchemy.pool.base._ConnectionRecord._ConnectionRecord__connect)
        unwrap(sqlalchemy.pool.base.Pool.connect)
        unwrap(sqlalchemy.pool.base.Pool._return_conn)

def trace_pool(pool):
    Pin(tracer=ddtrace.tracer, service="sqlalchemy.pool").onto(pool)

def _wrap_connection_record_connect(wrapped, instance, args, kwargs):
    pin = Pin.get_from(instance._ConnectionRecord__pool)
    if not pin or not pin.enabled():
        # don't trace the execution
        return wrapped(*args, **kwargs)

    with pin.tracer.trace(
        "sqlalchemy.pool.do_connect",
        service=pin.service,
        ):
        return wrapped(*args, **kwargs)

def _wrap_connection_record_close(wrapped, instance, args, kwargs):
    pin = Pin.get_from(instance._ConnectionRecord__pool)
    if not pin or not pin.enabled():
        # don't trace the execution
        return wrapped(*args, **kwargs)

    with pin.tracer.trace(
        "sqlalchemy.pool.do_close",
        service=pin.service,
        ):
        return wrapped(*args, **kwargs)

def _wrap_pool_connect(wrapped, instance, args, kwargs):
    pin = Pin.get_from(instance)
    if not pin or not pin.enabled():
        # don't trace the execution
        return wrapped(*args, **kwargs)

    with pin.tracer.trace(
        "sqlalchemy.pool.connect",
        service=pin.service,
        ) as span:
        span.set_tag("status", instance.status())
        return wrapped(*args, **kwargs)


def _wrap_pool_return_conn(wrapped, instance, args, kwargs):
    pin = Pin.get_from(instance)
    if not pin or not pin.enabled():
        # don't trace the execution
        return wrapped(*args, **kwargs)

    with pin.tracer.trace(
        "sqlalchemy.pool._return_conn",
        service=pin.service,
        ) as span:
        return wrapped(*args, **kwargs)
