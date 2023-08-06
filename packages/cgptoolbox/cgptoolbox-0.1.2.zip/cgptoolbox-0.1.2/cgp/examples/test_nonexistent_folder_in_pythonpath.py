import sys
import shutil
import os

tempdir = "c:/temp/temp"

try:
    import folder.module
    print folder.module
except ImportError:
    pass

# Uncomment this to see the error.
# if os.path.exists(tempdir):
#     shutil.rmtree(tempdir)

sys.path.append(tempdir)

try:
    import folder.module
    print folder.module
except ImportError:
    pass

os.makedirs(os.path.join(tempdir, "folder"))
with open(os.path.join(tempdir, "folder", "__init__.py"), "w") as f:
    pass
with open(os.path.join(tempdir, "folder", "module.py"), "w") as f:
    f.write("print 'Importing module'")

import folder.module