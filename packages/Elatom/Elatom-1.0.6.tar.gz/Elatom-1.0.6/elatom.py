#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# $Id: elatom.py 439 2011-07-13 12:03:05Z maury $
#
# Author : Olivier Maury
# Creation Date : 2009-04-24 12:49:49CEST
# Last Revision : $Date: 2011-07-13 14:03:05 +0200 (mer. 13 juil. 2011) $
# Revision : $Rev: 439 $
#
# tested on WinXP with Python 3.2.1
"""
Main file for Elatom, a podcast downloader for Python 3.
"""
__revision__ = "$Rev: 439 $"
__author__ = "Eliovir"

import codecs
import collections
import gettext
import configparser
import locale
from optparse import OptionGroup, OptionParser
import os
import platform
import re
import string
import sys
import time
import threading
try:
    import tkinter
    from tkinter.scrolledtext import ScrolledText
    import tkinter.filedialog as TkFileDialog
    import tkinter.simpledialog as TkSimpleDialog
    import tkinter.messagebox as TkMessageBox
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
    class TkSimpleDialog:
        """
        Fake class when tkinter is not available.
        """
        class Dialog:
            """
            Fake class when tkinter is not available.
            """
            pass

    class tkinter:
        """
        Fake class when tkinter is not available.
        """
        class Frame:
            """
            Fake class when tkinter is not available.
            """
            pass

import urllib.request
from xml.etree.ElementTree import ElementTree
from xml.parsers.expat import ExpatError

if platform.system() == 'Windows':
    # Curses is not available on Windows
    CURSES_AVAILABLE = False
else:
    import curses
    CURSES_AVAILABLE = True

###########
#         #
# Gettext #
#         #
###########
current_locale, encoding = locale.getdefaultlocale()
# Hack to get the locale directory
basepath = os.path.abspath(os.path.dirname(sys.argv[0]))
localedir = os.path.join(basepath, "locale")
domain = "elatom"             # the translation file is elatom.mo

# Set up Python's gettext
if current_locale != None:
    mytranslation = gettext.translation(domain, localedir, [current_locale],
                                            fallback=True)
    mytranslation.install()
    n_ = mytranslation.ngettext
else:
    def _(text):
        """
        Fake translation function.
        """
        return text
    def n_(singular, plural, number):
        """
        Fake plural translation function.
        """
        if number < 2:
            return singular
        else:
            return plural

########
#      #
# Help #
#      #
########
usage = _("usage: %prog [options]")
parser = OptionParser(usage=usage)
group_ui = OptionGroup(parser, _("Interface"),
                                _("Interface for launching the application."))
group_ui.add_option("-c", "--cli",
        action="store_true", dest="cli", default=False,
        help=_(
"Use the command line interface instead of the graphic interface (TkInter)."))
group_ui.add_option("-q", "--quiet",
        action="store_true", dest="quiet", default=False,
        help=_("Silent download, do not use any UI."))
parser.add_option_group(group_ui)
group_pod = OptionGroup(parser, _("Feeds management"),
                            _("Manage the list of podcasts using the CLI"))
group_pod.add_option("-a", "--add",
        action="store_true", dest="add", default=False,
        help=_("Add a podcast"))
group_pod.add_option("-d", "--delete",
        action="store_true", dest="delete",
        help=_("Delete a podcast"))
group_pod.add_option("-A", "--activate",
        action="store_true", dest="activate",
        help=_("Activate a podcast"))
group_pod.add_option("-i", "--inactivate",
        action="store_true", dest="inactivate",
        help=_("Inactivate a podcast"))
group_pod.add_option("-l", "--list",
        action="store_true", dest="list",
        help=_("List all podcasts"))
group_pod.add_option("-u", "--url",
        type="string", dest="url",
        help=_("Podcast URL to manage"))
group_pod.add_option("-n", "--name",
        type="string", dest="name",
        help=_("Podcast name to manage"))
parser.add_option_group(group_pod)
(args_options, args) = parser.parse_args()


# http://www.voidspace.org.uk/python/articles/urllib2.shtml#error-codes
# Table mapping response codes to messages; entries have the
# form {code: (shortmessage, longmessage)}.
HTTP_RESPONSES = {
    100: ('Continue', 'Request received, please continue'),
    101: ('Switching Protocols',
          'Switching to new protocol; obey Upgrade header'),

    200: ('OK', 'Request fulfilled, document follows'),
    201: ('Created', 'Document created, URL follows'),
    202: ('Accepted',
          'Request accepted, processing continues off-line'),
    203: ('Non-Authoritative Information', 'Request fulfilled from cache'),
    204: ('No Content', 'Request fulfilled, nothing follows'),
    205: ('Reset Content', 'Clear input form for further input.'),
    206: ('Partial Content', 'Partial content follows.'),

    300: ('Multiple Choices',
          'Object has several resources -- see URI list'),
    301: ('Moved Permanently', 'Object moved permanently -- see URI list'),
    302: ('Found', 'Object moved temporarily -- see URI list'),
    303: ('See Other', 'Object moved -- see Method and URL list'),
    304: ('Not Modified',
          'Document has not changed since given time'),
    305: ('Use Proxy',
          'You must use proxy specified in Location to access this '
          'resource.'),
    307: ('Temporary Redirect',
          'Object moved temporarily -- see URI list'),

    400: ('Bad Request',
          'Bad request syntax or unsupported method'),
    401: ('Unauthorized',
          'No permission -- see authorization schemes'),
    402: ('Payment Required',
          'No payment -- see charging schemes'),
    403: ('Forbidden',
          'Request forbidden -- authorization will not help'),
    404: ('Not Found', 'Nothing matches the given URI'),
    405: ('Method Not Allowed',
          'Specified method is invalid for this server.'),
    406: ('Not Acceptable', 'URI not available in preferred format.'),
    407: ('Proxy Authentication Required', 'You must authenticate with '
          'this proxy before proceeding.'),
    408: ('Request Timeout', 'Request timed out; try again later.'),
    409: ('Conflict', 'Request conflict.'),
    410: ('Gone',
          'URI no longer exists and has been permanently removed.'),
    411: ('Length Required', 'Client must specify Content-Length.'),
    412: ('Precondition Failed', 'Precondition in headers is false.'),
    413: ('Request Entity Too Large', 'Entity is too large.'),
    414: ('Request-URI Too Long', 'URI is too long.'),
    415: ('Unsupported Media Type', 'Entity body in unsupported format.'),
    416: ('Requested Range Not Satisfiable',
          'Cannot satisfy request range.'),
    417: ('Expectation Failed',
          'Expect condition could not be satisfied.'),

    500: ('Internal Server Error', 'Server got itself in trouble'),
    501: ('Not Implemented',
          'Server does not support this operation'),
    502: ('Bad Gateway', 'Invalid responses from another server/proxy.'),
    503: ('Service Unavailable',
          'The server cannot process the request due to a high load'),
    504: ('Gateway Timeout',
          'The gateway server did not receive a timely response'),
    505: ('HTTP Version Not Supported', 'Cannot fulfill request.'),
}

