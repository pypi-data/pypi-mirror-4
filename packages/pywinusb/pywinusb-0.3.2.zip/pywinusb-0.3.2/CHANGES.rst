Release changes
===============

0.3.2
-----

 * Python 3 filtering fix

0.3.1
-----

 * Python 2 and 3 support (tested with Python 3.2)

0.3.0
-----

 * Refactored setup api handling.

 * Many PyLint fixes.

0.2.9
-----

 * Fixed broken value array usages transactions

 * Better Setup API device paths handling

0.2.8
-----

 * Fixed broken value array usages transactions

0.2.7
-----

 * Fixing sending output / feature reports

0.2.6
-----

 * Fixed broken input report handling

 * Stability improvements

0.2.5
-----

 * Tweaked PnP example, added frame closing event handler, so the USB device is closed

 * Report reading threads and device closing optimizations

0.2.4
-----

 * Fixed bugs preventing properly setting report usage variables after a HidReport().get()

 * Fixed raw_data.py example

 * Fixed bug preventing proper value array setting/getting items

 * Fixed deadlock when device unplugged

0.2.3
-----

 * Added HidDevice.set_raw_data_handler(), and corresponding raw_data.py example script

0.2.2
-----

 * Fixing output only mode (no input report for forced open)

0.2.1
-----

 * Bringing a little bit of stability

 * Output only mode (no reading thread configured)

 * Kind of usable now

0.1.0 
-----

 * First public release

