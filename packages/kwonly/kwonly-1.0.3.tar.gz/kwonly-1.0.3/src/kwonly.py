import inspect
import sys

import decorator

NoDefault = object()

def reverse(x):
    l = list(x)
    l.reverse()
    return l

if sys.version_info < (3,):
    def kwonly(idx):
        def decorate(f):
            args, varargs, keywords, defaults = inspect.getargspec(f)
            defaults = defaults or ()

            default_map = dict(zip(reverse(args), reverse(defaults)))

            positional_args = args[:idx]
            kwonly_args = args[idx:]

            # Construct the parameters of the function signature
            param_decls = []

            for arg in positional_args:
                if arg in default_map:
                    param_decls.append('%s=%r' % (arg, default_map[arg]))
                else:
                    param_decls.append(arg)

            if varargs:
                param_decls.append('*%s' % varargs)

            # We need keyword arguments even if the original function didn't
            # accept them because that's how we'll take in the keyword-only
            # arguments
            if not keywords:
                keywords = 'restricted_kwargs'
            param_decls.append('**%s' % keywords)

            signature = '%s(%s)' % (f.__name__, ', '.join(param_decls))

            # Construct the source of the wrapper function
            source = []

            # We'll pop the keyword-only arguments out of the keyword arguments
            # when we call the wrapped function, so for each keyword-only
            # argument add code raise an exception if it wasn't provided and
            # there is no default or to put the default into the keyword
            # arguments if there is a default
            for arg in kwonly_args:
                default = default_map.get(arg, NoDefault)
                if default is NoDefault:
                    source.append('''\
if '%(argname)s' not in %(keywords)s:
    raise TypeError('%(funcname)s needs keyword-only argument %(argname)s')
''' % dict(argname=arg, keywords=keywords, funcname=f.__name__))
                else:
                    source.append('''\
if '%(argname)s' not in %(keywords)s:
    %(keywords)s['%(argname)s'] = %(default)r
''' % dict(argname=arg, keywords=keywords, default=default))

            # Construct the call to the wrapped function
            param_call = positional_args
            param_call.extend('%s.pop(\'%s\')' % (keywords, arg)
                               for arg in kwonly_args)
            if varargs:
                param_call.append('*%s' % varargs)
            param_call.append('**%s' % keywords)

            source.append('return %s_(%s)' % (f.__name__,
                                              ', '.join(param_call)))

            defaults = defaults[:idx - len(args)]
            return decorator.FunctionMaker.create(signature, ''.join(source),
                                                  {f.__name__ + '_': f},
                                                  defaults=defaults)

        return decorate

else:
    class FunctionMaker(decorator.FunctionMaker):
        def update(self, func, **kwargs):
            self.kwonlydefaults = kwargs.pop('kwonlydefaults')
            decorator.FunctionMaker.update(self, func, **kwargs)

    def kwonly(idx):
        def decorate(f):
            args, varargs, keywords, defaults = inspect.getargspec(f)
            defaults = defaults or ()

            default_map = dict(zip(reverse(args), reverse(defaults)))

            positional_args = args[:idx]
            kwonly_args = args[idx:]

            # Construct the parameters of the function signature
            param_decls = []

            for arg in positional_args:
                if arg in default_map:
                    param_decls.append('%s=%s' % (arg, default_map[arg]))
                else:
                    param_decls.append(arg)

            if varargs:
                param_decls.append('*%s' % varargs)
            else:
                param_decls.append('*')

            for arg in kwonly_args:
                default = default_map.get(arg, NoDefault)
                if default is NoDefault:
                    param_decls.append(arg)
                else:
                    param_decls.append('%s=%s' % (arg, default))

            if keywords:
                param_decls.append('**%s' % keywords)

            signature = '%s(%s)' % (f.__name__, ', '.join(param_decls))

            # Construct the source of the wrapper function
            source = []

            # Construct the call to the wrapped function
            param_call = list(args)
            if varargs:
                param_call.append('*%s' % varargs)
            if keywords:
                param_call.append('**%s' % keywords)

            source = 'return %s_(%s)' % (f.__name__, ', '.join(param_call))

            defaults = defaults[:idx - len(args)]
            kwonlydefaults = dict(
                [(k, default_map[k]) for k in kwonly_args
                 if default_map.get(k, NoDefault) is not NoDefault])
            return FunctionMaker.create(signature, ''.join(source),
                                        {f.__name__ + '_': f},
                                        defaults=defaults,
                                        kwonlydefaults=kwonlydefaults)

        return decorate


__all__ = ('NoDefault', 'kwonly')