##########
#        #
# Config #
#        #
##########

class Config:
    """
    Configuration class.
    """
    _config = None
    _configfilename = None
    _downloaded = None
    _logfilename = None

    def __init__(self, configfile=None, logfile=None):
        """
        Constructor.
        """
        if configfile is None:
            self._configfilename = os.path.join(os.path.expanduser('~'),
                                            '.config', 'elatom', 'elatom.conf')
        else:
            self._configfilename = configfile
        if logfile is None:
            self._logfilename = os.path.join(os.path.expanduser('~'),
                                            '.config', 'elatom', 'podcasts.log')
        else:
            self._logfilename = logfile
        directory = os.path.dirname(self._configfilename)
        if not os.path.exists(directory):
            os.makedirs(directory)
        if not os.path.exists(self._logfilename):
            file_handler = open(self._logfilename, "w")
            file_handler.write("")
            file_handler.close()
        self._config = configparser.ConfigParser()
        if os.path.exists(self._configfilename):
            file_handler = open(self._configfilename, 'r', encoding='utf-8')
            self._config.readfp(file_handler)

    def add_feed(self, name, url):
        """
        Add a feed.

        @type   name:   string
        @param  name:   feed name
        @type   url:    string
        @param  url:    feed URL
        @rtype:         string
        @return:        feed name
        """
        if not self._config.has_section(name):
            self._config.add_section(name)
        self._config.set(name, 'url', url)
        self._config.set(name, 'active', 'True')
        self.save()
        return name

    def _get_name_from_url(self, url):
        """
        Get the feed name, saved in the feed list, from its url.

        @type   url:    string
        @param  url:    feed url
        @rtype:         string
        @return:        feed name
        """
        feeds = self.feeds(False)
        for name in feeds:
            if feeds[name][0] == url:
                return name

    def delete_feed(self, name=None, url=None):
        """
        Remove a feed in the feed list, using its name or url.

        @type   url:    string
        @param  url:    feed url
        @type   name:   string
        @param  name:   feed name
        @rtype:         string
        @return:        feed name
        """
        if url != None:
            name = self._get_name_from_url(url)
        if name != None and self._config.has_section(name):
            self._config.remove_section(name)
            self.save()
            return name

    def activate_feed(self, name=None, url=None, state=True):
        """
        Activate a feed in the feed list, name or url is required.

        @type   url:    string
        @param  url:    feed url
        @type   name:   string
        @param  name:   feed name
        @type   state:  boolean
        @param  state:  state
        @rtype:         string
        @return:        feed name
        """
        if url != None:
            name = self._get_name_from_url(url)
        if name != None and self._config.has_section(name):
            self._config.set(name, "active", state)
            self.save()
            return name

    def inactivate_feed(self, name=None, url=None):
        """
        Inactivate a feed in the feed list, name or url is required.

        @type   url:    string
        @param  url:    feed url
        @type   name:   string
        @param  name:   feed name
        @rtype:         string
        @return:        feed name
        """
        return self.activate_feed(name, url, False)

    def feeds(self, only_active=True):
        """
        Feed dictionary {feed_name: [url, active]).

        @type   only_active:    boolean
        @param  only_active:    get only the active feeds
        @rtype:                 dict
        @return:                feeds
        """
        feeds = collections.OrderedDict()
        sections = self._config.sections()
        sections.sort()
        for section in sections:
            if section == 'elatom.py':
                continue
            try:
                active = self._config.get(section, 'active')
            except TypeError:
                active = 'False'
            if only_active and active == 'False':
                continue
            feeds[section] = [self._config.get(section, 'url'), active]
        return feeds

    def is_downloaded(self, url):
        """
        Check if the URL is already downloaded.

        @type   url:    string
        @param  url:    feed url
        @rtype:         boolean
        @return:        url downloaded
        """
        if self._downloaded == None:
            file_handler = open(self._logfilename)
            self._downloaded = file_handler.read().split('\n')
            file_handler.close()
        if url in self._downloaded:
            return True
        return False

    def memory(self, url):
        """
        Save the URL in the memory, to not download it.

        @type   url:    string
        @param  url:    feed url
        """
        if url in self._downloaded:
            return
        self._downloaded.append(url)
        file_handler = open(self._logfilename, "a+")
        file_handler.write(url + "\n")
        file_handler.close()

    def save(self):
        """
        Save the configuration.
        """
        self._sort()
        with open(self._configfilename, 'w', encoding='utf-8') as configfile:
            self._config.write(configfile)

    def _sort(self):
        """
        Sort the configuration sections.
        """
        old = self._config._sections.copy()
        sections = self._config.sections()
        sections.sort()
        for section in sections:
            self._config.remove_section(section)
            self._config._sections[section] = old[section]

    def download_directory(self, directory=None):
        """
        Save or get the download directory from the config.

        @type   directory:  string
        @param  directory:  directory path to download
        @rtype:     string
        @return:    download directory
        """
        section = 'elatom.py'
        option = 'download_directory'
        if not self._config.has_section(section):
            self._config.add_section(section)
        if not self._config.has_option(section, option) or directory != None:
            if directory == None:
                directory = os.path.join(os.path.expanduser('~'),
                                            _('Downloads'), _('Podcasts'))
            self._config.set(section, option, directory)
            self.save()
            return directory
        return self._config.get(section, option)

