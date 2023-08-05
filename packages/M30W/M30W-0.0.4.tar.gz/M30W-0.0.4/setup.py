from distutils.core import setup

setup(name="M30W",
      version="0.0.4",
      py_modules=["M30W", 'setup'],
      packages=['core', 'core.compiler', 'core.GUI',
                'core.parser', 'core.sprites'],
      package_data={'core': ['icons/*']},
      maintainer="roijac")