from src.urlshow.url import extract
import pytest


def test_extract_simple_single():
    cases = [
        'example.com',
        'www.example.com',
        'https://www.example.com',
    ]

    for case in cases:
        urls = extract(case)
        assert len(urls) == 1
        assert urls[0]   == case
