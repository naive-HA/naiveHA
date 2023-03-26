# Scope
This proof of concept intends to demonstrate the communication protocol between the coordinator and nodes via SSL sockets

# The setup
The system needs a coordinator who will engage various nodes in performing various actions. The coordinator is a Raspberry Pi Zero 2 W running 32-bit Raspberian OS. Instructions to setup the coordinator are found in `coordinator` folder.

The nodes are Raspberry Pi Pico W. The MicroPython implementation for Pico W is under constant development. Although the latest version of firmware assumes better capabilities, it cannot be guaranteed that the rolling updates will not introduce change that break the code demonstrated here. Thus, the code demonstrated here was successfully tested with the firmware `rp2-pico-w-20230323-unstable-v1.19.1-992-g38e7b842c.uf2` available in the folder `node`
To demonstrate the proof of concept, a power plug will be turned ON/OFF. The power plug is commercially available and is intended to be operated remotely via a 433MHz remote control. This remote control will be substituted by a 433MHz transmitter module wired to the node. Instructions on how to sniff the RF signal transmitted by the remote control are found in the folder `node/RF`

# Coordinator-node communication
Nodes connect to coordinator via wifi on port 65432. Once the comnection is established, the node and the coordinator authenticate each other by exchanging openSSL x509 certificates. These certificates are signed by a self established Certification Authority. Details on how to generate the certificates are shown in `SSL` folder

# Modus operandi
Upon system boot, the coordinator will automatically seek to join the wifi network and display a red LED. Once the wifi connection is established, the coordinator will accept connections from nodes on port 65432 and display a blue LED light. When the node connects, the LED light will turn off.

Upon powering up, the node will seek to join the wifi network and the on board LED will blink fast. Once the network connection is established the node will seek to connect to the coordinator and the LED will blink slowly. When the node successfully connects to the coordinator, the LED will turn off.

Events are triggered via the wired button fitted to the coordinator. Pressing the button the LED turns green and a signal is sent to the node to toggle the sate of the remote power plug. A video demonstration is available on youtube:
[![demonstration of concept](https://img.youtube.com/vi/lHx3oAHH-9Y/0.jpg)](https://www.youtube.com/watch?v=lHx3oAHH-9Y)

