from src.urishow.uri import extract
import pytest


def test_extract_simple_single():
    cases = [
        'example.com',
        'www.example.com',
        'https://www.example.com',
    ]

    for case in cases:
        uris = extract(case)
        assert len(uris) == 1
        assert uris[0]   == case
