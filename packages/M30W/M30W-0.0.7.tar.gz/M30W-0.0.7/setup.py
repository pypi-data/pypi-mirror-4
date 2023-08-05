from distutils.core import setup

setup(name="M30W",
      version="0.0.7",
      packages=['M30W', 'M30W', 'M30W.compiler', 'M30W.GUI',
                'M30W.parser', 'M30W.sprites'],
      package_data={'M30W': ['icons/*', 'COPYING.txt']},
      maintainer="roijac",
      scripts=['scripts/M30W'],
      maintainer_email="roi.jacoboson1@gmail.com",
      description="""GUI text-based interface to Scratch (by MIT) projects.""",
      license="GPL3")