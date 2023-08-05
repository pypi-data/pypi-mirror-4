from pyDatalog import pyDatalog

pyDatalog.pyEngine.Trace = True
pyDatalog.pyEngine.Debug = True

def test():
    @pyDatalog.program() # indicates that the following method contains pyDatalog clauses
    def _():
        # odd and even
        + even(0)
        even(N) <= (N > 0) & odd(N-1)
        odd(N) <= (N > 0) & ~ even(N)
        assert ask((X==1) & odd(X+2)) == set([(1,3)])
test()