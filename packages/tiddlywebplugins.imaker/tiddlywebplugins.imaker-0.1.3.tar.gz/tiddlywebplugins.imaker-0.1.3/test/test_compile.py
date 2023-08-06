

def test_compile():
    try:
        import tiddlywebplugins.imaker
        assert True
    except ImportError, exc:
        assert False, exc
