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
                 "height": 5,
                }
FFMPEG_OPTS = {
    "mp4":  ["-acodec", "mp3", "-ab", "96k", "-ar", "44100", "-vcodec", "libx264", "-level", "21", "-refs", "2", "-b:v", "1200k", "-threads", "0", "-r", "25"],
    "webm": ["-acodec", "libvorbis", "-ac", "2", "-ab", "96k", "-ar", "44100", "-b", "1200k"],
}
FFMPEG_SIZE_RE = r'Video: .*, ([0-9]+)x([0-9]+)[^0-9]'
# Examples:
# Stream #0:0: Video: mpeg4 (Advanced Simple Profile) (XVID / 0x44495658), yuv420p, 480x640 [SAR 1:1 DAR 3:4], 30 tbr, 30 tbn, 30 tbc
# Stream #0:0(eng): Video: h264 (High) (avc1 / 0x31637661), yuv420p, 1920x1080, 12187 kb/s, SAR 65536:65536 DAR 16:9, 21.50 fps, 90k tbr, 90k tbn, 180k tbc

VIDEO_SIZE = {"width": 800, "height": 600}

USE_PIL = False # PIL can't preserve EXIF data yet (http://mail.python.org/pipermail/image-sig/2008-January/004787.html)
try:
    import PIL.Image
except ImportError:
    USE_PIL = False



from .photo import Photo, THUMB_SIZE


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
        match = re.search(FFMPEG_SIZE_RE, output)
        if match is not None:
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
        command = ["ffmpeg", "-i", self.filepath, "-vf",
                   "thumbnail,scale=%s:%s" % (self.width, self.height),
                   "-frames:v", "1", tmpfile]
        proc = Popen(command, stdout=PIPE, stderr=STDOUT)
        proc.communicate()
        return tmpfile

    def _thumb_post_process(self, img_or_command):
        thumb_width, thumb_height = self._get_new_size(
                {"width": THUMB_SIZE, "height": THUMB_SIZE})
        if USE_PIL:
            im_top = PIL.Image.open(VIDEO_THUMBS["top"])
            im_bottom = PIL.Image.open(VIDEO_THUMBS["bottom"])
            img_or_command.paste(im_top, (0, 0))
            img_or_command.paste(im_bottom, (0, thumb_height - VIDEO_THUMBS["height"]) )
        else:
            img_or_command[3:3] = [
                   "-draw", "image Over 0,0 0,0 \"%s\"" % VIDEO_THUMBS["top"],
                   "-draw", "image Over 0,%s 0,0 \"%s\""
                        % (thumb_height - VIDEO_THUMBS["height"],
                           VIDEO_THUMBS["bottom"]),
                ]


    def resize(self, resized_dir):
        """Convert to a web format (webm)"""
        new_width, new_height = self._get_new_size(VIDEO_SIZE)
        for ext, opts in FFMPEG_OPTS.iteritems():
            videopath = os.path.join(resized_dir, os.path.basename(
                                            self.filepath)[:-4] + "." + ext)
            if new_width != self.width or new_height != self.height:
                opts = opts + ["-vf", "scale=%s:%s" % (new_width, new_height)]
            if os.path.exists(videopath):
                continue
            if self.verbose:
                print "Converting %s to %s..." % (self.filename, ext)
            command = ["ffmpeg", "-y", "-i", self.filepath] + opts + [videopath]
            proc = Popen(command, stdout=PIPE, stderr=STDOUT)
            output = proc.communicate()[0]
            if proc.returncode != 0:
                print "FAILED:", " ".join(command)
                print output
                if os.path.exists(videopath):
                    os.remove(videopath)
                continue
            os.chmod(videopath, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP |
                                stat.S_IROTH) # chmod 644
        if new_width != self.width or new_height != self.height:
            self.width = new_width
            self.height = new_height
        self._to_remove.append(self.filepath) # useless (same size)


    def build_html(self, final_dir, env):
        video_tpl = env.get_template('video.html')
        htmlpath = os.path.join(final_dir, "%s.html" % self.filename[:-4])
        with open(htmlpath, "w") as htmlfile:
            htmlfile.write(video_tpl.render(video=self.to_dict()).encode("utf-8"))
