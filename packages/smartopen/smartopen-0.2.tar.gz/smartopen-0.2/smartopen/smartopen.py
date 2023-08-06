#!/usr/bin/env python

"""
open what you give in your browser
"""

import os
import subprocess
import sys

from optparse import OptionParser
from pkg_resources import iter_entry_points
from ConfigParser import ConfigParser


### method to open a browser

### It turns out finding the default browser is very hard :(
# webbrowser is standard...just...what does that mean?  for gnome-terminal,
# I get firefox;  however, despite what
# http://stackoverflow.com/questions/4216985/python-call-to-operating-system-to-open-url
# says (and also because of it), I actually get `links` from xdg-open(!)
# (which of course it doesn't even tell me)

# xdg-settings --list
# Known properties:
#   default-web-browser           Default web browser
# xdg-settings get default-web-browser
# xdg-settings: unknown desktop environment

# The solution....is here:
# http://askubuntu.com/questions/96080/how-to-set-google-chrome-as-the-default-browser/96081#96081
# and indeed in ~/.local/share/applications/mimeapps.list
# I do have::

#  text/html=firefox.desktop;thunderbird.desktop;

# in `[Added Associations]`
# (fwiw, ``pprint(mailcap.getcaps())`` was interesting but not very useful, 
# referencing /usr/bin/sensible-browser which is in fact links (!)

# TODO:

# probably some fancy module should be written that *actually* does what
# its supposed to here; maybe https://pypi.python.org/pypi/desktop is that
# fancy pants module; I don't know! pypi doesn't let me browse tarballs!
# in any case, this is mostly for me and it must be portable;

# So what we'll actually do:
# (Not surprisingly, explicit wins)
# - if specified on the command line (which it can't be yet) that wins
# - use browser/BROWSER if set in config
# - if not...you're back to guessing
# - if `which` was stdlib I'd probably guess on that since I know I can't rely
#   on `xdg-open`...
# - ...and there are other platforms; again, I don't care....
# - so we're back to Firefox being #1

# Which despite my love for Firefox, I'd love to help with autoselection if
# anyone would throw their hat in

# * let's not forget http://freedesktop.org/wiki/Software/pyxdg if we're
# talking about non-stdlib solutions for linux only

def open_in_browser(url, browser=None):
    """yeah, that's right..."""

    if browser is None:
        browser = 'firefox' # we'll cheat because of course its easy

    # control via env variable; might as well keep it set o_O
    os.environ.setdefault('BROWSER', browser)
    # see e.g. http://hg.python.org/cpython/file/2.7/Lib/webbrowser.py
    # sadly these are different::
    # xdg-open http://k0s.org/
    # BROWSER=firefox xdg-open http://k0s.org/

    # now invoke the damn thing
    import webbrowser
    return webbrowser.open(url) # XXX lord almighty
    # why bother returning it even?


### methods for inspecting the locations

def locations(names=None, config=None, verbose=False):
    """
    list of 2-tuples of location handlers;
    * names: order names of handlers
    * config: nested dictionary of configuration from names
    """

    # setup
    _handlers = {}
    _names = []
    if config is None:
        config = {}

    # load the handlers
    # (really, these should come of a dict that is shared with an entry point)
    for i in iter_entry_points('smartopen.locations'):
        try:
            handler = i.load()
        except Exception, e:
            if verbose:
                print >> sys.stderr,  "Error loading handler:\n%s" % e
            continue
        _handlers[i.name] = handler
        if not names:
            _names.append(i.name)

    if not names:
        names = _names
    handlers = []
    for name in names:
        if ':' in name:
            _name, section = name.split(':', 1)
        else:
            _name = name
        if _name in _handlers:
            try:
                handler = _handlers[_name](**config.get(name, {}))
            except Exception, e:
                if verbose:
                    print >> sys.stderr, "blah  blah blah"
                continue
            handlers.append((name, handler))
    return handlers


def urls(query, handlers=None):
    """returns available urls in order of preference for a query"""

    if handlers is None:
        handlers = locations()
    urls = []
    for name, handler in handlers:
        if handler.test(query):
            urls.append((name, handler.url(query)))
    return urls


def url(query, handlers=None):
    """return the top url for a query"""

    if handlers is None:
        handlers = locations()
    for name, handler in handlers:
        if handler.test(query):
            return handler.url(query)

### command line entry point

def main(args=sys.argv[1:]):

    # parse command line optioins
    default_browser = os.environ.get('BROWSER', 'firefox') # ^ see LONG note above
    usage = '%prog [options] query'
    parser = OptionParser(usage=usage)
    parser.add_option('-b', '--browser', dest='browser',
                      default=None,
                      help="browser to use; can also be set in config and BROWSER [default: %default]")
    parser.add_option('-c', '--config', dest="config",
                      help="config file to read")
    parser.add_option('-u', '--url', dest="url",
                      action='store_true', default=False,
                      help="print the first url handled")
    parser.add_option('-a', '--all', dest="all",
                      action='store_true', default=False,
                      help="print all handlers that match the query")
    parser.add_option('-H', '--handler', dest="handlers",
                      action='append',
                      help="name of the handler to use, in order")
    parser.add_option('-v', '--verbose', dest='verbose',
                      action='store_true', default=True,
                      help="be verbose with output")
    parser.add_option('--print-handlers', dest="print_handlers",
                      action='store_true',
                      help="print all handlers in order they would be tried")
    options, args = parser.parse_args(args)

    # sanity check
    assert not (options.url and options.all)
    if not options.handlers:
        options.handlers = None

    # read config, if available
    config = ConfigParser()
    if not options.config:
        options.config = os.path.join(os.environ.get('HOME', ''), '.smartopen.ini')
    if os.path.exists(options.config):
        config.read(options.config)

        # select handlers
        if not options.handlers and config.has_option('DEFAULTS', 'handlers'):
            options.handlers = [i.strip() for i in config.get('DEFAULTS', 'handlers').split(',')]

        # select browser
        if not options.browser:
            for key in 'BROWSER', 'browser':
                if config.has_option('DEFAULTS', key):
                    options.browser = config.get('DEFAULTS', key)
                    break

    # the remaining config is arguments to the handlers
    _config = {}
    for section in config.sections():
        _config[section] = dict(config.items(section))

    # get the handlers
    _locations = locations(options.handlers, _config, verbose=options.verbose)

    if options.print_handlers:
        # print the handlers
        for name, loc in _locations:
            print name
        sys.exit(0)

    # get data to be operated on
    if args:
        data = ' '.join(args)
    else:
        # read from stdin
        data = sys.stdin.read()

    if options.all:
        # print the URLs
        _urls = urls(data, _locations)
        for name, _url in _urls:
            print '%s: %s' % (name, _url)
        sys.exit(0)

    # select the url
    _url = url(data, _locations)

    if options.url:
        # print a URL
        print _url or 'No handler found for your query'
        sys.exit(0)

    # open the URL in a browser
    if _url:
        open_in_browser(_url)
    else:
        parser.error("No handler found")

if __name__ == '__main__':
    main()
