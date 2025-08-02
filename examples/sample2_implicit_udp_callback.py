"""
Example: Using EEIPClient with UDP receive callback and auto UDP sending (Sensor Event/Acknowledgment)

This example demonstrates how to use the EEIPClient class to connect to an EtherNet/IP PLC, set up a callback function for receiving UDP data (implicit messaging), and send an acknowledgment back to the PLC when a sensor event is detected.

Scenario:
- The PLC is configured to send implicit messages to this client when a sensor triggers (e.g., digital input changes).
- The client receives the UDP message, processes the sensor event, and sends an acknowledgment UDP packet back to the PLC.

How it works:
- The EEIPClient is configured to connect to the PLC.
- A user-defined callback function is registered using set_udp_receive_callback().
- When the PLC sends a UDP message (e.g., on sensor event), the callback is invoked with the received bytes.
- The client processes the data and sends an acknowledgment UDP packet back to the PLC.
"""
import time
from eeip.eipclient import EEIPClient


class MessageProcessor:
    """
    Processes incoming UDP messages from the PLC and sends acknowledgments if a sensor event is detected.
    """
    def __init__(self, eeipclient):
        self.eeipclient = eeipclient

    def process(self, data):
        print(f"[CALLBACK] Received UDP data from PLC: {data.hex()}")
        # Example: Check if a sensor bit is set (e.g., first byte, bit 0)
        if data and (data[0] & 0x01):
            print("Sensor event detected! Sending acknowledgment...")
            ack = bytes([0xAC])
            self.eeipclient.send_udp_explicitly(ack)
            print("Acknowledgment sent.")
        else:
            print("No sensor event in this packet.")


def main():
    # Replace with your PLC's IP address
    target_ip = "192.168.1.10"

    eeipclient = EEIPClient()
    processor = MessageProcessor(eeipclient)

    # Set the UDP receive callback to the processor's process method
    eeipclient.set_udp_receive_callback(processor.process)

    print(f"Registering session with {target_ip}...")
    session_handle = eeipclient.register_session(target_ip)
    print(f"Session handle: {session_handle}")

    print("Opening implicit messaging connection (Forward Open)...")
    eeipclient.forward_open()
    print("Connection established. Waiting for sensor events from PLC...")

    try:
        # Run for 30 seconds, receiving UDP data via callback
        for i in range(30):
            # Optionally print the latest input data
            print(f"Input bytes: {list(eeipclient.t_o_iodata[:8])}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        print("Closing connection and unregistering session...")
        eeipclient.forward_close()
        eeipclient.unregister_session()
        print("Done.")

if __name__ == "__main__":
    main()
