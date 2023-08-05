#!/usr/bin/env python

from distutils.core import setup

setup(name="lsprofcalltree",
      description="lsprof output which is readable by kcachegrind",
      author="David Allouche, Jp Calderone, Itamar Shtull-Trauring and Johan Dahlin",
      author_email='gward@python.net',
      url="http://people.gnome.org/~johan/lsprofcalltree.py",
      py_modules=["lsprofcalltree"],
     )
