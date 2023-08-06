# Annoyingly, this does not replicate the error.
import sys
import os
import shutil
import tempfile
import importlib

dir = tempfile.mkdtemp().replace("\\", "/")

pkg = ["{}/pkg{}".format(dir, i) for i in 0, 1]

os.makedirs(pkg[0])

sys.path.append(dir)

os.makedirs(pkg[1])

for i in 0, 1:
    with open(os.path.join(pkg[i], "__init__.py"), "w") as f:
        f.write('"""__init__ file required for package directory."""')
    with open(os.path.join(pkg[i], "module{}.py".format(i)), "w") as f:
        f.write('print "Importing module{} from {}"'.format(i, pkg[i]))
    print "hello"
    importlib.import_module("pkg{}.module{}".format(i, i), "pkg{}".format(i))

shutil.rmtree(dir)
