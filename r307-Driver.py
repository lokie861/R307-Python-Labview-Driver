from pyfingerprint.pyfingerprint import PyFingerprint
import sys
import serial.tools.list_ports

class FingerprintSensor:
    def __init__(self, port='COM6', baud_rate=57600, address=0xFFFFFFFF, password=0x00000000):
        self.port = port
        self.baud_rate = baud_rate
        self.address = address
        self.password = password
        self.f = None

    def connect(self):
        try:
            self.f = PyFingerprint(self.port, self.baud_rate, self.address, self.password)
            if not self.f.verifyPassword():
                raise ValueError('The given fingerprint sensor password is wrong!')
        except Exception as e:
            print(f'Failed to initialize the fingerprint sensor: {str(e)}')
            raise e

    def close(self):
        if self.f is not None:
            try:
                self.f = None
                # print("Connection closed")
            except Exception as e:
                print(f"Failed to close connection: {str(e)}")

    def get_sensor_info(self):
        self.connect()
        try:
            info = f"Storage capacity: {self.f.getStorageCapacity()}\nSecurity level: {self.f.getSecurityLevel()}\nTemplate Count: {self.f.getTemplateCount()}"
            return info
        finally:
            self.close()

    def enroll_finger(self, positionNumber):
        self.connect()
        try:
            print('Waiting for finger...')
            while not self.f.readImage():
                pass
            self.f.convertImage(0x01)
            result = self.f.searchTemplate()
            positionNumber = result[0]
            if positionNumber >= 0:
                print(f'Finger already enrolled at position {positionNumber}')
                return
            print('Remove finger...')
            while self.f.readImage():
                pass
            print('Waiting for the same finger again...')
            while not self.f.readImage():
                pass
            self.f.convertImage(0x02)
            if self.f.compareCharacteristics() == 0:
                raise Exception('Fingers do not match')
            self.f.createTemplate()
            positionNumber = self.f.storeTemplate()
            print(f'Finger enrolled successfully at position {positionNumber}')
        finally:
            self.close()

    def delete_finger(self, positionNumber):
        self.connect()
        try:
            if self.f.deleteTemplate(positionNumber):
                print(f'Successfully deleted fingerprint at position {positionNumber}')
        finally:
            self.close()

    def search_finger(self):
        self.connect()
        try:
            print('Waiting for finger...')
            while not self.f.readImage():
                pass
            self.f.convertImage(0x01)
            result = self.f.searchTemplate()
            positionNumber = result[0]
            if positionNumber == -1:
                print('No match found')
            else:
                print(f'Found template at position {positionNumber}')
        finally:
            self.close()

    def get_enrolled_finger_count(self):
        self.connect()
        try:
            count = self.f.getTemplateCount()
            print(f'Number of enrolled fingers: {count}')
            return count
        finally:
            self.close()

def get_com_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        # Check for a specific manufacturer or description if known
        if "USB" in port.description or "TTL" in port.description:
            # print(port.device)
            return port.device
    print("No TTL converter found.")
    return None

if __name__ == "__main__":
        
    PORT = get_com_port()

    if PORT != None:
        if len(sys.argv) > 0:
            sensor = FingerprintSensor(port=PORT)
            
            # Get sensor info
            if sys.argv[1].lower() == "info":
                info = sensor.get_sensor_info()
                print(info)
            elif sys.argv[1].lower() == "enroll":
                # Enroll a finger
                sensor.enroll_finger(positionNumber=1)
            elif sys.argv[1].lower() == "search":
                # Search for a finger
                sensor.search_finger()
            elif sys.argv[1].lower() == "delete":
                # Delete a finger
                sensor.delete_finger(positionNumber= int(sys.argv[2]))
            elif sys.argv[1].lower() == "count":
                # Get enrolled finger count
                sensor.get_enrolled_finger_count()
            elif sys.argv[1].lower() == "port":
                PORT = get_com_port()
                print(PORT)
        else:
            print("Enter the operation as argv")
    else:
        print("Finger Print Sensor not found...")
