import asyncio
import redis.asyncio as redis
import json
# from pymodbus.client.async_serial import AsyncModbusSerialClient
from pymodbus.client.serial import AsyncModbusSerialClient
from pymodbus.client.tcp import AsyncModbusTcpClient
from database_service import add_log
mode = " " 

async def handle_rtu_request(request_data, client_rtu):
    request_id    = request_data["request_id"]
    function_code = request_data["function_code"]
    rtu_id        = request_data["rtu_id"]
    rtu_address   = request_data["rtu_address"]
    count         = request_data["count"]
    values        = request_data["values"]
    
    print(f"Receive packet from TCP server after mapping < function_code: {function_code}, rtu_id: {rtu_id}, rtu_address: {rtu_address} , count: {count}, values: {values} >")
    
    try:
        if function_code in [3, 4]:  
            if function_code == 3:
                result = await client_rtu.read_holding_registers(address=rtu_address, count=count, slave=rtu_id)
            elif function_code == 4:
                result = await client_rtu.read_input_registers(address=rtu_address, count=count, slave=rtu_id)
            else:
                result.isError()
                add_log("Modbus RTU service", f"Error reading RTU ID {rtu_id}: {result}")
                return {"request_id": request_id, "result": {"error": str(result)}}
            
            add_log("Modbus RTU service", f"Read RTU ID {rtu_id}, Address {rtu_address}: {result.registers}")
            print(f"Read RTU ID {rtu_id}, Address {rtu_address}: {result.registers}")
            return {"request_id": request_id, "result": result.registers}
        
        elif function_code in [6, 16]:  
            if function_code == 6:
                result = await client_rtu.write_register(address=rtu_address, value=values, slave=rtu_id)
            elif function_code == 16:
                result = await client_rtu.write_registers(address=rtu_address, values=values, slave=rtu_id)
            else:
                result.isError()
                add_log("Modbus RTU service", f"Error writing RTU ID {rtu_id}: {result}")
                return {"request_id": request_id, "result": {"error": str(result)}}
            
            add_log("Modbus RTU service", f"Wrote to RTU ID {rtu_id}, Address {rtu_address}")
            print(f"Wrote to RTU ID {rtu_id}, Address {rtu_address}")
            return {"request_id": request_id, "result": True}
        
        else:
            add_log("Modbus RTU service", f"Unsupported function code: {function_code}")
            return {"request_id": request_id, "result": {"error": "Unsupported function code"}}
        
    except Exception as e:
        add_log("Modbus RTU service", f"Exception for RTU ID {rtu_id}: {str(e)}")
        return {"request_id": request_id, "result": {"error": str(e)}}

async def run_rtu_service():
    # Connect to Redis server.
    redis_client = redis.Redis(host = 'localhost', port = 6379, decode_responses = True)
    
    # connect to Modbus device through Modbus TCP or Modbus RTU.
    client_tcp = AsyncModbusTcpClient(host = "192.168.3.1", port = 5000)  # Address of Modbus device.
    client_rtu = AsyncModbusSerialClient(port = '/dev/ttyS0', baudrate = 9600, parity = 'N', stopbits = 1, bytesize = 8)
    await client_tcp.connect()
    await client_rtu.connect()
    if client_tcp.connected:   
        add_log("Modbus RTU service", f"Connected to RTU device through Modbus TCP.")
        print(f"Connected to Gateway R40 device through Modbus TCP.")
        mode = "tcp"
    elif client_rtu.connected:
        add_log("Modbus RTU service", f"Connected to RTU device through Modbus RTU.")
        print("Connected to Gateway R40 device through Modbus RTU.")
        mode = "rtu"
    else:
        add_log("Modbus RTU service", f"Error connecting to RTU device !!!")
        print("Error connecting to Gateway R40 device !!!")
        await connect_again()
    

    # Wait for requests from TCP server.
    sub = redis_client.pubsub()
    await sub.subscribe("modbus_requests")
    async for message in sub.listen():
        try:
            if message["type"] == "message":
                request_data = json.loads(message["data"])
                if mode == "tcp":
                    response = await handle_rtu_request(request_data, client_tcp)
                elif mode == "rtu":
                    response = await handle_rtu_request(request_data, client_rtu)
                else:
                    add_log("Modbus RTU service", "Invalid mode, please check the connection to Modbus device !!!")
                    print("Invalid mode, please check the connection to Modbus device !!!")                   
                await redis_client.publish("modbus_responses", json.dumps(response))
                add_log("Modbus RTU service", f"Response sent for request ID {request_data['request_id']}")
        except Exception as e:
            add_log("Modbus RTU service", f"No response from RTU device !!!")

async def connect_again():
        try:
            await run_rtu_service()
        except Exception as e:
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(run_rtu_service())