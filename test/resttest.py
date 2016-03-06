# -*- coding: utf-8 -*-

import os
a  = os.popen('iostat -n0 | awk \'{ print $1 }\' | tail -1').readlines()[0]
print(a)