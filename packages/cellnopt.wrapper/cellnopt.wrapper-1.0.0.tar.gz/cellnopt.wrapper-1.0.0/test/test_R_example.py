import rpy2
from rpy2 import robjects


def test_R_function():
    robjects.r('''
        f <- function(r, verbose=FALSE) {
            if (verbose) {
                cat("I am calling f().\n")
            }
            2 * pi * r
        }
        f(3)
        ''')
    r_f = robjects.r['f']

    assert r_f(3)[0]>18.84 and r_f(3)[0]<18.85  # should be a better test, but this is
                                                # just to demonstrate the usage or R
                                                # code inside ryp2 and python

    #<FloatVector - Python:0x5742290 / R:0x571d668>
    #[18.849556]

