def hide_imports(hidden):
    def capture(f):
        def captured(*args, **kwargs):
            import sys
            for k in sys.modules.keys():
                if 'mahotas' in k or 'numpy' in k:
                    del sys.modules[k]
            original_import = __builtins__['__import__']
            def masked_import(name, global_ns={}, local_ns={}, fromlist=[], *rest):
                if name in hidden:
                    raise ImportError, "Hidden package"
                for n in (fromlist or []):
                    if n in hidden:
                        raise ImportError, "Hidden package"
                return original_import(name, global_ns, local_ns, fromlist, *rest)
            __builtins__['__import__'] = masked_import
            try:
                f()
            finally:
                __builtins__['__import__'] = original_import
        return captured
    return capture


def test_hide_imports():
    from nose.tools import raises
    @raises(ImportError)
    @hide_imports(['numpy'])
    def import_imread():
        import numpy
    import_imread()
    import numpy # should be restored

def test_hide_imports_other():
    @hide_imports(['numpy'])
    def import_imread():
        import os
    import numpy
