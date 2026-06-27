import time
import threading
import psutil
from .config import Config
from .logger import logger
from .listener import TelegramListener

class LaptopAssistant:
    def __init__(self):
        Config.validate()
        self.listener = TelegramListener()
        self.listener_thread = None
        self.stop_event = threading.Event()

    def is_charging(self):
        battery = psutil.sensors_battery()
        if battery is None:
            # Desktop or error, assume plugged in for functionality
            return True
        return battery.power_plugged

    def run(self):
        logger.info("Laptop Assistant Service Started.")
        
        try:
            while not self.stop_event.is_set():
                charging = self.is_charging()
                
                if charging:
                    if not self.listener.is_running:
                        logger.info("Laptop is charging. Activating listener.")
                        self.listener_thread = threading.Thread(target=self.listener.start, daemon=True)
                        self.listener_thread.start()
                    interval = Config.POWER_CHECK_INTERVAL
                else:
                    if self.listener.is_running:
                        logger.info("Laptop unplugged. Deactivating listener to save battery.")
                        self.listener.stop()
                    interval = Config.IDLE_POWER_CHECK_INTERVAL
                
                # Wait for next check or stop signal
                self.stop_event.wait(timeout=interval)
                
        except KeyboardInterrupt:
            logger.info("Shutdown signal received.")
        finally:
            self.listener.stop()
            logger.info("Laptop Assistant Service Stopped.")

if __name__ == "__main__":
    assistant = LaptopAssistant()
    assistant.run()
