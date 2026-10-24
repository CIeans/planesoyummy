# planesoyummy
An ADS-B decoder written from scratch in python with an RTL-SDR.

For context, this is one of the main side project I spent a while working on while learning DSP.
The project is heavily annotated with just about every little detail explained on why it's there, and how it works.

The output is a simple dictionary table that lists out ICAO, callsign, altitude, speed, heading, and vertical rate.
Requires a detectable antenna connected, and the program is easy to edit if you would rather read from a file.

While running, it will check every 500 ms for any caught preambles. Uses a checksum step to confirm validity of signal.

To run, "rtl_sdr -f 1090000000 -s 2000000 -g 40 - | python planesoyummy.py" uses rtl_sdr to connect to your antenna,
and the constantly repeating flowchart will update as new data in picked up.
