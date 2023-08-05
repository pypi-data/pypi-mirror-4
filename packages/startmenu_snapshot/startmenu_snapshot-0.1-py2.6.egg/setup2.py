# ...
# ModuleFinder can't handle runtime changes to __path__, but win32com uses them
try:
    # py2exe 0.6.4 introduced a replacement modulefinder.
    # This means we have to add package paths there, not to the built-in
    # one.  If this new modulefinder gets integrated into Python, then
    # we might be able to revert this some day.
    # if this doesn't work, try import modulefinder
    try:
        import py2exe.mf as modulefinder
    except ImportError:
        import modulefinder
    import win32com, sys
    for p in win32com.__path__[1:]:
        modulefinder.AddPackagePath("win32com", p)
    for extra in ["win32com.shell"]: #,"win32com.mapi"
        __import__(extra)
        m = sys.modules[extra]
        for p in m.__path__[1:]:
            modulefinder.AddPackagePath(extra, p)
except ImportError:
    # no build path setup, no worries.
    pass

from distutils.core import setup
import py2exe

setup(console=['startmenu_snapshot.py'],
      options={"py2exe":{"optimize": 2,"bundle_files": 1,
                                "excludes":['doctest','pdb','unitest','difflib',
                                                'inspect','calender']}},
      zipfile=None
    )
  
#compile with python -OO setup2.py py2exe to get optimised code even in top module

"""  
setup(console=['bookmark_merger.py'],
      options={"py2exe":{"optimize": 0,"bundle_files": 3,
                                "excludes":['doctest','pdb','unitest','difflib',
                                                'inspect','pickle','calender']}},
    )
"""