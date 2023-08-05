# -*- coding: utf-8 -*-
import io
import os

from clay.manage import new, build, run, get_settings, get_current
import pytest


def get_cwd():
    return os.path.dirname(os.path.abspath(__file__)) or '.'


def test_get_settings():
    cwd = get_cwd()
    settings = get_settings(cwd, filename='_test.yml')
    assert settings


def test_get_current():
    os.chdir(os.path.dirname(__file__))
    expected = os.getcwd()
    clay_ = get_current()
    assert clay_.base_dir == expected

