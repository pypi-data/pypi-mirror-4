

def test_compile():
    try:
        import tiddlywebplugins.pkgstore
        assert True
    except ImportError, exc:
        assert False, exc