class Download(threading.Thread):
    """
    Download thread.
    """
    Start = False

    def __init__(self, id, url, filename, group=None,
                    target=None, name=None, verbose=None):
        """
        Constructor.

        @type   id:     string
        @param  id:     value of <guid>, a permanent link identifying the url
        @type   url:    string
        @param  url:    file url to download
        @type   filename:   string
        @param  filename:   destination
        @type   group:  None
        @param  group:  reserved for future extension when a ThreadGroup class
                        is implemented. Should be None.
        @type   target: object
        @param  target: callable object to be invoked by the run() method
        @type   name:   string
        @param  name:   thread name. By default, a unique name is constructed.
        @type   verbose:
        @param  verbose:
        """
        self._id = id
        self._url = url
        self._filename = filename
        self.is_ended = False
        self.size = None
        self.downloaded = 0
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
            os.makedirs(directory)
        self._stopevent = threading.Event()
        threading.Thread.__init__(self, group=group,
                                    target=target, name=name, verbose=verbose)
    def run(self):
        """
        The activity itself, run by the thread.
        """
        try:
            user_agent = "elatom.py/%s" % __revision__[6:-1]
            headers = {'User-Agent': user_agent}
            req = urllib.request.Request(self._url, None, headers)
            url_handler = urllib.request.urlopen(req)
            self.size = url_handler.info().get('Content-Length')
            if self.size == None:
                self.size = 1
            else:
                self.size = int(self.size)
            local_file = open(self._filename + '.part', 'wb')
            chunk_size = 8192
            while 1:
                chunk = url_handler.read(chunk_size)
                self.downloaded += len(chunk)
                if not chunk:
                    self.is_ended = True
                    break
                local_file.write(chunk)
                # Stop downloading
                if self._stopevent.isSet():
                    self.downloaded = 0
                    os.unlink(self._filename + '.part')
                    return
            #
            local_file.close()
            if os.path.exists(self._filename + '.part'):
                os.rename(self._filename + '.part', self._filename)
                self.is_ended = True
        except urllib.error.HTTPError as error:
            self.size = 1
            self.log('HTTP Error: ' + self._url + " " + \
                        HTTP_RESPONSES[error.code][0])
        except urllib.error.URLError as error:
            self.size = 1
            self.log("URL Error: %s %s" % (self._url, error.reason))
        except IOError as error:
            self.size = 1
            self.log("IOError : %s %s" % (self._url, error.strerror))
        self.is_ended = True

    def stop(self):
        """
        Stop the download.
        """
        self._stopevent.set()

    def log(self, text):
        """
        Log

        @type   text:   string
        @param  text:   string to log
        """
        print("IIII %s" % text)

    def get_id(self):
        """
        Accessor to the ID (<guid>) of the URL.

        @rtype:     string
        @return:    URL/id
        """
        return self._id

    def get_url(self):
        """
        Accessor to the URL to download.

        @rtype:     string
        @return:    URL
        """
        return self._url

class FeedReader(threading.Thread):
    """
    Read from RSS:
    - the title from channel/title
    - the enclosures from item/enclosure

    From Atom (to be done):
    http://www.ibm.com/developerworks/xml/library/x-atom10/index.html
    - the title from title
    - the enclosures from entry/link[rel=enclosure]
    """
    _info = {
        "id": None,
        "url": None,
        "pubDate": None,
        "title": None,
        "type": None,
        "length": None
        }

    def __init__(self, url, group=None, target=None, name=None, verbose=None):
        """
        Constructor.

        @type   url:    string
        @param  url:    feed url
        """
        self.is_ended = False
        self.title = ""
        self._url = url
        self._urls = []
        threading.Thread.__init__(self, group=group,
                                    target=target, name=name, verbose=verbose)
    def get_urls(self):
        return self._urls

    def log(self, text):
        pass

    @staticmethod
    def parse_feed(tree:ElementTree):
        # RSS 2
        results = FeedReader.parse_rss2(tree)
        if results != None:
            return results
        # Atom 10
        results = FeedReader.parse_atom10(tree)
        if results != None:
            return results
        return None

    @staticmethod
    def parse_atom10(tree:ElementTree):
        title = tree.find('{http://www.w3.org/2005/Atom}title')
        if title == None:
            return None
        result = {"title": title.text, "files": []}
        items = tree.findall('{http://www.w3.org/2005/Atom}entry/' + \
                                '{http://www.w3.org/2005/Atom}link')
        for item in items:
            if "rel" in item.attrib and item.attrib["rel"] == "enclosure":
                info = FeedReader._info.copy()
                for (attr, info_attr) in (
                        ("href", "url"),
                        ("title", "title"),
                        ("type", "type"),
                        ("length", "length")
                    ):
                    if attr in item.attrib:
                        info[info_attr] = item.attrib[attr]
                # guid
                info["id"] = info["url"]
                #
                result["files"].append(info)
        return result

    @staticmethod
    def parse_rss2(tree:ElementTree):
        title = tree.find('channel/title')
        if title == None:
            return None
        result = {"title": title.text, "files": []}
        items = tree.findall("channel/item")
        for item in items:
            enclosure = item.find('enclosure')
            if enclosure == None:
                continue
            info = FeedReader._info.copy()
            for attr in ("title", "pubDate"):
                tag = item.find(attr)
                if tag != None:
                    info[attr] = tag.text
            for attr in ("url", "type", "length"):
                if attr in enclosure.attrib:
                    info[attr] = enclosure.attrib[attr]
            # guid
            info["id"] = info["url"]
            guid = item.find("guid")
            if guid != None:
                if ("isPermaLink" in guid.attrib and guid.attrib["isPermaLink"] != "false") or not "isPermaLink" in guid.attrib:
                    info["id"] = guid.text
            #
            result["files"].append(info)
        return result

    def run(self):
        try:
            file_handler = urllib.request.urlopen(self._url)
            tree = ElementTree()
            tree.parse(file_handler)
            results = FeedReader.parse_feed(tree)
            if results == None:
                self.is_ended = True
                return
            self.title = results["title"]
            for info in results["files"]:
                self._urls.append((info["id"], info["url"],
                                info["pubDate"], info["title"]))
        except urllib.error.HTTPError as error:
            self.log("HTTP Error: %s %s" %
                    (self._url, HTTP_RESPONSES[error.code][0]))
        except urllib.error.URLError as error:
            self.log("URL Error: %s %s" % (self._url, error.reason))
        except KeyError as error:
            self.log("KeyError: %s, unknown keys %s" % (self._url, error.args))
        except ExpatError as error:
            self.log("ExpatError: %s (%s)" % (self._url, error.code))
        self.is_ended = True

#####################
#                   #
# Podcast retriever #
#                   #
#####################

