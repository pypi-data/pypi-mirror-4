
""" ``patches`` module.
"""


def patch_strptime_cache_size(max_size=100):
    """ Patch for strptime regex cache max size.
    """
    try:  # pragma: nocover
        import _strptime
        if not hasattr(_strptime, '_CACHE_MAX_SIZE'):
            return False
        if not hasattr(_strptime, '_cache_lock'):
            return False
    except (ImportError, AttributeError):  # pragma: nocover
        return False

    l = _strptime._cache_lock
    l.acquire()
    try:
        _strptime._CACHE_MAX_SIZE = max_size
    finally:
        l.release()
    return True
