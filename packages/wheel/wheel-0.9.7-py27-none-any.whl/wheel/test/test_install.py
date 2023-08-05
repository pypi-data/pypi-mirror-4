# Test wheel.
# The file has the following contents:
#   hello.pyd
#   hello/hello.py
#   hello/__init__.py
#   test-1.0.data/data/hello.dat
#   test-1.0.data/headers/hello.dat
#   test-1.0.data/scripts/hello.sh
#   test-1.0.dist-info/WHEEL
#   test-1.0.dist-info/METADATA
#   test-1.0.dist-info/RECORD
# The root is PLATLIB
# So, some in PLATLIB, and one in each of DATA, HEADERS and SCRIPTS.

import wheel.util
from wheel.install import WheelFile
from tempfile import mkdtemp
import shutil
import os

THISDIR = os.path.dirname(__file__)
TESTWHEEL = os.path.join(THISDIR, 'test-1.0-py2.py3-none-win32.whl')

def check(*path):
    return os.path.exists(os.path.join(*path))

def test_install():
    whl = WheelFile(TESTWHEEL)
    tempdir = mkdtemp()
    def generate_supported():
        return list(wheel.util.generate_supported()) + [('py3', 'none', 'win32')]
    assert whl.supports_current_python(generate_supported)
    try:
        locs = {}
        for key in ('purelib', 'platlib', 'scripts', 'headers', 'data'):
            locs[key] = os.path.join(tempdir, key)
            os.mkdir(locs[key])
        whl.install(overrides=locs)
        assert len(os.listdir(locs['purelib'])) == 0
        assert check(locs['platlib'], 'hello.pyd')
        assert check(locs['platlib'], 'hello', 'hello.py')
        assert check(locs['platlib'], 'hello', '__init__.py')
        assert check(locs['data'], 'hello.dat')
        assert check(locs['headers'], 'hello.dat')
        assert check(locs['scripts'], 'hello.sh')
        assert check(locs['platlib'], 'test-1.0.dist-info', 'RECORD')
    finally:
        shutil.rmtree(tempdir)
