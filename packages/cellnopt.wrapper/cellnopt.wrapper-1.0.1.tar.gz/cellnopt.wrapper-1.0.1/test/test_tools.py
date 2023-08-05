""" test tools module

Most of the tools in this module are tested indirectly in other modules.
"""
from cellnopt.wrapper.tools import *
from cellnopt.data import get_data


class Counter(object):
    def __init__(self):
        pass



class Require():

    def __init__(self):
        self.m = Counter() # just a dummy class to play with.
        setattr(self.m, 'm', 1) # set a second level

    @require('m', 'no error message')  
    def test_require(self):
        """normal usage of require"""
        print self.m

    @require('a', 'a does not exist')
    def test_require_error(self):
        pass

    @require('m.a', 'm.a does not exist')
    def test_require_error_2_levels(self):
        pass

    @require('m.m', 'no error message')
    def test_require_2_levels(self):
        print self.m.m


def test_require():
   # simple test of require decorator using the class defined above
   r = Require()
   r.test_require()
   r.test_require_2_levels()
   try:
        r.test_require_error()
        assert False
   except:
        assert True
   try:
        r.test_require_error_2_levels()
        assert False
   except:
        assert True



def test_ErrorRequire1():
    """Test wrong usage fo require decorator. The class declaration is failing
    (normal behaviour), so put it inside the try/except"""
    try:
        class ErrorRequire1():
            def __init__():
                self.m = 1
        @require('m')
        def test_require_error2(self):
            pass
        r = ErrorRequire1()
        assert False
    except:
        assert True

def test_ErrorRequire2():
    """Test wrong usage fo require decorator. The class declaration is failing
    (normal behaviour), so put it inside the try/except"""
    try:
        class ErrorRequire2():
            def __init__():
                self.m = 1
        @require('m.m.m', 'error message')
        def test_require_error2(self):
            pass
        r = ErrorRequire2()
        assert False
    except:
        assert True


def test_get_data():
    f = get_data('ToyModelMKM.sif')
    try:
        f = get_data('dummy')
        assert False
    except:
        assert True
