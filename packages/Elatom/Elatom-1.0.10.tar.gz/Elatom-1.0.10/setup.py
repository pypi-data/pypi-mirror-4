'''
Elatom's setup.py
classifiers from http://pypi.python.org/pypi?%3Aaction=list_classifiers
'''
__revision__ = "1.0.10"
from distutils.core import setup
import glob

PARAMS = {
    "author_email": "eliovir@gmail.com",
    "name": "Elatom",
    "url": "https://launchpad.net/elatom",
    "download_url": "https://launchpad.net/elatom/+download",
    "version": __revision__,
    "description": "Podcast downloader in Python 3 with Curses and Tkinter interfaces.",
    "long_description": """
It reads RSS 2.0 and Atom 1.0. All files are downloaded simultaneously to speed up total download.

Except throw CLI, Curses or Tkinter interface, it can also be used in crontab to grab automatically the new media.

Notifications will be displayed if the notify2 package is installed.

It aims to be a single file for basic features, to facilitate the install.

Additional files provide translations (Esperanto, French, German, Russian, Turkish), desktop file, icon, or unit tests.""",
    "author": "Eliovir"
}
if __name__ == "__main__":
    setup(
        name=PARAMS["name"],
    #    packages=["elatom"],
        version=PARAMS["version"],
        description=PARAMS["description"],
        # The long_description field is used by PyPI when you are registering a package, to build its home page.
        long_description=PARAMS["long_description"],
        author=PARAMS["author"],
        author_email=PARAMS["author_email"],
        url=PARAMS["url"],
        download_url=PARAMS["download_url"],
        keywords=["podcast", "rss", "atom"],
        license="GNU GPL v2",
        platforms=["OS Independent"],
        classifiers = [
            "Topic :: Internet",
            "Programming Language :: Python :: 3",
            "Development Status :: 4 - Beta",
            "Environment :: Console :: Curses",
            "Intended Audience :: End Users/Desktop",
            "Environment :: Other Environment",
            "License :: OSI Approved :: GNU General Public License (GPL)",
            "Operating System :: OS Independent",
            "Natural Language :: English",
            "Natural Language :: Esperanto",
            "Natural Language :: French",
            "Natural Language :: German",
            "Natural Language :: Russian",
            "Natural Language :: Turkish"
        ],
        data_files=[
            ('share/applications', ['elatom.desktop']),
            ('share/pixmaps', ['elatom.png']),
            ('share/locale/fr/LC_MESSAGES', glob.glob('locale/*/LC_MESSAGES/elatom.mo')),
        ]
    )
