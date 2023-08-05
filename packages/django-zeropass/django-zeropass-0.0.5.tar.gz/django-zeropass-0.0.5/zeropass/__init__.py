version = (0, 0, 5)


def get_version():
    """returns a pep complient version number"""
    return '.'.join(str(i) for i in version)
