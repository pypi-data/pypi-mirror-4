MAX_RESULTS_PER_PAGE = 100


def all(listf, **kwargs):
    """
    Simple generator to page through all results of function `listf`.
    """
    if not kwargs.get('limit'):
        kwargs['limit'] = MAX_RESULTS_PER_PAGE

    resp = listf(**kwargs)

    for obj in resp['objects']:
        yield obj

    while resp['meta']['next']:
        limit = resp['meta']['limit']
        offset = resp['meta']['offset']
        resp = listf(offset=(offset + limit))
        for obj in resp['objects']:
            yield obj


def clean_pagename(name):
    # Pagenames can't contain a slash with spaces surrounding it.
    name = '/'.join([part.strip() for part in name.split('/')])
    return name
