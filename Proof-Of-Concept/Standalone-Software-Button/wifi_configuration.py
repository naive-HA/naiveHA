import json
import network

configs = {}
print("Enter WiFi network name/SSID")
configs["SSID"] = input("#: ")
print("")
print("Enter WiFi network password")
configs["password"] = input("#: ")
print("")
with open('wifi_configs', 'w') as config_file:
    config_file.write(json.dumps(configs))
with open('wifi_configs', 'r') as config_file:
    config_file_content = config_file.read()
configs = json.loads(config_file_content)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
while True:
    wlan.scan()
    wlan.connect(configs["SSID"], configs["password"])
    if wlan.status() < 0 or wlan.status() >= 3:
        if wlan.status() != 3:
            #network connection failed
            time.sleep(1)
        else:
            #connected
            break
ip, mask, gateway, dns = wlan.ifconfig()
print("connect to the Control Panel by typing in your web browser")
print("http://{0}".format(ip))
print("Please note - http - not https")