from browse import *


def test_browse():
    
    browse("http://pypi.python.org", verbose=True)
    import webbrowser
