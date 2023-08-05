'''
Elatom's setup.py
classifiers from http://pypi.python.org/pypi?%3Aaction=list_classifiers
'''
__revision__ = "1.0.6"
from distutils.core import setup

PARAMS = {
    "name": "Elatom",
    "version": __revision__,
    "description": "Podcast downloader in Python 3",
    "author": "Eliovir"
}
if __name__ == "__main__":
    setup(
        name=PARAMS["name"],
    #    packages=["elatom"],
        version=PARAMS["version"],
        description=PARAMS["description"],
        author=PARAMS["author"],
        author_email="eliovir@gmail.com",
        url="https://launchpad.net/elatom",
        #download_url=
        keywords=["podcast", "rss", "atom"],
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
        long_description = """\
    A podcast downloader developed in Python 3 with Curses and Tkinter interfaces.

    It can also be used in crontab to grab automatically the new media.
    It reads RSS 2.0 and Atom 1.0. All files are downloaded simultaneously to speed up total download.
    It aims to be a single file for basic features, to facilitate the install.
    Additional files provide translations (Esperanto, French, German, Russian, Turkish), or unit tests.
    """
    )
