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
import re
import stat
from subprocess import call, Popen, PIPE, STDOUT

from pkg_resources import resource_filename # pylint: disable-msg=E0611


RESOURCES_DIR = resource_filename(__name__, "resources")
VIDEO_THUMBS = { "top": os.path.join(RESOURCES_DIR, "images", "video-top.gif"),
                 "bottom": os.path.join(RESOURCES_DIR, "images", "video-bottom.gif"),
                 "height": 32,
                }
FFMPEG_OPTS = {
    #"mp4": ["-acodec", "libfaac", "-ab", "96k", "-vcodec", "libx264", "-level", "21", "-refs", "2", "-b", "345k", "-bt", "345k", "-threads", "0"],
    "webm": ["-acodec", "libvorbis", "-ac", "2", "-ab", "96k", "-ar", "44100", "-b", "345k"],
}

USE_PIL = False # PIL can't preserve EXIF data yet (http://mail.python.org/pipermail/image-sig/2008-January/004787.html)
try:
    import PIL.Image
except ImportError:
    USE_PIL = False



from .photo import Photo


class Video(Photo):


    def __init__(self, filepath, verbose=False):
        Photo.__init__(self, filepath, verbose)
        self.type = "video"
        self._to_remove = []


    def process(self, final_dir):
        """Main entry point"""
        d = Photo.process(self, final_dir)
        for f in self._to_remove:
            os.remove(f)
        return d


    def set_size(self):
        process = Popen(["ffmpeg", "-i", self.filepath], stdout=PIPE, stderr=STDOUT)
        output = process.communicate()[0]
        if output:
            match = re.search('Video: .*, ([0-9]+)x([0-9]+) ', output)
            self.width = int(match.group(1))
            self.height = int(match.group(2))
        else:
            self.width = 640
            self.height = 480


    def set_title(self):
        self.title = ""


    def to_dict(self):
        d = Photo.to_dict(self)
        d["large_url"] = "%s.html" % self.filename[:-4]
        d["sources"] = [ ("%s.%s" % (self.filename[:-4], ext), "video/%s" % ext)
                         for ext in FFMPEG_OPTS.keys() ]
        return d


    def _thumb_source(self):
        tmpfd, tmpfile = tempfile.mkstemp(".jpg")
        os.close(tmpfd)
        self._to_remove.append(tmpfile)
        command = ["ffmpeg", "-vframes", "1", "-i", self.filepath,
                   "-ss", "00:00:01.000", "-y", "-f", "mjpeg", tmpfile]
        with open("/dev/null", "w") as devnull:
            call(command, stdout=devnull, stderr=devnull)
        return tmpfile

    def _thumb_post_process(self, img_or_command):
        if USE_PIL:
            im_top = PIL.Image.open(VIDEO_THUMBS["top"])
            im_bottom = PIL.Image.open(VIDEO_THUMBS["bottom"])
            img_or_command.paste(im_top, (0, 0))
            img_or_command.paste(im_bottom, (0, self.height - VIDEO_THUMBS["height"]) )
        else:
            img_or_command[1:1] = [
                   "-draw", "image Over 0,0 0,0 \"%s\"" % VIDEO_THUMBS["top"],
                   "-draw", "image Over 0,%s 0,0 \"%s\""
                        % (self.height - VIDEO_THUMBS["height"],
                           VIDEO_THUMBS["bottom"]),
                ]


    def resize(self, resized_dir):
        """Convert to a web format (webm)"""
        for ext, opts in FFMPEG_OPTS.iteritems():
            videopath = os.path.join(resized_dir, os.path.basename(
                                            self.filepath)[:-4] + "." + ext)
            if os.path.exists(videopath):
                continue
            with open("/dev/null", "w") as devnull:
                retcode = call(["ffmpeg", "-y", "-i", self.filepath] + opts + [videopath],
                               stdout=devnull, stderr=devnull)
            if retcode != 0:
                os.remove(videopath)
                continue
            os.chmod(videopath, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP |
                                stat.S_IROTH) # chmod 644
            if self.verbose:
                print "Converted %s to %s..." % (self.filename, ext)
        self._to_remove.append(self.filepath) # useless (same size)


    def build_html(self, final_dir, env):
        video_tpl = env.get_template('video.html')
        htmlpath = os.path.join(final_dir, "%s.html" % self.filename[:-4])
        with open(htmlpath, "w") as htmlfile:
            htmlfile.write(video_tpl.render(video=self.to_dict()).encode("utf-8"))
