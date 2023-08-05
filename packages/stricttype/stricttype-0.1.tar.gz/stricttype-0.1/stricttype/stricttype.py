import types

classobj = types.ClassType

def check_base_type(arg, nested=False):
    msgs = []

    if isinstance(arg, tuple) and not nested:
        [check_base_type(a, True) for a in arg]

    try:
        assert type(arg) == type or type(arg) == classobj
    except AssertionError:
        msgs.append('{arg} is not basetype, but `{actual_type}`'.format(arg=arg, actual_type=type(arg).__name__))
 
    if msgs:
        print ' '.join(msgs)
        raise AssertionError


def mydeco(fn, *args, **kwargs):
    def wrapper(*args2, **kwargs2):
        return_type = kwargs.pop('return_type', None)

        map(check_base_type, args)

        msgs = []

        if len(args) != len(args2):
            print 'Length of types: {}, length of args: {}'
            return

        for i, arg in enumerate(args):
            try:
                assert isinstance(args2[i], args[i]) 
            except AssertionError:
                msgs.append('{arg} is not instance of `{expected_type}`, but `{actual_type}`'.format(arg=args2[i], expected_type=args[i].__name__, actual_type=type(args2[i]).__name__))

        for key in kwargs2:
            try:
                assert isinstance(kwargs2[key], kwargs[key]) 
            except AssertionError:
                msgs.append('{arg} is not instance of `{expected_type}`, but `{actual_type}`'.format(arg=kwargs2[key], expected_type=kwargs[key].__name__, actual_type=type(kwargs2[key].__name__)))

        if not msgs:
            if not return_type:
                return fn(*args2, **kwargs)

            ret_val = fn(*args2, **kwargs)
            try:
                assert isinstance(ret_val, return_type) 
            except AssertionError:
                msgs.append('{arg} is not instance of `{expected_type}`, but `{actual_type}`'.format(arg=ret_val, expected_type=return_type.__name__, actual_type=type(ret_val).__name__))
                print ' '.join(msgs)

    return wrapper
