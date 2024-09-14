import serial
import time

# Function to calculate checksum
def check_sum(*args):
    checksum = sum(args)
    return checksum & 0xFFFF  # Return as 16-bit value

def VfyPwd(r307_address, vfy_password):
    # Validate that vfy_password is 4 bytes
    if len(vfy_password) != 4:
        raise ValueError("vfy_password must be exactly 4 bytes long")

    # Initialize the command data with specific bytes
    tx_cmd_data = bytearray([0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x07, 0x13])
    check_sum_data = bytearray([0x00, 0x1B])
    
    # Compute checksum based on tx_cmd_data and password
    checksum_value = check_sum(*tx_cmd_data, *vfy_password)
    
    check_sum_data[0] = (checksum_value >> 8) & 0xFF  # Higher byte of checksum
    check_sum_data[1] = checksum_value & 0xFF         # Lower byte of checksum

    # Update tx_cmd_data with address and password
    for i in range(4):
        tx_cmd_data[i + 2] = r307_address[i]            # Add the module address
        
        tx_cmd_data[i + 10] = vfy_password[i]           # Add the password
        if i < 2:
            tx_cmd_data[i + 14] = check_sum_data[i]     # Add the checksum

    instruction_code = tx_cmd_data[9]  # Get instruction code (0x13 in this case)

    # Initialize UART communication (example using pyserial)
    ser = serial.Serial('COM6', baudrate=9600, timeout=1)  # Adjust port and settings

    # Send the packet over UART
    txBytes = ser.write(tx_cmd_data)

    print(f"Wrote {txBytes} bytes")

    # Wait for response
    time.sleep(0.5)

    # Process the response
    confirmation_code = r307_response(ser, instruction_code)

    return confirmation_code

def r307_response(ser, instruction_code):
    # This function should read the UART response and process the confirmation code
    # Example: read a fixed number of bytes (modify based on your response structure)
    response = ser.read(12)  # Read the response (adjust the number of bytes as needed)
    print(f"Received response: {response}")

    # Assuming the confirmation code is in the 10th byte of the response (modify as per spec)
    confirmation_code = response[9]
    
    return confirmation_code

# Example usage:
r307_address = bytearray([0xFF, 0xFF, 0xFF, 0xFF])  # Modify as per your device's address
vfy_password = bytearray([0x00, 0x00, 0x00, 0x00])  # Modify with the correct password (must be 4 bytes)

confirmation_code = VfyPwd(r307_address, vfy_password)
print(f"Confirmation code: {confirmation_code}")
