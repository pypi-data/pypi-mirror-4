from __future__ import absolute_import

import string
assert not hasattr(string, 'foo'), "fail"
print("success")