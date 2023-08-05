from distutils.core import setup
from distutils.command.install import install
from distutils.sysconfig import get_python_lib
import sys, shutil, os, subprocess

desktop_file = \
"""[Desktop Entry]
Type=Application
Name=M30W
Comment=GUI text-based interface to Scratch (by MIT) projects.
Icon=m30w
Exec=M30W
Terminal=false
Categories=Application;Development
MimeType=application/x-scratch-project
"""

class my_install(install):
    def run(self):
        install.run(self)

        if not sys.platform == 'linux2':
            return
        message = "Detected linux. Install icons and .desktop file? (Y/n)"
        do_install = raw_input(message)
        while do_install.lower() not in ('y', 'n', ''):
            do_install = raw_input(message)
        if do_install == 'n': return

        print "Writing .desktop file..."
        with open('/usr/share/applications/m30w.desktop', 'w') as f:
            f.write(desktop_file)

        print "Copying icon..."
        icons_path = os.path.join(self.install_lib, 'M30W', 'icons')
        shutil.copyfile(os.path.join(icons_path, 'm30w.png'),
                        '/usr/share/icons/hicolor/128x128/apps/m30w.png')

        #Different commands that update icons cache and such. Tried to be as
        #cross-dist as possible
        try:
            subprocess.call(['gtk-update-icon-cache',
                             '-qf', 
                             '/usr/share/icons/hicolor'])
        except OSError:
            pass
        try:
            subprocess.call('update-desktop-database')
        except OSError:
            pass
        try:
            subprocess.call('kbuildsycoca')
        except OSError:
            pass

long_description = \
"""
M30W is a program designed to allow fast
developing of Scratch projects.
It uses a unique text syntax to allow typing of
blocks rather than laggy dragging them around.
"""

scripts = ['scripts/M30W']
if 'bdist_wininst' in sys.argv:
    scripts = ['scripts/M30W_post_install.py']

setup(name="M30W",
      version="0.1.0",
      maintainer="roijac",
      maintainer_email="roi.jacoboson1@gmail.com",
      url="http://scratch.mit.edu/forums/viewtopic.php?id=106225",
      install_requires=['kurt', 'PIL', 'wxpython'],
      packages=['M30W', 'M30W', 'M30W.compiler', 'M30W.GUI',
                'M30W.parser', 'M30W.sprites'],
      package_data={'M30W': ['icons/*', 'COPYING.txt']},
      scripts=scripts,
      description="""GUI text-based interface to Scratch (by MIT) projects.""",
      long_description=long_description,
      license="GPL3",
      cmdclass={'install': my_install})
