"""Sanity checks for package import."""

import importlib


def test_package_importable():
    assert importlib.import_module("living_engine")
