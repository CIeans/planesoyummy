# planesoyummy
An ADS-B decoder written from scratch in python with an RTL-SDR.  
  
For context, this is one of the main side projects I spent a while working on while learning DSP.  
The .py file is heavily annotated with every step numbered, and most of the unintuitive code is explained in simpler terms.  
  
The output is a simple dictionary table that lists out ICAO, callsign, altitude, speed, heading, and vertical rate.\
Requires an RTL-SDR dongle with an antenna, Python 3, numpy, and the rtl_sdr tools (comes with radioconda).
  
The project was heavily inspired by my initial dive into DSP, with my discovery of dump1090.\
Results were cross-checked with dump1090, ensuring both programs caught the same ADS-B signals.

  
## How It Works:
- While running, it will check every 500 ms for any caught preambles. 
- Slices caught signals into 112 bits, using a checksum step (CRC-24 check) to confirm validity of signal.
- Most of the given data in the ADS-B signal is decoded into callsign/altitude/velocity.
- Not seen in the screenshot below, but planes that haven't been picked up for 60s get dropped from the table. 

    
The only missing data is latitude and longitude, which I’d like to plot on a matplotlib map. \
Given it's a bit beyond my current scope, it's something I hope to soon come back to and add. 

    
<img width="632" height="248" alt="image" src="https://github.com/user-attachments/assets/44a930c5-8efe-4f80-9a3c-3e558fe618a8" />   
      
      
To run, the command below uses the rtl_sdr tool, connecting to the dongle with radioconda. \
The frequency is 1090 MHz, which aviation transponders use. Gain and sample rate can be changed if needed. 

```
rtl_sdr -f 1090000000 -s 2000000 -g 40 - | python planesoyummy.py
```
