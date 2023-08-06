def is_edit_url(url):
    """Is the url a url for editing?

    We use 127.0.0.1 for editing and localhost for viewing::

    >>> is_edit_url('http://localhost/')
    False
    >>> is_edit_url('http://127.0.0.1/')
    True

    Urls starting with 'edit', 'cms', 'manage' or 'admin' are editing urls.

    >>> is_edit_url('http://edit.google.com/')
    True
    >>> is_edit_url('http://edit.google.com')
    True
    >>> is_edit_url('http://cms.google.com/')
    True
    >>> is_edit_url('http://admin.google.com/')
    True
    >>> is_edit_url('http://google.com/')
    False
    >>> is_edit_url('http://www.google.com/')
    False

    In case our normal domain name is also "edit-like", we have to be
    careful::

    >>> is_edit_url('http://edit.com/')
    False
    >>> is_edit_url('http://edit.edit.com/')
    True
    >>> is_edit_url('http://www.edit.com/')
    False

    Some other protocals should be fine as well::

    >>> is_edit_url('https://edit.google.com/')
    True
    >>> is_edit_url('ftp://edit.google.com/')
    True
    >>> is_edit_url('https://google.com/')
    False
    >>> is_edit_url('ftp://google.com/')
    False

    If we do not see a protocol, we are not a url, so definitely not
    an edit url::

    >>> is_edit_url('edit.google.com/')
    False

    Let's try to crash this function::

    >>> is_edit_url('')
    False
    >>> is_edit_url(0)
    False
    >>> is_edit_url(3.14)
    False
    >>> is_edit_url(object())
    False
    >>> is_edit_url(is_edit_url)
    False
    >>> is_edit_url(u'http://cms.google.com/')
    True
    >>> is_edit_url(u'http://google.com/')
    False
    >>> is_edit_url(u'http://...////')
    False
    >>> is_edit_url(u'http://www.nothing.com//edit.nothing.com/')
    False

    """
    if not isinstance(url, basestring):
        return False
    protocolend = url.find("//")
    if protocolend == -1:
        # No url
        return False
    url = url[protocolend+2:]
    domain = url.split('/')[0]
    # Note: domain could be mydomain.com:8080 here but we do not care.
    parts = domain.split('.')
    if len(parts) < 3:
        return False
    if domain.startswith('127.0.0.1'):
        return True
    if parts[0] not in ('edit', 'cms', 'manage', 'admin'):
        return False
    return True
