from led import LED
from button import BUTTON
from const import _LED_MODES
from networkd import NETWORKD

LED_MODES = _LED_MODES()

if __name__ == "__main__":
    light = LED()
    light.start()
    def set_led_mode(flag: int) -> None:
        light.display(flag)
        return None

    def packet_received(data: str) -> None:
        print("received data " + data)
        return None

    network_daemon = NETWORKD()
    network_daemon.set_led_mode = set_led_mode
    network_daemon.packet_received = packet_received

    network_daemon.start()
    network_daemon.accept_node_connection(600)

    def trigger_action() -> None:
        set_led_mode(LED_MODES.TRIGGER_ACTION)
        network_daemon.send_packet(0, "hello")

    trigger = BUTTON()
    trigger.event_detected = trigger_action
    trigger.start()

    if input("end?: "):
        trigger.stop()
        light.stop()
        network_daemon.stop()
        
