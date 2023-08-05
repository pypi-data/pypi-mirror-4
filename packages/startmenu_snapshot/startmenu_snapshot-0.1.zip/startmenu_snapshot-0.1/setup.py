from setuptools import setup

setup(name='startmenu_snapshot',
        version='0.1',
        description="Takes a 'photo' of the winxp startmenu as a memory aid.",
        long_description="""\
        This script recreates the winxp startmenu from the directory contents of 'All users'/startmenu 
        and $userprofile$/startmenu. It can save the structure and the program icons to a pickled file
        and later reload from the file. So this is mostly useful for remembering which programs that 
        you had installed on another computer and how your start menu looked.
        """,
        classifiers=[
          "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
          "Programming Language :: Python",
          "Development Status :: 4 - Beta",
          "Environment :: Win32 (MS Windows)",
          "Intended Audience :: End Users/Desktop",
          "Intended Audience :: System Administrators",
          "Natural Language :: English",
          "Operating System :: Microsoft :: Windows :: Windows XP",
          "Topic :: System :: Archiving",
          "Topic :: Utilities"
           ],
        author='robochat',
        author_email='rjsteed@talk21.com',
        url='https://sourceforge.net/projects/start-snapshot/',
        license='GPLv3',
        keywords='start-menu',
        py_modules=['startmenu_snapshot','setup','setup2'], # this is too small to setup a package system
        scripts=['startmenu_snapshot.py'],
        data_files=[('',['COPYING','README'])],
        install_requires=['pywin32','wxPython'],
        zip_safe=False
        )


