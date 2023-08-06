=============================
Static HTML gallery generator
=============================

Convert pictures and videos from a directory to another directory
where the pictures are recompressed and resized and the videos are
converted to WebM, then generate the HTML pages.

Browsing is done using Colorbox, a jQuery-based Lightbox clone.



TODO
====
- modify colorbox to insert a link to the original image
- parralelize conversions using a thread pool (work is done by forking commands)
