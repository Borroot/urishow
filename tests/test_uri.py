import sys, os
sys.path.append(os.path.realpath(os.path.dirname(__file__)+"/../src/urishow/"))

import pytest
from main import _extract


def test_extract_simple_single():
    cases = [
        'https://www.example.com',
        'mailto://www.example.com',
    ]

    for case in cases:
        uris = _extract(case)
        assert len(uris) == 1
        assert uris[0]   == case
