from pyfingerprint.pyfingerprint import PyFingerprint
import serial

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
                self.f._serial.close()
                print("Connection closed")
            except Exception as e:
                print(f"Failed to close connection: {str(e)}")

    def get_sensor_info(self):
        self.connect()
        try:
            info = {
                'Storage capacity': self.f.getStorageCapacity(),
                'Security level': self.f.getSecurityLevel(),
                'Template Count': self.f.getTemplateCount()
                
            }
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

# Example usage
sensor = FingerprintSensor()

# Get sensor info
# info = sensor.get_sensor_info()
# print(info)

# Enroll a finger
# sensor.enroll_finger(positionNumber=1)

# Search for a finger
sensor.search_finger()

# Delete a finger
# sensor.delete_finger(positionNumber=1)

# Get enrolled finger count
# sensor.get_enrolled_finger_count()
