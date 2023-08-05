from distutils.core import setup


long_description = \
"""
M30W is a program designed to allow fast
developing of Scratch projects.
It uses a unique text syntax to allow typing of
blocks rather than laggy dragging them around.
"""

setup(name="M30W",
      version="0.0.12",
      maintainer="roijac",
      maintainer_email="roi.jacoboson1@gmail.com",
      url="http://scratch.mit.edu/forums/viewtopic.php?id=106225",
      install_requires=['kurt', 'PIL', 'wxpython'],\
      packages=['M30W', 'M30W', 'M30W.compiler', 'M30W.GUI',
                'M30W.parser', 'M30W.sprites'],
      package_data={'M30W': ['icons/*', 'COPYING.txt']},
      scripts=['scripts/M30W.pyw'],
      description="""GUI text-based interface to Scratch (by MIT) projects.""",
      long_description=long_description,
      license="GPL3")
