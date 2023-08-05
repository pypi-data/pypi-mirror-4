# coding=utf8

import py
pytest_plugins = "pytester",


def test_version():
    import pytest_pep8
    assert pytest_pep8.__version__


class TestIgnores:
    def pytest_funcarg__example(self, request):
        testdir = request.getfuncargvalue("testdir")
        p = testdir.makepyfile("")
        p.write("class AClass:\n    pass\n       \n\n#too many spaces")
        return p

    def test_ignores(self, tmpdir):
        from pytest_pep8 import Ignorer
        ignores = ["E203", "b/?.py E204 W205", "z.py ALL", "*.py E300"]
        ign = Ignorer(ignores)
        assert ign(tmpdir.join("a/b/x.py")) == "E203 E204 W205 E300".split()
        assert ign(tmpdir.join("a/y.py")) == "E203 E300".split()
        assert ign(tmpdir.join("a/z.py")) is None

    def test_ignores_all(self, testdir):
        from pytest_pep8 import Ignorer
        testdir.makeini("""
            [pytest]
            pep8ignore = E203
                *.py E300
                tests/*.py ALL E203 # something
        """)
        testdir.tmpdir.ensure("xy.py")
        testdir.tmpdir.ensure("tests/hello.py")
        result = testdir.runpytest("--pep8", "-s")
        assert result.ret == 0
        result.stdout.fnmatch_lines([
            "*collected 1*",
            "*xy.py .*",
            "*1 passed*",
        ])

    def test_w293w292(self, testdir, example):
        result = testdir.runpytest("--pep8", )
        result.stdout.fnmatch_lines([
            #"*plugins*pep8*",
            "*W293*",
            "*W292*",
        ])
        assert result.ret != 0

    def test_mtime_caching(self, testdir, example):
        testdir.tmpdir.ensure("hello.py")
        result = testdir.runpytest("--pep8", )
        result.stdout.fnmatch_lines([
            #"*plugins*pep8*",
            "*W293*",
            "*W292*",
            "*1 failed*1 passed*",
        ])
        assert result.ret != 0
        result = testdir.runpytest("--pep8", )
        result.stdout.fnmatch_lines([
            "*W293*",
            "*W292*",
            "*1 failed*1 skipped*",
        ])
        testdir.makeini("""
            [pytest]
            pep8ignore = *.py W293 W292
        """)
        result = testdir.runpytest("--pep8", )
        result.stdout.fnmatch_lines([
            "*2 passed*",
        ])


def test_ok_verbose(testdir):
    p = testdir.makepyfile("""
        class AClass:
            pass
    """)
    p = p.write(p.read() + "\n")
    result = testdir.runpytest("--pep8", "--verbose")
    result.stdout.fnmatch_lines([
        "*test_ok_verbose*PEP8-check*",
    ])
    assert result.ret == 0


def test_keyword_match(testdir):
    testdir.makepyfile("""
        def test_hello():
            a=[ 1,123]
            #
    """)
    result = testdir.runpytest("--pep8", "-k pep8")
    result.stdout.fnmatch_lines([
        "*E201*",
        "*1 failed*",
    ])
    assert 'passed' not in result.stdout.str()


def test_maxlinelength(testdir):
    testdir.makeini("""
        [pytest]
        pep8maxlinelength = 50
    """)
    testdir.makepyfile("""
# this line is longer than the configured max. line length
""")
    result = testdir.runpytest("--pep8", "-k pep8")
    result.stdout.fnmatch_lines([
        "*E501*",
        "*1 failed*",
    ])
    assert 'passed' not in result.stdout.str()


def test_unicode_error(testdir):
    x = testdir.tmpdir.join("x.py")
    import codecs
    f = codecs.open(str(x), "w", encoding="utf8")
    f.write(py.builtin._totext("""
# coding=utf8

accent_map = {
    u'\\xc0': 'a', # À -> a  non-ascii comment crashes it
}
""", "utf8"))
    f.close()
    result = testdir.runpytest("--pep8", x, "-s")
    result.stdout.fnmatch_lines("*non-ascii comment*")


def test_strict(testdir):
    testdir.makepyfile("")
    result = testdir.runpytest("--strict", "--pep8")
    assert result.ret == 0
