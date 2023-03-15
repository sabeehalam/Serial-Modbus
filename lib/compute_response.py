import ustruct
import const
import misc
import registers

# Unpack the command to find the variables
def parseParams(data):
    start_register_high, start_register_low, register_count_high, register_count_low, recv_crc_1, recv_crc_2 = ustruct.unpack(">BBBBBB", data[2:8])
    start_register = misc.formDecAddress(start_register_high, start_register_low) # Compute the start register address
    register_count = misc.formDecAddress(register_count_high, register_count_low) # Compute the register count or values
    return start_register, register_count, recv_crc_1, recv_crc_2

# Call to read coils
def readCoils(slave_address, function_code, start_register, register_count):
    response = ustruct.pack(">BBB", slave_address, function_code, register_count) #Coil count is either 1 or 2 for our case
    coil_values = 0b00
    for bit_index in range(register_count):
        if misc.isSet(registers.coil_single, bit_index):
            coil_values += 2 ** bit_index
    response += ustruct.pack(">B", coil_values)        
    # Send Modbus RTU response
    return response

# Call to read discrete inputs
def readDiscreteInputs(slave_address, function_code, start_register, register_count):
    response = ustruct.pack(">BBB", slave_address, function_code, register_count) #Coil count is either 1 or 2 for our case
    coil_values = 0b00
    for bit_index in range(register_count):
        if misc.isSet(registers.coil_single, bit_index):
            coil_values += 2 ** bit_index
    response += ustruct.pack(">B", coil_values)        
    # Send Modbus RTU response
    return response

# Call to read holding registers
def readHoldingRegisters(slave_address, function_code, start_register, register_count):
    response = ustruct.pack(">BBB", slave_address, function_code, (register_count * 2))
    for i in range(register_count):
        response += (ustruct.pack(">H", registers.holding_registers[(start_register + i)]))      
    return response

# Call to read holding registers
def readInputRegisters(slave_address, function_code, start_register, register_count):
    response = ustruct.pack(">BBB", slave_address, function_code, (register_count * 2))
    for i in range(register_count):
        response += (ustruct.pack(">H", registers.holding_registers[(start_register + i)]))      
    return response

# Call to write coils
def writeCoil(start_register, values):
    mask_1 = 0b00000001 << start_register
    # Extract coil value
    if values != 0:
        registers.coil_single |= mask_1
    else:
        mask_1 = ~mask_1
        registers.coil_single &= mask_1
    return response
    
# Call to write holding registers
def writeHoldingRegisters(slave_address, function_code, start_register, values):
    # Extract register value
    registers.holding_registers[start_register] = int.from_bytes(ustruct.pack(">H", values), 'big')
    response = ustruct.pack(">BBBB", slave_address, function_code, start_register, values)
    return response

# Function to handle Modbus requests
def handleRequest(data):
    global coil_single
    global discrete_input_single
    
    # Unpack slave address and function code from command
    slave_address, function_code = ustruct.unpack(">BB", data[0:2])
    start_register, register_count, recv_crc_1, recv_crc_2 = parseParams(data)
    
#     print("Slave Address: ", slave_address)
#     print("function_code: ", function_code)
#     print("start_register_high: ", start_coil)
#     print("start_register_low: ", start_register_low)
#     print("value or count high: ", coil_count)
#     print("value or count low: ", register_count_low)
#     print("recv_crc_1: ", recv_crc_1)
#     print("recv_crc_2: ", recv_crc_2)
      
    # Handle read coil request
    if function_code == const.READ_COILS:
        response = readCoils(slave_address, function_code, start_register, register_count)   
        # Send Modbus RTU response
        return response
    
    # Handle read discrete inputs request
    elif function_code == const.READ_DISCRETE_INPUTS:
        response = readCoils(slave_address, function_code, start_register, register_count)  
        # Send Modbus RTU response
        return response

    # Handle read holding register request
    elif function_code == const.READ_HOLDING_REGISTERS: 
        response = readHoldingRegisters(slave_address, function_code, start_register, register_count)
        # Send Modbus RTU response
        return response
    
    # Handle read holding register request
    elif function_code == const.READ_INPUT_REGISTERS:
        response = readInputRegisters(slave_address, function_code, start_register, register_count)
        # Send Modbus RTU response
        return response

    # Handle write single coil request
    elif function_code == const.WRITE_SINGLE_COIL:
        writeCoil(start_register, register_count)
        # Send Modbus RTU response
        return data

    # Handle write single register request
    elif function_code == const.WRITE_HOLDING_REGISTER:
        writeHoldingRegisters(start_register, register_count)
        # Send Modbus RTU response
        return data
    
    # Unsupported function code
    else:
        return None
