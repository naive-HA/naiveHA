# Standalone Software Button
This proof of concept demonstrates the graphical inteface of naiveHA. To this end, a Raspberry Pi Pico W is put to use, along a few breakout modules: an Infrared transmitter to mimic IR remote control, a 433MHz Radio Frequency transmitter to mimic a RF remote control and a temperature sensor.
The Raspberry Pi Pico W receives commands via WiFi, executes and then returns the status. The graphical interface is a web page, written in html/css/javascript, served by Raspberry Pi Pico W upon connecting via a web browser, like Chrome of Firefox.

# Controlling a power outlet
First, a commercially available power outlet is control remotely by mimicing its 433MHz remote control.
![arlec power outlet](https://raw.githubusercontent.com/naive-HA/naiveHA/main/Proof-Of-Concept/Standalone-Software-Button/IMG_20230319_194943_204.jpg)

The RF signals are sent by a cheap breakout module:
![RF module](https://raw.githubusercontent.com/naive-HA/naiveHA/main/Proof-Of-Concept/Standalone-Software-Button/IMG_20230409_173019_605.jpg)

The graphical interface is straightforward: it features an ON/OFF button

![graphical interface](https://raw.githubusercontent.com/naive-HA/naiveHA/main/Proof-Of-Concept/Standalone-Software-Button/Screenshot_20230409-170044.png)

The workflow is demonstrated in the below video. In this video, controlling the power outlet achieves the control of a bed side lamp. But other use cases could be imagined: like the control of ceiling lights, a ceiling fan, a cheap heater, etc. The only limits are your imagination.
The workflow is demonstrated in the below video

[![demonstration of concept](https://img.youtube.com/vi/iH8CAHKDYGw/0.jpg)](https://www.youtube.com/watch?v=iH8CAHKDYGw)

# Controlling a heater panel
A second demonstration shows a more complex case then the previous one which considered toggle two states: ON/OFF. In the current case, a commercially available heater panel is controlled via a cheap infrared transmitting module mimicing the IR remote control. For advance control, the setup includes also a AHT20 temperature sensor
![IR module](https://raw.githubusercontent.com/naive-HA/naiveHA/main/Proof-Of-Concept/Standalone-Software-Button/IMG_20230409_173001_261.jpg)

In the current case, the graphical interface is a tad more complex and features controls for heat level, fan and target temperature

![graphical interface](https://raw.githubusercontent.com/naive-HA/naiveHA/main/Proof-Of-Concept/Standalone-Software-Button/Screenshot_20230409-170052.png)

![graphical interface](https://raw.githubusercontent.com/naive-HA/naiveHA/main/Proof-Of-Concept/Standalone-Software-Button/Screenshot_20230409-170058.png)

The workflow is demonstrated in the below video

[![demonstration of concept](https://img.youtube.com/vi/w7Tisz9hLJI/0.jpg)](https://www.youtube.com/watch?v=w7Tisz9hLJI)