class Elatom(threading.Thread):
    """
    Core class for retrieving the podcasts.
    """
    def __init__(self, app):
        self._config = Config()
        self._app = app
        self._stopevent = threading.Event()
        threading.Thread.__init__(self)
        self._app.set_elatom(self)

    def run(self):
        # get feed URLs, and set a progress bar on feed progress
        feed_readers = {}
        feeds = self._config.feeds()
        for name in feeds:
            self._app.add_feed_info(name, 0)
            url = feeds[name][0]
            feed_readers[name] = FeedReader(url)

        # waiting
        while 1:
            time.sleep(1)
            if not Download.Start:
                # Stop ?
                if self._stopevent.isSet():
                    self._app.stop()
                    return
                self._app.waiting_launch()
                continue
            break

        for name in feeds:
            feed_reader = feed_readers[name]
            feed_reader.start()

        # progress
        urls = {}
        i = 0
        total = len(feeds)
        while i < total:
            for name in feeds:
                feed_reader = feed_readers[name]
                if feed_reader.is_ended and not name in urls:
                    urls[name] = []
                    file_nb = 0
                    for (id, url, pubdate, title) in feed_reader.get_urls():
                        # clean the URL
                        url = self._clean_url(url)
                        # if downloaded, ignore
                        if self._config.is_downloaded(id):
                            continue
                        urls[name].append((id, url, pubdate, title))
                        file_nb += 1
                    self._app.update_feed_info(name,
                                    n_("%d file", "%d files", file_nb) % file_nb, 0, file_nb)
                    i += 1
                    continue
                time.sleep(0.2)
            # Stop ?
            if self._stopevent.isSet():
                self._app.stop()
                return

        # nothing to download, exit
        if sum([len(urls[name]) for name in urls]) == 0:
            self._app.status(_("No new files to download.") + " " + \
                                _("Bye"), 0, 0)
            time.sleep(2)
            self._app.stop()
            return

        # set the download threads
        download_threads = {}
        downloaded = {}
        sizes = {}
        total = 0
        for name in urls:
            if len(urls[name]) == 0:
                continue
            download_threads[name] = []
            sizes[name] = {"total": 0, "urls": []}
            downloaded[name] = 0
            feed_title = feed_readers[name].title
            # clean the title
            feed_title = Elatom.format_title(feed_title)
            for (id, url, pubdate, title) in urls[name]:
                # format the date
                pubdate = Elatom.format_date(pubdate)
                # clean the title
                title = title.replace(feed_readers[name].title, '')
                title = Elatom.format_title(title)
                # filename
                ext = os.path.splitext(url)[1]
                filename = os.path.join(self._config.download_directory(),
                                pubdate + '_' + feed_title + "_" + title + ext)
                # download,
                # and set a progress bar on each feed for file progress
                download_thread = Download(id, url, filename)
                download_threads[name].append(download_thread)
                download_thread.start()
                total += 1

        # update the progress bars
        ## with the total size
        i = 0
        while i < total:
            for name in download_threads:
                for download_thread in download_threads[name]:
                    if (download_thread.size != None and
                        not download_thread.get_url() in sizes[name]["urls"]):
                        sizes[name]["urls"].append(download_thread.get_url())
                        sizes[name]["total"] += download_thread.size
                        i += 1
        for name in sizes:
            file_nb = len(sizes[name]["urls"])
            if file_nb > 0:
                self._app.update_feed_info(name,
                        ((n_("%d file", "%d files", file_nb) % file_nb) + \
                            # TRANSLATORS: mega-bytes
                            " (" + _("%.2f Mb") + ")") %
                            (sizes[name]["total"] / 1024 / 1024.),
                        0, sizes[name]["total"])
        ## during download
        downloaded_urls = []
        i = 0
        while i < total:
            for name in download_threads:
                downloaded[name] = 0
                file_nb = len(sizes[name]["urls"])
                for download_thread in download_threads[name]:
                    if download_thread.is_ended:
                        # tell the frontends, one more is downloaded
                        if not download_thread.get_url() in downloaded_urls:
                            downloaded_urls.append(download_thread.get_url())
                            i = len(downloaded_urls)
                        downloaded[name] += download_thread.size
                        # save
                        self._config.memory(download_thread.get_id())
                    elif download_thread.downloaded != None:
                        downloaded[name] += download_thread.downloaded
                if sizes[name]["total"] == downloaded[name]:
                    self._app.update_feed_info(name,
                    (n_("%d downloaded file", "%d downloaded files", file_nb) +
                            " (" + _("%.2f Mb") + ")") %
                                (file_nb, sizes[name]["total"] / 1024 / 1024.),
                            downloaded[name])
                else:
                    self._app.update_feed_info(name,
                  (n_("Downloading %d file", "Downloading %d files", file_nb) +
                            " (" + _("%.2f Mb") + ")") %
                                (file_nb, sizes[name]["total"] / 1024 / 1024.),
                            downloaded[name])
                time.sleep(0.2)
            # Stop ?
            if self._stopevent.isSet():
                for name in download_threads:
                    for download_thread in download_threads[name]:
                        if not download_thread.is_ended:
                            download_thread.stop()
                return

        # stop the frontends
        self._app.status(_("All files are downloaded.") + " " + _("Bye"), 1, 1)
        time.sleep(2)
        self._app.stop()

    def stop(self):
        self._stopevent.set()

    def _clean_url(self, url):
        """
        Transform url to remove redirections.
        """
        # patch pour
        # http://logi3.xiti.com/get/...&url=http://images.telerama.fr/...
        if 'url=' in url and 'telerama.fr' in url:
            url = url.split('url=')[1]
        return url

    @staticmethod
    def format_date(pubdate):
        """
        Convert the date from Atom/RSS to Ymd.

        @type   pubdate:    string
        @param  pubdate:    date string
        @rtype:             string
        @return:            converted date
        """
        try:
            pubdate = time.strftime('%Y%m%d',
                                time.strptime(pubdate, '%Y-%m-%dT%H:%M:%SZ'))
            return pubdate
        except:
            pass
        pubdate = pubdate.split()
        pubdate = pubdate[3] + '-' + pubdate[2] + '-' + pubdate[1]
        try:
            pubdate = time.strftime('%Y%m%d',
                                time.strptime(pubdate, '%Y-%b-%d'))
        except:
            months = {'Jan': '01', 'Feb': '02', 'Fev': '02', 'Mar': '03',
                    'Apr': '04', 'May': '05', 'Jun': '06', 'Jul': '07',
                    'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11',
                    'Dec': '12'}
            for month in months:
                pubdate = pubdate.replace('-' + month + '-', months[month])
                splitted = pubdate.split('_')
                if len(splitted[0]) == 7:
                    splitted[0] = splitted[0][0:6] + '0' + splitted[0][6]
                    pubdate = '_'.join(splitted)
        return pubdate

    @staticmethod
    def format_title(title):
        """
        Clean title.

        @type   title:  string
        @param  title:  title to clean
        @rtype:         string
        @return:        cleaned title
        """
        pattern = re.compile('\W')
        title = re.sub(pattern, '', title)
        title = title.replace('FranceInter', '')\
                    .replace('FranceCulture', '')\
                    .replace('Podcast', '')\
                    .replace('podcast', '').strip()
        return ''.join([x for x in title if x in string.printable])[0:20]


