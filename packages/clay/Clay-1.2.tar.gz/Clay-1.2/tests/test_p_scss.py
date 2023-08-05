# -*- coding: utf-8 -*-
import shutil

from clay import p_scss
import pytest

from tests.utils import *


def setup_module():
    try:
        shutil.rmtree(clay_.build_dir)
    except OSError:
        pass


def teardown_module():
    try:
        shutil.rmtree(clay_.build_dir)
    except OSError:
        pass


SRC_SCSS = """
@option compress: no;
.selector {
    a {
        display: block;
    }
        strong {
        color: blue;
    }
}
""".strip()

EXPECTED_SCSS = """
.selector a {
  display: block;
}
.selector strong {
  color: #0000ff;
}
""".strip()

FILENAME_IN = 'sassy.scss'
FILENAME_OUT = 'sassy.css'

HTML = """
<link rel="stylesheet" href="foo/bar/%s" />
<p class="scss"></p>"""

SRC_HTML = HTML % FILENAME_IN
EXPECTED_HTML = HTML % FILENAME_OUT


def test_scss_render():
    filepath = make_view(FILENAME_IN, SRC_SCSS)
    try:
        resp = c.get('/' + FILENAME_IN)
        content = resp.data.strip()
        assert content == EXPECTED_SCSS
    finally:
        remove_file(filepath)


def test_scss_build():
    filepath = make_view(FILENAME_IN, SRC_SCSS)
    filepath_out = get_build_filepath(FILENAME_OUT)
    try:
        clay_.build()
        content = read_file(filepath_out).strip()
        assert content == EXPECTED_SCSS
    finally:
        remove_file(filepath)
        remove_file(filepath_out)


def test_scss_html_replace():
    static_filepath = make_view(FILENAME_IN, SRC_SCSS)
    filepath_out = get_build_filepath(FILENAME_OUT)
    html_filename = 'test_scss.html'
    html_filepath = make_view(html_filename, SRC_HTML)
    html_filepath_out = get_build_filepath(html_filename)
    try:
        clay_.build()
        content = read_file(html_filepath_out)
        assert content == EXPECTED_HTML
    finally:
        remove_file(static_filepath)
        remove_file(filepath_out)
        remove_file(html_filepath)
        remove_file(html_filepath_out)

