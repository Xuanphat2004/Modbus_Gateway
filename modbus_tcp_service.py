import asyncio
import redis.asyncio as redis
import json
# from pymodbus.server.async_io import StartTcpServer
from pymodbus.server.startstop import StartAsyncTcpServer
from pymodbus.datastore import ModbusServerContext, ModbusSlaveContext, ModbusSequentialDataBlock
# from pymodbus.pdu import ExceptionResponse
from pymodbus.pdu.register_message import (
    ReadHoldingRegistersRequest, ReadHoldingRegistersResponse,
    ReadInputRegistersRequest, ReadInputRegistersResponse,
    WriteSingleRegisterRequest, WriteSingleRegisterResponse,
    WriteMultipleRegistersRequest, WriteMultipleRegistersResponse,
    ExceptionResponse
)
from database_service import get_mapping, add_log

#====================================================================================================
# Receive packet from TCP client, get mapping from database, and send request to RTU service.
async def handle_modbus_request(function_code, address, count=None, values=None, redis_client=None):
    add_log("Modbus TCP server", f"Receive packet from client.")
    print(f"Packet from TCP client have function_code: {function_code}, address: {address}, count: {count}, values: {values}")
    tcp_address = address

    mapping = get_mapping(tcp_address)
    try:
        rtu_id, rtu_address = mapping
    except:
        add_log("Modbus TCP server", f"No mapping for TCP address: {tcp_address}")
        return {"error": "Illegal Data Address"}
    
    print(f"After mapping: ID device is {rtu_id} and start address is {rtu_address}")
    request_id = str(id(object()))  # transaction ID for the request
    request_data = {
        "request_id"   : request_id,
        "function_code": function_code,
        "rtu_id"       : rtu_id,
        "rtu_address"  : rtu_address,
        "count"        : count if count is not None else 1,
        "values"       : values
    }

    # Send request through Redis for Modbus RTU service
    await redis_client.publish("modbus_requests", json.dumps(request_data))
    add_log("Modbus TCP server", f"Send request for Modbus RTU server {tcp_address}: {request_data}")
    print(f"Send request for Modbus RTU service {tcp_address}: {request_data}")

    # Wait for response from Redis
    sub = redis_client.pubsub()
    await sub.subscribe("modbus_responses")
    async for message in sub.listen():
        # print("..........")
        if message:
            if message["type"] == "message": # mesage return from rtu_service 
                add_log("Modbus TCP server", f"Receive response for request {request_id} from Redis.")
                response = json.loads(message["data"]) # convert JSON type to dict type.
                print (f"Received response: {response}")
                if response["request_id"] == request_id:
                    result = response["result"]
                    try:
                        if "error" not in result:
                            add_log("Modbus TCP server", f"Response for TCP {tcp_address}: {result}")
                            return result
                    except ValueError:
                        add_log("Modbus TCP server", f"Invalid response format for TCP {tcp_address}: {result}")
                        return {"error": "Invalid response format"}
            else:
                add_log("Modbus TCP server", f"Received unexpected message type: {message['type']}")
                return {"error": "Unexpected message type"}
        else:
            add_log("Modbus TCP server", f"No receive response from redis {request_id} !!!")
            return {"error": "No response from Modbus RTU service"}       

async def run_tcp_server():
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
    """Custom PDU classes for Modbus TCP requests"""
    """Custom classes for Modbus TCP requests to handle specific function codes"""
    """Custom class for function code 3: Read Holding Registers"""
    
    class CustomReadHoldingRegistersRequest(ReadHoldingRegistersRequest):
        async def update_datastore(self, context):
            result = await handle_modbus_request(
                function_code = self.function_code,  
                address       = self.address,        
                count         = self.count,         
                values        = None,                
                redis_client  = redis_client
            )
            # if "error" in result:
            #     return ExceptionResponse(function_code=self.function_code, exception_code=404)
            return ReadHoldingRegistersResponse(registers=result)
    
    class CustomReadInputRegistersRequest(ReadInputRegistersRequest):
        """Custom class for function code 4: Read Input Registers"""
        async def update_datastore(self, context):
            result = await handle_modbus_request(
                function_code = self.function_code,  
                address       = self.address,
                count         = self.count,
                values        = None,
                redis_client  = redis_client
            )
            # if "error" in result:
            #     return ExceptionResponse(function_code=self.function_code, exception_code=404)
            return ReadInputRegistersResponse(registers=result)

    class CustomWriteSingleRegisterRequest(WriteSingleRegisterRequest):
        """Custom class for function code 6: Write Single Register"""
        async def update_datastore(self, context):
            result = await handle_modbus_request(
                function_code=self.function_code,  # 6
                address=self.address,
                count=None,
                values=self.registers[0],
                redis_client=redis_client
            )
            # if "error" in result:
            #     return ExceptionResponse(function_code=self.function_code, exception_code=404)
            return WriteSingleRegisterResponse(address=self.address, registers=[1] if result else [0])

    class CustomWriteMultipleRegistersRequest(WriteMultipleRegistersRequest):
        """Class tùy chỉnh cho function code 16: Write Multiple Registers"""
        async def update_datastore(self, context):
            result = await handle_modbus_request(
                function_code=self.function_code,  # 16
                address=self.address,
                count=self.count,
                values=self.registers,
                redis_client=redis_client
            )
            # if "error" in result:
            #     return ExceptionResponse(function_code=self.function_code, exception_code=404)
            return WriteMultipleRegistersResponse(address=self.address, count=self.count if result else 0)

    custom_pdu = [
        CustomReadHoldingRegistersRequest,    # 3
        CustomReadInputRegistersRequest,      # 4
        CustomWriteSingleRegisterRequest,     # 6
        CustomWriteMultipleRegistersRequest   # 16
    ]

    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [0]*10000),
        co=ModbusSequentialDataBlock(0, [0]*10000),
        hr=ModbusSequentialDataBlock(0, [0]*10000),
        ir=ModbusSequentialDataBlock(0, [0]*10000)
    )

    context = ModbusServerContext(slaves=store, single=True)
    
    await StartAsyncTcpServer(
        context=context,
        address=("localhost", 502),
        custom_pdu=custom_pdu
    )

if __name__ == "__main__":
    asyncio.run(run_tcp_server())