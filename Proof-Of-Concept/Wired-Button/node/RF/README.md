# Scope
Replaying 433MHz radio frequency signals using cheap breakout modules requires sniffing/capturing the signal played by the remote control.

# Hardware
First of all, to sniff the 433MHz signals specialized hardware is needed. Several options are available, but a cheap (and reliable) option is RTL-SDR RTL2832U DVB-T Tuner Dongles (https://www.rtl-sdr.com/buy-rtl-sdr-dvb-t-dongles/).

# Software
The hardware is paired with a compatible software. The best option is URH (Universal Radio Hacker) https://github.com/jopohl/urh
To enable the hardware under windows a driver is required: zadig-2.8, which can be found at https://zadig.akeo.ie/

Once everything installed is time to capture buttons. Open URH, select the device: RTL-SDR, click refresh and press Start button
![start capturing](https://raw.githubusercontent.com/naive-HA/naiveHA/main/Proof-Of-Concept/Wired-Button/node/RF/1.png)


Next, press a button on the remote control and once the signal is captured, click Stop buton, close the current inner window and save to progress to the next stage
![record the signal](https://raw.githubusercontent.com/naive-HA/naiveHA/main/Proof-Of-Concept/Wired-Button/node/RF/2.png)
***
It is time to analyze the signal: switch to "Hex" view and the signal is displayed as a sequence of codes, in this particular case, a sequence of "8" and "e". We will make use of this sequence in the code found at `node/rf.py`

![](https://raw.githubusercontent.com/naive-HA/naiveHA/main/Proof-Of-Concept/Wired-Button/node/RF/3.png)
***
Each "8" or "e" is actually made of either a short or long high pulse or low pulse (or pause). Siwtch to a demodulated view and zoom in to better view the signal. Make use of the below instructions and note the duration of these pulses. These will be used in the code `node/rf.py`. N.B. although here the durations are different for pusle, in the code only 2 durations are used: 285 microseconds and, respectively, 865. Furthermore, the code scales down these initial durations, as computations are employed in between the time the breakout module is instructed to change to a different state: high to low pulse or vice-versa. You area hacker by now: experiement with the setup and even sniff back the signal broadcast by the breakout module to check that the replayed signal matches the signal broadcast by the origianl remote control.
![](https://raw.githubusercontent.com/naive-HA/naiveHA/main/Proof-Of-Concept/Wired-Button/node/RF/4.png)

![](https://raw.githubusercontent.com/naive-HA/naiveHA/main/Proof-Of-Concept/Wired-Button/node/RF/5.png)

![](https://raw.githubusercontent.com/naive-HA/naiveHA/main/Proof-Of-Concept/Wired-Button/node/RF/6.png)


![](https://raw.githubusercontent.com/naive-HA/naiveHA/main/Proof-Of-Concept/Wired-Button/node/RF/7.png)

![](https://raw.githubusercontent.com/naive-HA/naiveHA/main/Proof-Of-Concept/Wired-Button/node/RF/8.png)


