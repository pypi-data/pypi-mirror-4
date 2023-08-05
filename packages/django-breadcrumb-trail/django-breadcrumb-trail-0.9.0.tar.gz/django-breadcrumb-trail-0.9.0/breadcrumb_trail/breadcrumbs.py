from django.core.urlresolvers import resolve, get_script_prefix
import re

CAMELCASE_BOUNDRY = '(((?<=[a-z])[A-Z])|([A-Z](?![A-Z]|$)))'


def breadcrumbs(url_or_request):
    """
    Given a url returns a list of breadcrumbs,
    which are each a tuple of (name, url).
    """
    prefix = get_script_prefix().rstrip('/')
    url = getattr(url_or_request, 'path', url_or_request)
    url = url[len(prefix):]
    ret = resolve_views(url, [], prefix)
    return [(view_to_name(view), url) for (view, url) in ret]


def resolve_views(url, resolve_list, prefix):
    """
    Add tuples of (view, url) to the breadcrumbs list,
    progressively chomping off parts of the url.
    """

    try:
        view = resolve(url)[0]
    except Exception:
        pass
    else:
        # Don't add the same view in consecutively.
        # Probably resolving an optional trailing slash.
        if not resolve_list or resolve_list[0][0] != view:
            resolve_list.insert(0, (view, prefix + url))

    if url == '':
        # All done
        return resolve_list

    elif url.endswith('/'):
        # Drop trailing slash off the end and continue to try to resolve more breadcrumbs
        return resolve_views(url.rstrip('/'), resolve_list, prefix)

    # Drop trailing non-slash off the end and continue to try to resolve more breadcrumbs
    return resolve_views(url[:url.rfind('/') + 1], resolve_list, prefix)


def view_to_name(view):
    """
    Given a view return a humanized string representation
    """
    name = view.__name__
    # Tokenize on CamelCaseBoundaries (class based views)
    name = re.sub(CAMELCASE_BOUNDRY, ' \\1', name)
    # Tokenize on underscores (function based views)
    name = name.replace('_', ' ')
    # Any all-lowercase tokens -> Title Case
    name = ' '.join([token.lower() == token and token.title() or token
                    for token in name.split()])
    # Remove trailing 'View' if it exists
    return name.endswith(' View') and name[:-5] or name
