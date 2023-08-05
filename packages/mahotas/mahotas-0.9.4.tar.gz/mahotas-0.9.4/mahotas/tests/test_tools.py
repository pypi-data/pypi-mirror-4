from mahotas.tests.tools import hide_imports

def test_hide_imports():
    from nose.tools import raises
    @raises(ImportError)
    @hide_imports(['numpy'])
    def import_numpy():
        import numpy
    import_numpy()
    import numpy # should be restored

def test_hide_imports_other():
    @hide_imports(['numpy'])
    def import_numpy():
        import os
    import numpy
