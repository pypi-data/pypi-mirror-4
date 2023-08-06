


def test_compile():
    try:
        import tiddlywebplugins.migrate
        assert True
    except ImportError, exc:
        assert False, exc
