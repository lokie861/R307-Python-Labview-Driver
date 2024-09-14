from pyfingerprint.pyfingerprint import PyFingerprint
import serial.tools.list_ports

# Get COM Port of the TTL Converter
def get_com_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        # Check for a specific manufacturer or description if known
        if "USB" in port.description or "TTL" in port.description:
            print(f"Found TTL converter on {port.device}")
            return port.device
    print("No TTL converter found.")
    return None
# Initialize Fingerprint Sensor
def initialize_sensor():
    try:
        sensor = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)
        if verify_password(sensor):
            return sensor
        else:
            print("Could not initialize sensor")
            return None
    except Exception as e:
        print(f"Failed to initialize fingerprint sensor: {e}")
        return None

# Verify Password
def verify_password(fingerprint_sensor):
    try:
        if fingerprint_sensor.verifyPassword():
            return True
        else:
            return False
    except Exception as e:
        print(f'Password verification failed: {e}')
        return False

# Enroll Fingerprint
def enroll_fingerprint(fingerprint_sensor):
    try:
        print("Waiting for finger...")
        while not fingerprint_sensor.readImage():
            pass

        fingerprint_sensor.convertImage(0x01)

        result = fingerprint_sensor.searchTemplate()
        position_number = result[0]
        
        if position_number >= 0:
            print(f"Fingerprint already exists at position {position_number}")
            return False

        print("Remove finger...")
        while fingerprint_sensor.readImage():
            pass

        print("Place same finger again...")
        while not fingerprint_sensor.readImage():
            pass

        fingerprint_sensor.convertImage(0x02)

        if fingerprint_sensor.compareCharacteristics() == 0:
            raise Exception("Fingers do not match")

        fingerprint_sensor.createTemplate()

        position_number = fingerprint_sensor.storeTemplate()
        print(f"Fingerprint enrolled successfully at position {position_number}")
        return position_number

    except Exception as e:
        print(f"Failed to enroll fingerprint: {e}")
        return False

# Search Fingerprint
def search_fingerprint(fingerprint_sensor):
    try:
        print("Waiting for finger...")
        while not fingerprint_sensor.readImage():
            pass

        fingerprint_sensor.convertImage(0x01)

        result = fingerprint_sensor.searchTemplate()
        position_number = result[0]
        accuracy_score = result[1]

        if position_number == -1:
            print("No match found")
            return None
        else:
            print(f"Found match at position {position_number} with accuracy score {accuracy_score}")
            return position_number

    except Exception as e:
        print(f"Failed to search fingerprint: {e}")
        return None

# Delete Fingerprint
def delete_fingerprint(fingerprint_sensor, position_number):
    try:
        if fingerprint_sensor.deleteTemplate(position_number):
            print(f"Fingerprint at position {position_number} deleted")
            return True
        else:
            print(f"Failed to delete fingerprint at position {position_number}")
            return False

    except Exception as e:
        print(f"Failed to delete fingerprint: {e}")
        return False

# Get Stored Template Count
def get_template_count(fingerprint_sensor):
    try:
        count = fingerprint_sensor.getTemplateCount()
        print(f"Number of stored fingerprints: {count}")
        return count
    except Exception as e:
        print(f"Failed to get template count: {e}")
        return None

# Load a Fingerprint Template
def load_fingerprint_template(fingerprint_sensor, position_number):
    try:
        if fingerprint_sensor.loadTemplate(position_number):
            print(f"Fingerprint template {position_number} loaded")
            return True
        else:
            print(f"Failed to load template {position_number}")
            return False
    except Exception as e:
        print(f"Failed to load fingerprint template: {e}")
        return False

# Download Fingerprint Image
def download_fingerprint_image(fingerprint_sensor, filename):
    try:
        if fingerprint_sensor.downloadImage(filename):
            print(f"Fingerprint image downloaded as {filename}")
            return True
        else:
            print("Failed to download fingerprint image")
            return False
    except Exception as e:
        print(f"Failed to download fingerprint image: {e}")
        return False

# Read System Parameters
def read_system_parameters(fingerprint_sensor):
    try:
        system_params = fingerprint_sensor.readSystemParameters()
        print(f"System Parameters: {system_params}")
        return system_params
    except Exception as e:
        print(f"Failed to read system parameters: {e}")
        return None

# Set Security Level
def set_security_level(fingerprint_sensor, level):
    try:
        if fingerprint_sensor.setSecurityLevel(level):
            print(f"Security level set to {level}")
            return True
        else:
            print("Failed to set security level")
            return False
    except Exception as e:
        print(f"Failed to set security level: {e}")
        return False

# Clear Fingerprint Database
def clear_database(fingerprint_sensor):
    try:
        if fingerprint_sensor.clearDatabase():
            print("Fingerprint database cleared")
            return True
        else:
            print("Failed to clear database")
            return False
    except Exception as e:
        print(f"Failed to clear fingerprint database: {e}")
        return False

# Example of how to use the functions
if __name__ == "__main__":
    sensor = initialize_sensor()
    
    if sensor:
        # You can now call any function here
        print(get_template_count(sensor))
