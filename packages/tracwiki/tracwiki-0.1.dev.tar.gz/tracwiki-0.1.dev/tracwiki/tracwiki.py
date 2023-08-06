#!/usr/bin/env python

"""
Checkout and commit wiki pages stored on a trac server.


First use the config option to configure the server, after this, the checkout
and commit commands are available.
"""

import os
import sys
import json
import keyring
import getpass
import hashlib
import argparse
import xmlrpclib

def docSplit(func):
    """
    Return the header of the docstring of a function.

    @arg func: A function.
    @type func: function
    """
    return func.__doc__.split("\n\n")[0]
#docSplit

class TracWiki(object):
    """
    Checkout and commit wiki pages stored on a trac server.
    """
    config_file = ".trac_config"

    def __init__(self, handle, url="", username="", password=""):
        """
        Class constructor. Make the config file if it doesn't exist, read the
        config file.

        @arg handle: Open writeable handle to the output file.
        @type handle: stream
        @arg url: URL of the trac server.
        @type url: str
        @arg username: User name.
        @type username: str
        @arg password: Password.
        @type password: str
        """
        delimiter = "://"
        self.conf = {}
        self.handle = handle
        self.password = None

        if os.path.isfile(self.config_file):
            self.conf = json.loads(open(self.config_file).read())

        if url:
            if delimiter in url:
                protocol, location = url.split(delimiter)

                self.conf["protocol"] = protocol
                self.conf["location"] = location
                self.conf["username"] = username
                if not username:
                    self.conf["username"] = raw_input("User name: ")
                if not password:
                    self.password = getpass.getpass("Password: ")
                    keyring.set_password(location, self.conf["username"],
                        self.password)
                #if
                if "info" not in self.conf:
                    self.conf["info"] = {}
            #if
            else:
                raise ValueError("Invalid URL.")
        #if

        if not self.conf:
            raise ValueError("No configuration found, use \"config\".")

        if self.password == None:
            self.password = keyring.get_password(self.conf["location"],
                self.conf["username"])

        self.server = xmlrpclib.ServerProxy("%s://%s:%s@%s/login/xmlrpc" % (
            self.conf["protocol"], self.conf["username"],
            self.password, self.conf["location"]))
    #__init__

    def __del__(self):
        """
        Class destructor. Save the config file.
        """
        open(self.config_file, "w").write(json.dumps(self.conf))
    #__del__

    def __getFile(self, fileName):
        """
        Retrieve a page from the server.

        @arg fileName: Name of the page.
        @type fileName: str
        """
        if fileName in self.conf["info"]:
            localContent = open(fileName).read()
            localMd5sum = hashlib.md5(localContent).hexdigest()

            if self.conf["info"][fileName][1] != localMd5sum:
                self.handle.write("\n\"%s\" has local modifications." %
                    fileName)
                return
            #if
        #if

        pageInfo = self.server.wiki.getPageInfo(fileName)

        if pageInfo:
            version = pageInfo["version"]
            content = self.server.wiki.getPage(fileName).encode("utf-8")
            md5sum = hashlib.md5(content).hexdigest()

            if (fileName not in self.conf["info"] or
                self.conf["info"][fileName][1] != md5sum):
                open(fileName, "w").write(content)
                self.conf["info"][fileName] = [version, md5sum]
                self.handle.write("\nUpdated \"%s\"." % fileName)
            #if
            else:
                self.handle.write(".")
                self.handle.flush()
            #else
        #if
        else:
            self.handle.write("\nNo such page \"%s\"." % fileName)
    #__getFile

    def __putFile(self, fileName):
        """
        Save a file to the server.

        @arg fileName: Name of the page.
        @type fileName: str
        """
        if not os.path.isfile(fileName):
            raise ValueError("No such file \"%s\"" % fileName)

        pageInfo = self.server.wiki.getPageInfo(fileName)
        if not pageInfo:
            version = 0
            self.conf["info"][fileName] = [version, ""]
        #if
        else:
            version = pageInfo["version"]

        if version == self.conf["info"][fileName][0]:
            content = open(fileName).read()
            md5sum = hashlib.md5(content).hexdigest()

            if self.conf["info"][fileName][1] != md5sum:
                self.server.wiki.putPage(fileName, open(fileName).read(), {})
                self.conf["info"][fileName][0] += 1
                self.conf["info"][fileName][1] = md5sum
                self.handle.write("\nCommitted \"%s\"." % fileName)
            #if
            else:
                self.handle.write(".")
                self.handle.flush()
            #else
        #if
        else:
            self.handle.write("\nVersion error, can not commit \"%s\"." % fileName)
    #__putFile

    def checkout(self, fileName=None):
        """
        Retrieve a trac wiki page in plain text format.

        @arg fileName: Name of the page.
        @type fileName: str
        """
        if not fileName:
            for i in self.server.wiki.getAllPages():
                self.__getFile(i)
        else:
            self.__getFile(fileName)
        self.handle.write("\n")
    #checkout

    def commit(self, fileName=None):
        """
        Commit a trac wiki file.

        @arg fileName: Name of the page.
        @type fileName: str
        """
        if not fileName:
            for i in self.conf["info"]:
                self.__putFile(i)
        else:
            self.__putFile(fileName)
        self.handle.write("\n")
    #commit
#TracWiki

def config(args):
    """
    Make a configuration file for a trac server.

    @arg args: Argparse argument list.
    @type args: object
    """
    TracWiki(args.out, args.URL, args.USER, args.PASS)
#config

def checkout(args):
    """
    Retrieve a trac wiki page in plain text format.

    @arg args: Argparse argument list.
    @type args: object
    """
    T = TracWiki(args.out)

    T.checkout(args.FILE)
#checkout

def commit(args):
    """
    Commit a trac wiki file.

    @arg args: Argparse argument list.
    @type args: object
    """
    T = TracWiki(args.out)

    T.commit(args.FILE)
#commit

def main():
    """
    Main entry point.
    """
    default_parser = argparse.ArgumentParser(add_help=False)
    default_parser.add_argument("-o", dest="out", type=argparse.FileType("w"),
        default=sys.stdout, help="write output to this file")

    usage = __doc__.split("\n\n\n")
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=usage[0], epilog=usage[1])
    subparsers = parser.add_subparsers()

    parser_config = subparsers.add_parser("config", parents=[default_parser],
        description=docSplit(config))
    parser_config.add_argument("URL", type=str,
        help="base url of the trac intallation")
    parser_config.add_argument("USER", type=str, nargs='?', default="",
        help="user name")
    parser_config.add_argument("PASS", type=str, nargs='?', default="",
        help="password")
    parser_config.set_defaults(func=config)

    parser_checkout = subparsers.add_parser("checkout",
        parents=[default_parser], description=docSplit(checkout))
    parser_checkout.add_argument("FILE", type=str, nargs='?',
        help="name of the page")
    parser_checkout.set_defaults(func=checkout)

    parser_commit = subparsers.add_parser("commit", parents=[default_parser],
        description=docSplit(commit))
    parser_commit.add_argument("FILE", type=str, nargs='?',
        help="name of the page")
    parser_commit.set_defaults(func=commit)

    args = parser.parse_args()

    try:
        args.func(args)
    except ValueError, error:
        parser.error(error)
#main

if __name__ == "__main__":
    main()