################
#              #
# Progress bar #
#              #
################

class BaseProgressBar:
    """
    Parent class for CLI and TkInter progress bar.
    """

    def __init__(self, min_value=0, max_value=100, width=80):
        """
        Constructor.

        @type   min_value:  float
        @param  min_value:  minimum value for the progress bar
        @type   max_value:  float
        @type   max_value:  maximum value for the progress bar
        @type   width:      integer
        @param  width:      progress bar width
        """
        self._min = min_value
        self._max = max_value
        self._percent_done = 0
        self._span = max_value - min_value
        self._width = width
        self._value = min_value       # When value == max, we are 100% done
        self.set_value(min_value)           # Calculate progress

    def set_max(self, max_value=100):
        """
        Set the maximum value and calculate.

        @type   max_value:  float
        @type   max_value:  maximum value for the progress bar
        """
        self._max = float(max_value)
        self._span = max_value - self._min

    def set_value(self, value):
        """ Update the progress with the new value (with min and max
            values set at initialization; if it is over or under, it takes the
            min or max value as a default. """
        if value < self._min:
            value = self._min
        if value > self._max:
            value = self._max
        self._value = value

        # Figure out the new percent done, round to an integer
        diff_from_min = float(self._value - self._min)
        if self._max == self._min:
            self._percent_done = 100.0
        else:
            self._percent_done = (diff_from_min / float(self._span)) * 100.0
            self._percent_done = int(round(self._percent_done))

class ProgressBar(BaseProgressBar):
    """ Creates a text-based progress bar. Call the object with the `print'
    command to see the progress bar, which looks something like this:

    [=======>        22%                  ]

    You may specify the progress bar's width, min and max values on init.

        limit = 100
        width = 30
        prog = ProgressBar(0, limit, width)
        for i in range(limit+1):
            prog.set_value(i)
            print(prog, "\r", end="")
            time.sleep(0.20)

        http://code.activestate.com/recipes/168639-progress-bar-class/
    """

    def __init__(self, min_value=0, max_value=100, width=80):
        """
        Constructor.

        @type   min_value:  float
        @param  min_value:  minimum value for the progress bar
        @type   max_value:  float
        @type   max_value:  maximum value for the progress bar
        @type   width:      integer
        @param  width:      progress bar width
        """
        BaseProgressBar.__init__(self, min_value=min_value, max_value=max_value,
                                    width=width)
        self._prog_bar = "[]"   # This holds the progress bar string

    def set_value(self, value=0):
        """
        Update the progress bar with the new value (with min and max values set
        at initialization; if it is over or under, it takes the min or max
        value as a default.
        
        @type   value:  float
        @param  value:  new value for the current position
        """
        BaseProgressBar.set_value(self, value)

        # Figure out how many hash bars the percentage should be
        all_full = self._width - 2
        num_hashes = (self._percent_done / 100.0) * all_full
        num_hashes = int(round(num_hashes))

        # Build a progress bar with an arrow of equal signs; special cases for
        # empty and full
        if num_hashes == 0:
            self._prog_bar = "[>%s]" % (' ' * (all_full - 1))
        elif num_hashes == all_full:
            self._prog_bar = "[%s]" % ('=' * all_full)
        else:
            self._prog_bar = "[%s>%s]" % ('=' * (num_hashes - 1),
                                        ' ' * (all_full - num_hashes))
        # figure out where to put the percentage, roughly centered
        percent_place = (int(len(self._prog_bar) / 2) -
                        len(str(self._percent_done)))
        percent_string = str(self._percent_done) + "%"

        # slice the percentage into the bar
        self._prog_bar = ''.join([self._prog_bar[0:percent_place],
                            percent_string,
                            self._prog_bar[percent_place + len(percent_string):]
                                ])

    def __str__(self):
        """
        String representation.

        @rtype:     string
        @return:    string representation
        """
        return str(self._prog_bar)

class TkProgressBar(BaseProgressBar, tkinter.Frame):
    '''
    A simple progress bar widget.
    Inspired from klappnase
    http://www.velocityreviews.com/forums/t329218-need-a-progress-bar-meter-for-tkinter.html#1753710
    '''
    def __init__(self, master, fillcolor='orchid1', min_value=0, max_value=100,
                    width=150, text='', **kw):
        """
        Constructor.

        @type   fillcolor:  string
        @param  fillcolor:  fill color for the progress bar
        @type   min_value:  float
        @param  min_value:  minimum value for the progress bar
        @type   max_value:  float
        @type   max_value:  maximum value for the progress bar
        @type   width:      integer
        @param  width:      progress bar width
        @type   text:       string
        @param  text:       information text shown near the progress bar
        """
        tkinter.Frame.__init__(self, master, bg='white', width=width, height=20)
        self.configure(width=width, **kw)

        self._canvas = tkinter.Canvas(self, bg=self['bg'],
                                width=self['width'], height=self['height'],
                                highlightthickness=0, relief='flat', bd=0)
        self._canvas.pack(fill='x', expand=1)
        self._r = self._canvas.create_rectangle(0, 0, 0, int(self['height']),
                                                    fill=fillcolor, width=0)
        self._t = self._canvas.create_text(int(self['width']) / 2,
                                            int(self['height']) / 2, text='')

        BaseProgressBar.__init__(self, min_value=min_value, max_value=max_value,
                                    width=width)
        self.set_value(min_value, text)

    def set_value(self, value=0.0, text=None):
        """
        Update the progress bar with the new value (with min and max values set
        at initialization; if it is over or under, it takes the min or max
        value as a default.
        
        @type   value:  float
        @param  value:  new value for the current position
        @type   text:   string
        @param  text:   information text shown near the progress bar
        """
        BaseProgressBar.set_value(self, value)
        #make the value failsafe:
        if text == None:
            #if no text is specified get the default percentage string:
            text = str(int(self._percent_done)) + ' %'
        self._canvas.coords(self._r, 0, 0,
                int(self['width']) * (value / self._max), int(self['height']))
        self._canvas.itemconfigure(self._t, text=text)

##############
#            #
# Interfaces #
#            #
##############

