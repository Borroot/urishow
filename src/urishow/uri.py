import re


def extract_mail():
    pass


def extract_url():
    pass


def extract(text: str) -> [str]:
    """
    Extract all the uris from the given text.
    """

    # TODO Recognize the uris from a context.
    regex = '^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?'
    for match in re.findall(regex, text):
        scheme    = match[1]
        authority = match[3]
        path      = match[4]
        query     = match[6]
        fragment  = match[8]
        print("{}{}{}{}{}".format(scheme, authority, path, query, fragment))
