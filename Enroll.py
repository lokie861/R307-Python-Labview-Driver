from pyfingerprint.pyfingerprint import PyFingerprint
import time
## Initialize sensor on COM6 at baud rate 57600
try:
    f = PyFingerprint('COM6', 57600, 0xFFFFFFFF, 0x00000000)

    if f.verifyPassword() == False:
        raise ValueError('Invalid fingerprint sensor password!')
except Exception as e:
    print('The fingerprint sensor could not be initialized!')
    print('Exception message: ' + str(e))
    exit(1)

## Get the sensor's current capacity
print('Currently used templates: ' + str(f.getTemplateCount()) + '/' + str(f.getStorageCapacity()))

## Enroll the fingerprint
try:
    print('Waiting for finger...')

    ## Wait until a finger is read on the sensor
    while f.readImage() == False:
        pass

    ## Convert the read image to a characteristic
    f.convertImage(0x01)

    ## Check if the fingerprint is already enrolled
    result = f.searchTemplate()
    positionNumber = result[0]

    if positionNumber >= 0:
        print('Fingerprint already exists at position #' + str(positionNumber))
        exit(0)

    print('Remove finger...')
    time.sleep(2)

    print('Waiting for the same finger again...')

    ## Wait for the same finger to be read again
    while f.readImage() == False:
        pass

    ## Convert the second image to a characteristic
    f.convertImage(0x02)

    ## Create a template from both fingerprint characteristics
    if f.compareCharacteristics() == 0:
        raise Exception('Fingers do not match!')

    ## Create a new fingerprint template
    f.createTemplate()

    ## Store the template at the first available position
    positionNumber = f.storeTemplate()
    print('Fingerprint enrolled successfully at position #' + str(positionNumber))

except Exception as e:
    print('Operation failed!')
    print('Exception message: ' + str(e))
    exit(1)