class BaseApp:
    """
    Abstract class for the interfaces.
    """
    _elatom = None
    def add_feed_info(self, name, total):
        raise NotImplementedError()
    def set_elatom(self, elatom):
        self._elatom = elatom
    def start(self):
        raise NotImplementedError()
    def status(self, text, progress, total):
        """
        Display a message, the progress in the interface.

        @type   text:   string
        @param  text:   message
        @type   progress:   float
        @param  progress:   current progress
        @type   total:      float
        @param  total:      maximum progress
        """
        raise NotImplementedError()
    def stop(self):
        raise NotImplementedError()
    def update_feed_info(self, name, status, progress, total=False):
        raise NotImplementedError()
    def waiting_launch(self):
        raise NotImplementedError()

class CursesApp(BaseApp):
    """
    Curses application.
    """
    _screen = None
    _feeds = {}
    _code = None
    _prog_width = 18

    def __init__(self):
        # initialize library, and make a window:
        self._stdscr = curses.initscr()
        (self._scr_height, self._scr_width) = (self._stdscr.getmaxyx())
        self._stdscr.keypad(1)
        # Allow color and echo text.
        curses.echo()
        curses.start_color()
        # Set 'curses.color_pair(1)' to green text on black.
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        #
        self._screen = self._stdscr.subwin(self._scr_height,
                                                self._scr_width - 1, 0, 0)
        self._screen.box()
        self._screen.hline(2, 1, curses.COLOR_BLACK, self._scr_width - 3)
        self._prog = ProgressBar(0, 10, 18)
        self.status("", 0, 0)

    def add_feed_info(self, name, total):
        self._feeds[name] = {
                "name": name[0:50],
                "number": len(self._feeds),
                "total": total,
                "progress bar": ProgressBar(0, total, self._prog_width)
                }
        prog = self._feeds[name]["progress bar"]
        prog.set_value(0)

        self._screen.addstr(3 + self._feeds[name]["number"],
                    1, name, curses.color_pair(0))
        self._screen.addstr(3 + self._feeds[name]["number"],
                    self._scr_width - self._prog_width - 2, str(prog),
                    curses.color_pair(0))

    def status(self, text, progress, total):
        self._screen.addstr(1, 1, "elatom.py", curses.color_pair(1))
        self._screen.addstr(1, 8, text)
        self._screen.addstr(1, self._scr_width - 2 - 8,
                                time.strftime("%H:%M:%S"))
        if total > 0:
            self._prog.set_max(total)
            self._prog.set_value(progress)
            self._screen.addstr(1,
                                self._scr_width - 2 - 8 - self._prog_width - 2,
                                str(self._prog))
        else:
            self._screen.addstr(1,
                                self._scr_width - 2 - 8 - self._prog_width - 2,
                                " " * 18)
        self._screen.refresh()

    def start(self):
        pass

    def stop(self):
        """ Set everything back to normal. """
        curses.nocbreak()
        self._stdscr.keypad(0)
        self._screen.keypad(False)
        curses.echo()
        curses.endwin()

    def update_feed_info(self, name, status, progress, total=False):
        prog = self._feeds[name]["progress bar"]
        if total != False:
            prog.set_max(total)
        prog.set_value(progress)
        self._screen.addstr(3 + self._feeds[name]["number"],
                            self._scr_width - self._prog_width - 2, str(prog),
                            curses.color_pair(1))
        self._screen.refresh()

    def waiting_launch(self):
        """ Nothing, downloading begins at start. """
        Download.Start = True
        return

class QuietApp(BaseApp):
    """
    Application without any interface.
    """
    def __init__(self):
        pass
    def add_feed_info(self, name, total):
        pass
    def status(self, text, progress, total):
        pass
    def start(self):
        pass
    def stop(self):
        pass
    def update_feed_info(self, name, status, progress, total=False):
        pass
    def waiting_launch(self):
        pass

# keep in global space the PhotoImage objects
GIFDICT = {}

class TkApp(BaseApp):
    """
    TkInter application.
    """
    def __init__(self):
        self.feed_infos = {}
        self.root = tkinter.Tk()
        # window title text
        self.root.title("ElAtom")
        self.root.wm_title("Elatom")
        # application icon
        iconpath = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])),
                                "elatom.xbm")
        if os.path.exists(iconpath):
            iconpath = "@" + iconpath
            self.root.iconbitmap(iconpath)
            self.root.wm_iconbitmap(iconpath)
        # frames
        buttonframe = tkinter.Frame(self.root)
        buttonframe.pack()
        self.feedframe = tkinter.Frame(self.root)
        self.feedframe.pack()
        # buttons
        tkinter.Button(buttonframe, text=_("Settings"),
                        command=self.on_show_config).pack(side=tkinter.LEFT)
        tkinter.Button(buttonframe, text=_("About"),
                        command=self.on_show_about).pack(side=tkinter.LEFT)
        # TRANSLATORS: Used in a button: a verb.
        tkinter.Button(buttonframe, text=_("Start"),
                        command=self._start).pack(side=tkinter.LEFT)
        tkinter.Button(buttonframe, text=_("Quit"),
                        command=self.stop).pack(side=tkinter.LEFT)
        self._prog = TkProgressBar(buttonframe, min_value=11, max_value=99,
                                    width=150)
        self._prog.pack(side=tkinter.LEFT)
        self._prog.set_value(0)
        # variable
        self.vtext = tkinter.StringVar()
        self.vtext.set("ok")
        self.text = tkinter.Label(self.root, width=(40 + 35 + 10),
                                    textvariable=self.vtext, bd=1,
                                    relief=tkinter.SUNKEN, anchor='w')
        self.text.pack(side=tkinter.BOTTOM)
    def waiting_launch(self):
        self.vtext.set(_("Waiting.") + time.strftime("%H:%M:%S"))
    def add_feed_info(self, name, total):
        # variables
        ## To correct this exception on another Python 3.1.2 with Tk 8.5.8,
        ##  value must be set at instanciation
        ## Exception _tkinter.TclError:
        ##  'can\'t unset "PY_VAR1": no such variable'
        ## In case of error
        ## _tkinter.TclError: out of stack space (infinite loop?)
        ## dev-lang/tk must be recompiled with threads enabled
        self.feed_infos[name] = [
                # status
                tkinter.StringVar(master=self.root, value=_("Beginning")),
                # progress
                tkinter.DoubleVar(master=self.root, value=0.0),
                # progress text
                tkinter.StringVar(master=self.root, value="0.0%"),
                # total
                tkinter.DoubleVar(master=self.root, value=total),
                0, 0
        ]
        # widgets
        frame = tkinter.Frame(master=self.feedframe)
        frame.pack(side=tkinter.TOP)
        ## label
        label = tkinter.Label(frame, width=40, height=1, text=name)
        label.pack(side=tkinter.LEFT)
        ## status
        self.feed_infos[name][4] = tkinter.Label(frame, width=35,
                                        textvariable=self.feed_infos[name][0],
                                        bd=1, relief=tkinter.SUNKEN,
                                        anchor='w')
        self.feed_infos[name][4].pack(side=tkinter.LEFT)
        ## progress text
        self.feed_infos[name][5] = tkinter.Label(frame, width=10,
                                        textvariable=self.feed_infos[name][2],
                                        bd=1, relief=tkinter.SUNKEN, anchor='w')
        self.feed_infos[name][5].pack(side=tkinter.LEFT)
    
    def on_show_about(self):
        """
        Display the about dialog.
        """
        TkAbout(self.root)

    def on_show_config(self):
        """
        Display the config dialog.
        """
        TkConfig(self.root)

    def update_feed_info(self, name, status, progress, total=False):
        if total != False:
            self.feed_infos[name][3].set(total)
        else:
            total = self.feed_infos[name][3].get()
        if total == 0:
            progresstext = "-"
        else:
            progresstext = "%.2f%%" % (progress / total * 100.)
        self.feed_infos[name][0].set(status)
        self.feed_infos[name][1].set(progress)
        self.feed_infos[name][2].set(progresstext)
        # status
        total = 0
        progress = 0
        for feed in self.feed_infos:
            progress += self.feed_infos[feed][1].get()
            total += self.feed_infos[feed][3].get()
        if progress >= total:
            self.vtext.set(_("All feeds are downloaded."))
        else:
            text = _("Downloading:") + " %.2f%%" % (progress / total * 100.)
            self.status(text, progress, total)

    def status(self, text, progress, total):
        self.vtext.set(text)
        if total > 0:
            self._prog.set_max(total)
            self._prog.set_value(progress)

    def start(self):
        self.root.mainloop()

    def stop(self):
        """
        Stop the backend application and close the TkInter interface.
        """
        self._elatom.stop()
        time.sleep(0.2)
        self.root.quit()
        sys.exit(0)

    def _start(self):
        Download.Start = True
        self.vtext.set(_("Downloading the files.") + time.strftime("%H:%M:%S"))

