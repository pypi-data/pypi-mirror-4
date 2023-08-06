# -*- coding: utf-8 -*-
# vim: set expandtab tabstop=4 shiftwidth=4 :

"""
Copyright (C) 2008-2013 Aurelien Bompard <aurelien@bompard.org>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


import sys
import os
import optparse
import shutil
import re
import stat
import locale
import datetime
import random
import string # pylint: disable-msg=W0402
import tempfile

from pkg_resources import resource_filename # pylint: disable-msg=E0611
from jinja2 import Environment, PackageLoader

from .photo import Photo
from .video import Video



class Convertor(object):


    def __init__(self, directory, options):
        self.directory = directory
        self.options = options
        self.final_dir = None
        self.metadata = { "title": "", "date": "", }
        self.items = []
        if self.options.ressources_url is not None:
            self.metadata["resources_url"] = self.options.ressources_url
        else:
            self.metadata["resources_url"] = "resources"


    def get_final_dir(self):
        dir_clean = get_clean_name(os.path.basename(self.directory))
        if self.options.password:
            passwd = "".join(random.choice(string.ascii_letters)
                             for i in range(8))
            dir_clean = "%s_%s" % (dir_clean, passwd)
        return os.path.join(self.options.dest, dir_clean)


    def run(self):
        """ Go through all directories specified on the command line, and
        convert them to the dest dir """
        self.final_dir = self.get_final_dir()
        self.copy_images()
        self.extract_metadata()
        print "Recompressing images and building thumbnails from %s..." % self.directory
        files = os.listdir(os.path.join(self.final_dir, "original"))
        files.sort()
        inc = 0
        for f in files:
            inc += 1
            item = self.process_file(f)
            if item is None:
                continue # unknown file format
            self.items.append(item)
            if not self.options.verbose: # Nice progress counter
                sys.stdout.write("\r")
                sys.stdout.write("[%s/%s]" % (inc, len(files)))
                sys.stdout.flush()
        if not self.options.verbose:
            print
        self.build_static_html()
        print "The generated static directory is: %s" % self.final_dir


    def copy_images(self):
        """Copy the original dir to the temp dir (if not yet done)"""
        if os.path.exists(os.path.join(self.final_dir, "original")):
            try:
                print "The final directory already exists:", self.final_dir
                print "Should I go on anyway (no file will be overwritten) ? [Y/n]"
                rep = raw_input()
            except KeyboardInterrupt:
                print "Aborted."
                sys.exit(1)
            if rep.strip() == "n":
                print "Skipped %s !" % self.directory
                return
        else:
            os.makedirs(os.path.join(self.final_dir, "original"))
        print "Copying images..."
        for filepath in list_recursive(self.directory):
            finalpath = os.path.join(self.final_dir, "original",
                                     os.path.basename(filepath))
            if os.path.exists(finalpath):
                continue
            shutil.copy(filepath, finalpath)
            os.chmod(finalpath, stat.S_IRUSR | stat.S_IWUSR |
                                stat.S_IRGRP | stat.S_IROTH) # chmod 644


    def extract_metadata(self):
        dir_name = os.path.basename(self.directory.rstrip("/"))
        # I usually name my photo dirs this way : "2008-06-16 Joe's birthday"
        # Pre-fill the metadata if that's the format we find
        match = re.match('(20\d\d-\d\d-\d\d) (.*)', dir_name)
        if match:
            title = match.group(2)
            date = match.group(1)
            date = datetime.date(int(date[0:4]), int(date[5:7]), int(date[8:10]))
            date = date.strftime("%A %d %B %Y").capitalize()
        else:
            title = dir_name
            date = ""
        self.metadata["title"] = title.decode(sys.getfilesystemencoding())
        self.metadata["date"] = date.decode("utf-8")


    def process_file(self, f):
        """ Handle each picture or movie """
        filepath = os.path.join(self.final_dir, "original", f)
        if f.lower()[-4:] in [".avi", ".wmv", ".mov", ".mp4"]:
            item_class = Video
        elif not ( f.lower()[-4:] in [".jpg", ".gif", ".png"]
                or f.lower().endswith(".jpeg") ):
            # Unknown file format
            os.remove(filepath) # don't upload it
            return
        else:
            item_class = Photo
        item = item_class(filepath, verbose=self.options.verbose)
        item.process(self.final_dir)
        return item


    def build_static_html(self):
        # create the HTML with Jinja
        env = Environment(loader=PackageLoader(__name__, 'templates'))
        variables = self.metadata.copy()
        variables["files"] = [ item.to_dict() for item in self.items ]
        # Main HTML file
        template = env.get_template('base.html')
        with open(os.path.join(self.final_dir, "index.html"), "w") as index:
            index.write(template.render(variables).encode("utf-8"))
        # Sub HTML files
        for item in self.items:
            item.build_html(self.final_dir, env)
        # copy static ressources
        res_dir = os.path.join(self.final_dir, "resources")
        if not os.path.exists(res_dir) and self.options.ressources_url is None:
            shutil.copytree(resource_filename(__name__, "resources"), res_dir)
        if self.options.verbose:
            print "Generated HTML"



def list_recursive(dirname):
    for root, dirs, files in os.walk(dirname):
        for name in files:
            if name.startswith("."):
                continue
            yield os.path.join(root, name)
        # Don't visit hidden directories
        for d in dirs:
            if d.startswith("."):
                dirs.remove(d)


def get_clean_name(dirname):
    """ Replace non-ascii chars by their equivalent """
    dir_clean = dirname.replace(" ", "_").replace("'", "").replace('"', '')
    dir_clean = dir_clean.lower()
    # dirty, but efficient ! :)
    mapping = { "é":"e", "è":"e", "ê":"e", "ç":"c", "à":"a", "â":"a", "ô":"o", "î":"i", "ï":"i", }
    for key in mapping:
        dir_clean = dir_clean.replace(key, mapping[key])
    dir_clean = dir_clean.decode("utf-8").encode("ascii", "ignore")
    return dir_clean


def parse_opts():
    usage = "usage: %prog [options] original-folder [original-folder-2 ...]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-d", "--destination", dest="dest",
                      help="the resulting files will be placed in this folder")
    parser.add_option("-p", "--password", action="store_true",
                      help="add a random password to the generated directory name")
    parser.add_option("-r", "--ressources-url", help="URL to the static "
                      "ressources directory, if already uploaded")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose")

    (options, args) = parser.parse_args()
    if len(args) == 0:
        parser.error("must specify a directory to process")
    if not options.dest:
        options.dest = tempfile.gettempdir()
    for directory in args:
        if not os.path.exists(directory) or not os.path.isdir(directory):
            parser.error('The directory %s does not exist.' % directory)
    directories = [ os.path.normpath(d) for d in args ]

    print
    print "Folder(s) to process:", ", ".join(directories)
    print "Destination folder:", options.dest
    total_files = 0
    for directory in directories:
        total_files += len(list(list_recursive(directory)))
    print "Number of files to be processed:", total_files
    print "Is it OK ? (Ctrl-C to abort)"
    raw_input()
    return options, directories


#### MAIN ####

def main():

    try:
        options, dirs = parse_opts()
    except KeyboardInterrupt:
        print "Aborted."
        sys.exit(0)
    # set the correct locale for the names of the days and months
    locale.setlocale(locale.LC_ALL, '')
    dirs.sort()
    try:
        for directory in dirs:
            convertor = Convertor(directory, options)
            convertor.run()
    except KeyboardInterrupt:
        print "\rExiting on user request."



if __name__ == '__main__' : main()
