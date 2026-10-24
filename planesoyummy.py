import numpy as np
import math
import matplotlib.pyplot as plt # was using it during testing. keeping it incase needed
import sys
import os  # why are there so many imports
import time # here comes another one. jeez.

gen = [int(x) for x in format(0x1FFF409, '025b')]  # later used for checksum                           # these 3 are the setup parts for later
chars = "#ABCDEFGHIJKLMNOPQRSTUVWXYZ#####_###############0123456789######" # later used for callsign
planes = {}                                        # plain plane

def to_num(b): 
    return int("".join(str(x) for x in b), 2)      # bits to number convertor. loops through each bit turning it into a string, then uses int by base 2

def decode(mag):
    s = 0
    while (s < len(mag) - 240):
    # so basically mag refers to the amplitude and we're checking each signal as its coming in on i and q (so mag, basically)

    # and as a result the purpose of this is to say "for each signal if it has a preample, accept it. decline and move on if not
            # the planned route is basically;
    #   !  # step 1: check for preamble and start reading if found
        if ((mag[s] > 8) and (mag[s+2] > 8) and (mag[s+7] > 8) and (mag[s+9] > 8)) and ((mag[s+1] < 4) and (mag[s+3] < 4) and (mag[s+4] < 4) and (mag[s+5] < 4) and (mag[s+6] < 4) and (mag[s+8] < 4)):
            bits = [] # the binary result!
    #   !  # step 2: turning the signal into binary (data)
            for k in range(112): # so this is the "signal to 0 and 1's" equivalent
                if mag[s + 16 + 2*k] > mag[s + 17 + 2*k]:
                    bits.append(1) # if mag(s1) > mag(s2), first half greater. append 1
                else:
                    bits.append(0) # if mag(s1) < mag(s2), second half greater. append 0.
        
    #   !  # step 3: make the checksum
                # for info, the checksum is the latter 25 bits end. its mathematically added
                # so that every full 112 bit signal is divisible by checksums constant (gen)
                # this means to divide, we need to basically use long division of mag_divisible_number divided by mag
                # if any of the numbers divide wrong, it means the signal is faulty. a bit got muddied and misread.
                # this just makes sure we have a good healthy proper read signal.

            c = bits.copy()  # building the checksum calculation into a copy of bits
            for j in range(88): 
                if c[j] == 1: # if c[j] is one, then along the entire range of gen (25 bits),
                    for n in range(25): 
                        c[j+n] = (gen[n]^c[j+n]) # checksum by long dividing (using XOR)
        
    #   !  # step 4: verify if checksum succeeded to signal read alas
            if c[88:] == [0]*24: # compares checksummed[88:] to 24 0's, meaning it divided correctly.
                num = to_num(bits[8:32]) # established early for hexid
                name = ""
                hexid = format(num, "06X") # for formatting later. its the planes ICAO address.

    #     !    # step 5: start preparing for signal reading. establish type check.
                tc = to_num(bits[32:37]) # type check. 
                    # if 1-4: identification. the bits 40+ are call sign
                    # if 9-18: airborne position. the bits 40+ are altitude
                    # if 19: velocity. the bits 40+ are speed and heading
            
    #     !    # step 6: start compiling dictionary for data display
                if hexid not in planes: # obligatory plane dictionary organizing
                    planes[hexid] = {"call": "", "altitude": "", "speed": "", "heading": "", "vertical": "", "msgs": 0}
                planes[hexid]["msgs"] += 1 # counts each time it updates planes[hexid]  

    #     !    # step 7: signal reading after 40! uses the type check to know what to expect
                if (1 <= tc <= 4): # 1-4. bits 40+ are callsign.
                    for n in range(8):
                        num = to_num(bits[40+6*n : 46+6*n]) # calls are 6 bits, 8 characters long.
                        name += (chars[num]) # builds the call up
                    name = name.replace("_", "") # visual preference. removes the padding names include
                    planes[hexid]["call"] = name
            
    #     !    # step 7.1: altitude variant for type check.
                if (9 <= tc <= 18): # 9-18. bits 40+ are altitude
                    altitude = bits[40:52] 
                    if altitude[7] == 1: # this is called the q bit! it is a flag in the middle of the 12 bits meaning '25 step'.
                        altitude = to_num(altitude[:7] + altitude[8:])*25-1000 # re-attaches the numbers :7 + 8: (around the q bit), multiplies by step (25 ft) and removes 1000 for sea level.
                        planes[hexid]["altitude"] = altitude 

                # step 7.2: speed variant for type check. 
                if tc == 19: # 19. bits+ are multiple pieces of directional movement

                    if bits[45] == 1: # direction bit. east 0 , west 1
                        ew = -(to_num(bits[46:56]) - 1) # calculating east-west speed in knots by using bits 46:56
                    else: 
                        ew = to_num(bits[46:56]) - 1
              
                    if bits[56] == 1: # direction bit. north 0 , south 1
                        ns = -(to_num(bits[57:67]) - 1) # calculating north-south speed in knots by using bits 57:67
                    else: 
                        ns = to_num(bits[57:67]) - 1 

                    if bits[68] == 1: # direction bit. up 0 , down 1
                        ud = -((to_num(bits[69:78]) - 1)*64) # calculating vertical rate in ft/min by using bits 69:78
                    else: 
                        ud = (to_num(bits[69:78]) - 1)*64 # theres probably a better cleaner way to make these 'else's negative but i dont have any ideas

                    speed = round(math.hypot(ew, ns)) # written seperate just for cleanliness. this makes a hypotenuse, basically.
                    heading = round(math.degrees(math.atan2(ew, ns))) % 360 # this makes a circle for heading
                    planes[hexid]["speed"] = speed
                    planes[hexid]["heading"] = heading
                    planes[hexid]["vertical"] = ud
                
                # step 7.3: adding this after already finishing the program, just wanted to add a 'clear old planes' thing like dump1090 does.
                planes[hexid]["seen"] = time.time()

        s += 1 # keeps it looping

# end of entire signal catching loop

def show(): # step 8: dictionary formatting. sits outside the main loops!
    os.system('cls')
    print(f"{'hex':<8}{'call':<10}{'alt (ft)':>10}{'speed (kt)':>11}{'hdg (°)':>8}{'vert (ft/m)':>12}{'msgs':>6}")
    for h in list(planes):
            if (time.time() - planes[h]['seen']) > 60:
                del planes[h]
                continue        # so that it doesnt try to print the plane i just deleted lol
            print(f"{h:<8}{planes[h]['call']:<10}{planes[h]['altitude']:>10}{planes[h]['speed']:>11}{planes[h]['heading']:>8}{planes[h]['vertical']:>12}{planes[h]['msgs']:>6}")

# final! step 9: basically the 'flowgraph' portion because i want this to run actively instead of off a file (like my first version did!)
while True:
    chunk = sys.stdin.buffer.read(2000000)             # reads every 0.5 sec of data
    if not chunk: break                                # streams have to end eventually!
    raw = np.frombuffer(chunk, dtype=np.uint8)         # idk what this lowkey does
    i = raw[0::2] - 127.5                              # every even byte = i
    q = raw[1::2] - 127.5                              # every odd byte  = q
    mag = np.sqrt(i**2 + q**2)                         # complex numbers from signals to magnitude (for processing)
    decode(mag)
    show()                                             
    print("noise:", np.median(mag), "loudest:", mag.max()) # i added this later for debugging. its nice info so im personally keeping it


# this is the antenna input taker below! its preconfigured. frequency, sample rate, and gain are f s and g respectively
# rtl_sdr -f 1090000000 -s 2000000 -g 40 - | python planesoyummy.py