class TkAbout(TkSimpleDialog.Dialog):
    """ Display the About dialog : it reads the README.txt file. """

    def __init__(self, parent):
        """ Create and display window. """
        TkSimpleDialog.Dialog.__init__(self, parent, _('Podcasts'))
    
    def body(self, master):
        """ Create dialog body """
        readme_path = os.path.join(
                os.path.abspath(os.path.dirname(sys.argv[0])),
                "README.txt")
        if os.path.exists(readme_path):
            file_handler = codecs.open(readme_path, 'r', 'utf8')
            readme_text = file_handler.read()
            file_handler.close()
        else:
            readme_text = _("""This file "%s" does not exist.""" %
                            "README.txt")
        translations = _("Translations")
        readme_text += "\n\n%s\n%s\n\n%s" % (
                translations,
                "=" * len(translations),
                _("translator-credits")
            )
        text = ScrolledText(master)
        text.insert(tkinter.END, readme_text)
        text.configure(state=tkinter.DISABLED)
        text.pack()

    def buttonbox(self):
        """ Create custom buttons """
        tkinter.Button(self, text=_('Close'), width=10, command=self.ok,
                        default=tkinter.ACTIVE).pack(side=tkinter.RIGHT)
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.ok)

class TkFeedWidget(tkinter.Frame):
    """ A widget to display the name, the url and the active box. """
    def __init__(self, master, name, url, active, width=150, text='', **kw):
        tkinter.Frame.__init__(self, master, width=width, height=20)
        self.configure(width=width, **kw)
        self.name = name
        self.url = url
        self.ckb_active = tkinter.IntVar()
        self.e_active = tkinter.Checkbutton(self, text="",
                            variable=self.ckb_active).pack(side=tkinter.LEFT)
        if active == 'True':
            self.ckb_active.set(1)
        else:
            self.ckb_active.set(0)
        self.e_name = tkinter.Entry(self, width=40)
        self.e_name.insert(tkinter.END, name)
        self.e_name.pack(side=tkinter.LEFT)
        self.e_url = tkinter.Entry(self, width=40)
        self.e_url.insert(tkinter.END, url)
        self.e_url.pack(side=tkinter.LEFT)
        self.btn_delete = tkinter.Button(self, text="X", padx=0, pady=0,
                    command=self.on_delete, borderwidth=0, relief=tkinter.FLAT)
        self.btn_delete.pack(side=tkinter.RIGHT)

    def on_delete(self):
        """
        Event function triggered by the delete button.
        It deletes the feed attached to the widget.
        """
        Config().delete_feed(name=self.name)
        self.destroy()

