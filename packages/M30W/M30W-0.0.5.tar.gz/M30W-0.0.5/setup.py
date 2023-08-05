from distutils.core import setup

setup(name="M30W",
      version="0.0.5",
      packages=['M30W', 'M30W.core', 'M30W.core.compiler', 'M30W.core.GUI',
                'M30W.core.parser', 'M30W.core.sprites'],
      package_data={'M30W.core': ['icons/*'],
                    'M30W': ['COPYING']},
      maintainer="roijac")