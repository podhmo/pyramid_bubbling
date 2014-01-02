# -*- coding:utf-8 -*-
print("""
pyramid_bubbling
================

bubbling event

sample
----------------------------------------
""")
import os
import sys


out = os.popen("../bin/python {}".format(sys.argv[1]))
print("output ::")
print("")
for line in out.readlines():
    print("   ", line.rstrip())
print("")

for f in sys.argv[1:]:
    print(f)
    print("::")
    print("")
    with open(f) as rf:
        for line in rf.readlines():
            print("   ", line.rstrip())