class TkConfig(TkSimpleDialog.Dialog):
    """ Display the configuration dialog : feeds and download directory. """

    def __init__(self, parent):
        """ Create and display window. """
        self.canvas = None
        self._config = Config()
        self.download_directory = None
        self.frame_dd = None
        self.vscroll = None
        self.widgets = {}
        TkSimpleDialog.Dialog.__init__(self, parent, _('Podcasts'))

    def add_feed(self):
        url = TkSimpleDialog.askstring(_("Add a podcast"), _("Podcast address"))
        if url:
            try:
                file_handler = urllib.request.urlopen(url)
                tree = ElementTree()
                tree.parse(file_handler)
                file_handler.close()
                results = FeedReader.parse_feed(tree)
                title = results['title']
                name = self._config.add_feed(name=title, url=url)
                if name != None:
                    self.widgets[name] = TkFeedWidget(self.frame, name, url,
                                                        'True')
                    self.widgets[name].pack()
                    self.update()
            except urllib.error.HTTPError as error:
                TkMessageBox.showwarning("Yes", 'HTTP Error: %s %s ' %
                                          (url, HTTP_RESPONSES[error.code][0]))
            except urllib.error.URLError as error:
                TkConfig.log("URL Error: %s %s" % (url, error.reason))
            except IOError as error:
                TkConfig.log("Error: %s %s" % (url, error))

    def ask_download_directory(self):
        """
        Event function to ask the download directory.
        """
        directory = TkFileDialog.askdirectory()
        if directory != "":
            self.download_directory.set(directory)

    def body(self, master):
        """ Create dialog body """
        self.master = master
        # podcasts
        tkinter.Label(master, text=_("Podcasts")).grid(row=0, column=0)
        # canvas + vscroll : container for the feeds
        self.canvas = tkinter.Canvas(master, width=650, height=500)
        self.canvas.grid(row=1, column=0, sticky='nswe')
        self.vscroll = tkinter.Scrollbar(master, orient=tkinter.VERTICAL,
                                            command=self.canvas.yview)
        self.vscroll.grid(row=1, column=1, sticky='ns')
        self.canvas.configure(yscrollcommand=self.vscroll.set)
        self.frame = tkinter.Frame(self.canvas)
        self.frame.pack()
        feeds = self._config.feeds(False)
        for name in feeds:
            self.widgets[name] = TkFeedWidget(self.frame, name,
                                                feeds[name][0], feeds[name][1])
            self.widgets[name].pack()
        # download directory
        self.frame_dd = tkinter.Frame(master)
        tkinter.Label(self.frame_dd, text=_("Download directory"), width=30)\
                .pack(side=tkinter.LEFT)
        self.download_directory = tkinter.StringVar()
        self.download_directory.set(self._config.download_directory())
        tkinter.Entry(self.frame_dd, textvariable=self.download_directory,
                width=40).pack(side=tkinter.LEFT)
        open_image = tkinter.PhotoImage(format='gif',
            data="R0lGODlhEAAQAIcAADFKY0L/QplnAZpoApxqBJ5sBqBuCKJwCqNxC6RyDKVzD\
ad1D6x6FLB+GLOBG7WCHbeEH7qHIr2KJcaaGcaaGsKPKsiVMMmWMcuYM8yZNMmgIc+iJte4QNq/bOKz\
Q+LBUP3VcP/bdfDkev/kf5SlvZylvbe3t5ytxqW11qm92r3GxrnK5P/XhP/rhP/viffwif/4k///mf/\
/nP//pcTExMXFxc3NzdHR0cbW69jh8efv9+vz//r7/P///wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAMAAAEALAAAAAAQABAAAAiZAAMIHEiwoMGDBzNkwHDB\
AkKBGXpI5MGjAsKIMjJm7CEhAoQHDhoIxNBDo0mJEhncCHChB4yXMGPKWFBjgs2bOG1+aIGAxoQYJk3\
G6DCBhQGfQGPClPFiAogCNAL8dEG1KtUZGjwQiPpTxoivYEfM4LBhQFSpMUKoXatWBAUBNQROUECXbo\
IDBgoQGGDCxkAbNAILHuz34cGAADs=")
        GIFDICT['open_image'] = open_image
        tkinter.Button(self.frame_dd, image=open_image,
                        command=self.ask_download_directory)\
                .pack(side=tkinter.LEFT)
        self.frame_dd.grid(row=2, column=0)

        self.update()

    def buttonbox(self):
        """ Create custom buttons """
        add_text = _('Add a podcast')
        add_width = len(add_text)
        if add_width < 20:
            add_width = 20
        tkinter.Button(self, text=add_text, width=add_width,
                command=self.add_feed, default=tkinter.ACTIVE)\
                .pack(side=tkinter.LEFT)
        tkinter.Button(self, text=_('Save'), width=10, command=self.save,
                default=tkinter.ACTIVE).pack(side=tkinter.RIGHT)
        tkinter.Button(self, text=_('Cancel'), width=10, command=self.close,
                default=tkinter.ACTIVE).pack(side=tkinter.RIGHT)
        self.bind("<Return>", self.save)
        #self.bind("<Escape>", self.close) # bug

    def close(self):
        """ Close the windows. """
        self.frame.destroy()
        TkSimpleDialog.Dialog.ok(self)

    @staticmethod
    def log(text):
        """ Logging the text. """
        print(text)

    def save(self):
        """ Save the changes on name, url or activation. """
        for name in self.widgets:
            if (self.widgets[name].e_name.get() != name or
                    self.widgets[name].e_url.get() != self.widgets[name].url):
                self._config.add_feed(name=self.widgets[name].e_name.get(),
                                        url=self.widgets[name].e_url.get())
                self._config.delete_feed(name)
            if self.widgets[name].ckb_active.get() == 1:
                self._config.activate_feed(self.widgets[name].e_name.get())
            else:
                self._config.inactivate_feed(self.widgets[name].e_name.get())
        if self.download_directory.get() != self._config.download_directory():
            self._config.download_directory(self.download_directory.get())
        self.close()

    def update(self):
        self.frame.update()
        self.canvas.create_window(0, 0, window=self.frame, anchor=tkinter.NW)
        self.canvas.configure(scrollregion=self.canvas.bbox(tkinter.ALL))

##########################

def main(options):
    """
    Command line interaction and application launch.
    """

    if options.add:
        config = Config()
        name = config.add_feed(name=options.name, url=options.url)
        if name != None:
            print(_("""The feed "%s" is added.""") % name)
        sys.exit(0)
    if options.delete:
        config = Config()
        name = config.delete_feed(name=options.name, url=options.url)
        if name != None:
            print(_("""The feed "%s" is deleted.""") % name)
        sys.exit(0)
    if options.activate:
        config = Config()
        name = config.activate_feed(name=options.name, url=options.url)
        if name != None:
            print(_("""The feed "%s" is activated.""") % name)
        sys.exit(0)
    if options.inactivate:
        config = Config()
        name = config.inactivate_feed(name=options.name, url=options.url)
        if name != None:
            print(_("""The feed "%s" is inactivated.""") % name)
        sys.exit(0)
    if options.list:
        config = Config()
        feeds = config.feeds(False)
        line = "%s :\n   %s"
        head = _("Active feeds")
        print(head)
        print("=" * len(head))
        print()
        for name in feeds:
            if feeds[name][1] == 'True':
                print(line % (name, feeds[name][0]))
        print()
        head = _("Inactive feeds")
        print(head)
        print("=" * len(head))
        print()
        for name in feeds:
            if feeds[name][1] == 'False':
                print(line % (name, feeds[name][0]))

        sys.exit(0)
    if options.quiet:
        Download.Start = True
        app = QuietApp()
    elif CURSES_AVAILABLE and options.cli:
        app = CursesApp()
    elif TKINTER_AVAILABLE:
        app = TkApp()
    else:
        Download.Start = True
        app = QuietApp()
    elatom = Elatom(app)
    elatom.start()
    app.start()

if __name__ == "__main__":
    main(args_options)
