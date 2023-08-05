
try:
    unicode
except NameError:
    # Python 3
    basestring = unicode = str

version = '1.0'

def normalize_chain(chain):
    """
    Convenience method formatting attribute chain into iterables.
    """
    if isinstance(chain, (str, unicode)):
        chain = chain.split('.')

    if not isinstance(chain, (list, tuple)):
        raise Exception
    return chain


def broken(obj, chain):
    """Return name of attribute where the chain
    is broken.

    If chain is not broken (all attributes are represented in chain)
    nothing is returned."""
    chain = normalize_chain(chain)

    for attr in chain:
        obj = getattr(obj, attr, None)
        if not obj:
            return attr


def get(obj, chain, *args):
    """Recursively walk chain. Return the value
    of the final named attribute in the chain.

    If a named attribute does not exist,
    default is returned if provided, otherwise AttributeError is raised.

    Replaces doing things like:
    object.attr1.attr2.attr3 if object and object.attr1.attr2 else None

    or

    getattr(getattr(getattr(object, 'attr1', ''), 'attr2', ''), 'attr3', None)
    """
    dflt_set = False

    if args:
        if len(args) != 1:
            raise TypeError('{0} expected at most 3 arguments, got {1}'.format(
                'get', len(args)))
        dflt = args[0]
        dflt_set = True

    chain = normalize_chain(chain)

    for attr in chain:
        obj = getattr(obj, attr, dflt) if dflt_set else getattr(obj, attr)
    return obj


def has(obj, chain):
    """The result is True if the all attributes in the chain exist, False if not.
    (This is implemented by calling get(object, chain) and seeing
    whether it raises an exception or not.)"""
    try:
        get(obj,chain)
    except AttributeError:
        return False
    return True


def walk(obj, chain):
    """Recursively walk chain. Return the value
    of the each named attribute in the chain.

    If a named attribute does not exist,
    AttributeError is raised.
    """
    chain = normalize_chain(chain)

    for attr in chain:
        obj = getattr(obj, attr)
        yield obj
