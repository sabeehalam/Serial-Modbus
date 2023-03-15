import compute_response
import const
import crc
import misc
import registers
import validate_command
import coil_output
from machine import Pin, UART

def main():
    try:
        #Initialize output coils
        coil_1 = Pin(Pin.PB_08, Pin.OUT, Pin.PULL_DOWN)
        coil_2 = Pin(Pin.PB_07, Pin.OUT, Pin.PULL_DOWN)
    
        # Initialize UART
        uart = UART(1, baudrate = const.UART_BAUD_RATE)
        uart.init(baudrate = const.UART_BAUD_RATE, bits = const.UART_DATA_BITS,
            stop = const.UART_STOP_BITS, parity = const.UART_PARITY)
    
        while True:
            # Wait for Modbus request
            response_data = 0
            # Check if there's any data available for reading on UART
            # If available read it
            if uart.any():
                data = uart.read(40)
                # If anything was read from UART, validate and parse it from validateResponse() and send it to handleRequest()
                if data is not None:
                    # Send the received command for validation checks. If no error is found, return None else return the exception response
                    response_error = validate_command.validateResponse(data)
                    if response_error is None:
                        # Compute the response for the command from master
                        response_data = compute_response.handleRequest(data) # Initial part of response
                        crc = crc.reverseCRC(crc.crc16(response_data)) # Compute the CRC for response and reverse it 
                        response = bytearray(response_data) # Convert response to a bytearray
                        response.extend(crc) # Append the CRC 
#                         print("Response = ", response)
                        uart.write(response) # Write response to the UART
                        # Change coil state on register update
                        if(data[1] == WRITE_SINGLE_COIL):
                            coil_outputcoilPinOutChange(coil_1, coil_2, coil_single)
                                        
                    else:
                        crc_rev = crc.crc16(response_error)
                        crc = crc.reverseCRC(crc_rev)
                        print("crc: ", crc)
                        response_error_bytes = bytearray(response_error)
                        response_error_bytes.extend(crc)
                        print("Response Error = ", response_error_bytes)
                        uart.write(response_error_bytes)
                        response = None
                    
                    gc.collect()
                
    except KeyboardInterrupt as e:
        print("No more modbus")
    
# Run the main function when the script is executed
if __name__ == "__main__":
    main()
