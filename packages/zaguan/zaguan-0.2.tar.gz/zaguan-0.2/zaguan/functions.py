import gobject

from zaguan.constants import WEBKIT, GECKO


def get_implementation():
    try:
        import webkit
        have_webkit = True
    except:
        have_webkit = False

    try:
        import gtkmozembed
        have_gtkmozembed = True
    except:
        have_gtkmozembed = False

    if have_webkit:
        implementation = WEBKIT
    elif have_gtkmozembed:
        implementation = GECKO
    else:
        raise Exception('Fallo al importar modulo de webkit o gtkmozembed')
    return implementation

def asynchronous_gtk_message(fun):
    def worker((function, args, kwargs)):
        apply(function, args, kwargs)

    def fun2(*args, **kwargs):
        gobject.idle_add(worker, (fun, args, kwargs))

    return fun2
