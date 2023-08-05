
def superhash(anything, try_anyway=True):
    """takes anything. returns a hash of the anything."""
    
    xhash = 0

    try:
        # does it have attributes we should take into account?
        xhash ^= superhash(anything.__dict__)
    except AttributeError:
        pass
    
    # is it functional?
    try:
        xhash ^= superhash(anything.func_code)  # Python 2.x (for x >= 6 at least)
        return hash(xhash)
    except AttributeError:
        try:
            xhash ^= superhash(anything.__code__)   # Python 3
            return hash(xhash)
        except AttributeError:
            pass
    except AttributeError:
        pass
    
    try:
        if try_anyway:
            # can python hash it already?
            xhash ^= hash(anything)
        else:
            raise TypeError('can\'t hash that')
    except TypeError:
        try:
            # is it dict-like?
            for item in anything.items():
                xhash ^= superhash(item)
        except AttributeError:
            try:
                # is it iterable?
                for item in anything:
                    xhash ^= superhash(item)
            except TypeError:
                pass
    
    return hash(xhash)
