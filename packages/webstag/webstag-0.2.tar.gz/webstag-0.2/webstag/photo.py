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


import os
import tempfile
from subprocess import call, Popen, PIPE, STDOUT


THUMB_DIR = "_thumbs"
THUMB_SIZE = 150
IMG_SIZE = {"width": 800, "height": 600}

USE_PIL = False # PIL can't preserve EXIF data yet (http://mail.python.org/pipermail/image-sig/2008-January/004787.html)
try:
    import PIL.Image
except ImportError:
    USE_PIL = False



class PhotoError(Exception): pass


class Photo(object):

    def __init__(self, filepath, verbose=False):
        self.filepath = filepath
        self.verbose = verbose
        self.filename = os.path.basename(self.filepath)
        self.type = "photo"
        self.width = None
        self.height = None
        self.portrait = None
        self.title = None
        self.thumb_margin = 0


    def process(self, final_dir):
        """Main entry point"""
        self.set_size()
        self.set_orientation()
        self.set_title()
        self.resize(final_dir)
        thumb_dir = os.path.join(final_dir, THUMB_DIR)
        self.make_thumbnail(thumb_dir)
        return self.to_dict()


    def set_size(self):
        """Portrait or landscape format ?"""
        if USE_PIL:
            im = PIL.Image.open(self.filepath)
            self.width, self.height = im.size
        else:
            process = Popen(["identify", self.filepath], stdout=PIPE, stderr=STDOUT)
            output = process.communicate()[0]
            if self.filepath.lower().endswith(".jpg") or self.filepath.lower().endswith(".jpeg"):
                properties = output.split(" JPEG ")[1]
            elif self.filepath.lower().endswith(".gif"):
                properties = output.split(" GIF ")[1]
            elif self.filepath.lower().endswith(".png"):
                properties = output.split(" PNG ")[1]
            else:
                print "Can't identify %s !" % self.filepath
                raise PhotoError(self.filepath)
            size = properties.split(" ")[0].split("x")
            self.width = int(size[0])
            self.height = int(size[1])


    def set_orientation(self):
        """Portrait or landscape format ?"""
        self.portrait = False
        if self.height > self.width:
            self.portrait = True


    def set_title(self):
        """Find title (IPTC Object Name)"""
        origlink = u"<a href=\"original/%s\">haute rés.</a>" \
                    % self.filename
        #proc = Popen(["iptc", "-p", "2:005", self.filepath],
        #             stdout=PIPE, stderr=STDOUT)
        #output = proc.communicate()[0]
        #if proc.returncode == 0:
        #    self.title = u"%s (%s)" % (output.strip(), origlink)
        #else:
        #    self.title = origlink
        self.title = origlink


    def resize(self, resized_dir):
        resized_path = os.path.join(resized_dir, self.filename)
        if os.path.exists(resized_path):
            return
        if self.verbose:
            print "Resizing %s" % self.filename
        if USE_PIL:
            im = PIL.Image.open(self.filepath)
            outim = im
            new_width, new_height = self._get_new_size(IMG_SIZE)
            outim = im.resize((new_width, new_height), PIL.Image.ANTIALIAS)
            outim.save(resized_path, quality=90)
        else:
            tmpfd, tmpfile = tempfile.mkstemp(".jpg")
            os.close(tmpfd)
            if self.height > IMG_SIZE["height"]:
                call(["convert", "-resize", "x%s" % IMG_SIZE["height"],
                      self.filepath, tmpfile])
            elif self.width > IMG_SIZE["width"]:
                call(["convert", "-resize", IMG_SIZE["width"], self.filepath, tmpfile])
            call(["convert", "-quality", "90", tmpfile, resized_path])
            os.remove(tmpfile)


    def _get_new_size(self, limit, size=None):
        if size is None:
            size = {"width": self.width, "height": self.height}
        new_width = size["width"]
        new_height = size["height"]
        if self.portrait and size["height"] > limit["height"]:
            new_height = limit["height"]
            new_width = int(round(size["width"] * limit["height"]
                            / float(size["height"]))) # keep proportion
        elif not self.portrait and size["width"] > limit["width"]:
            new_width = limit["width"]
            new_height = int(round(size["height"] * limit["width"]
                             / float(size["width"]))) # keep proportion
        return new_width, new_height


    def make_thumbnail(self, thumb_dir):
        # Set thumb margin
        thumb_width, thumb_height = self._get_new_size(
                {"width": THUMB_SIZE, "height": THUMB_SIZE})
        self.thumb_margin = (150 - thumb_height) / 2
        # Build thumbnail
        thumb_filename = os.path.join(thumb_dir, self.filename[:-4]+".jpg")
        if os.path.exists(thumb_filename):
            return
        if self.verbose:
            print "Building thumbnail for %s..." % self.filename
        # Prepare thumbnails dir
        if not os.path.exists(thumb_dir):
            os.mkdir(thumb_dir)
        thumb_source = self._thumb_source()
        if USE_PIL:
            im = PIL.Image.open(thumb_source)
            outim = im.resize((thumb_width, thumb_height), PIL.Image.ANTIALIAS)
            self._thumb_post_process(outim)
            outim.save(thumb_filename, quality=90, dpi=(120, 120))
        else:
            size = THUMB_SIZE
            if self.portrait:
                size = "x%s" % THUMB_SIZE
            command = ["convert", "-geometry", str(size), thumb_source, thumb_filename]
            self._thumb_post_process(command)
            call(command)

    def _thumb_source(self):
        return self.filepath

    def _thumb_post_process(self, img_or_command):
        pass


    def to_dict(self):
        return {
                "type": self.type,
                "large_url": self.filename,
                "thumb_url": "%s/%s" % (THUMB_DIR, self.filename[:-4] + ".jpg"),
                "orig_url": "original/%s" % self.filename,
                "title": self.title,
                "portrait": self.portrait,
                "filename": self.filename,
                "width": self.width,
                "height": self.height,
                "thumb_margin": self.thumb_margin,
        }


    def build_html(self, final_dir, env):
        pass
