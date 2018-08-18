# SimpleSumpple

A simple monitoring console for Foscam-compatible still and motion cameras (I happen to be using the Sumpple brand, but they use the well-cloned Foscam REST interface, as do most cheap security cameras on Amazon).  The goal here is to:

1) Be able to store a large number of images (similar to how a hunting/game camera works) while selectively "thinning" the stored image folder (e.g. store hourly after one week, daily after 1 month, monthly after 1 year)

2) Have a an HTML interface that will poll both motion (via the Foscam "snapshot" function) and still cameras into a multi-panel display while allowing one to (via a single click) go into the PTZ (pan-tilt-zoom) interface for that camera (if supported).

