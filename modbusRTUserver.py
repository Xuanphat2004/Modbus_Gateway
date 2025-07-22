import asyncio
import logging
import json
import redis.asyncio as aioredis 
from pymodbus.client.tcp import AsyncModbusTcpClient
from pymodbus.client.serial import AsyncModbusSerialClient
# from database_service import add_log

logging.basicConfig()
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

#==================================================================================
# --- 0x01: Coil Functions ---
# async def read_coils(client, address, count, unit):
#     read = await client.read_coils(address, count, unit)
#     if read.isError():
#         print(f"[ERROR] Read Coils: {read}")
#         add_log("Modbus", f"Read Coils Error: {read}")
#     else:
#         print(f"[OK] Coils at {address}: {read.bits[:count]}")
#         add_log("Modbus", f"Read Coils Success: {read.bits[:count]}")

# async def write_single_coil(client, address, value, unit):
#     write = await client.write_coil(address, value, unit)
#     if write.isError():
#         print(f"[ERROR] Write Single Coil: {write}")
#         add_log("Modbus", f"Write Single Coil Error: {write}")
#     else:
#         print(f"[OK] Wrote coil {address} = {value}")
#         add_log("Modbus", f"Wrote Single Coil Success: {address} = {value}")

# async def write_multiple_coils(client, address, values, unit):
#     write = await client.write_coils(address, values, unit=unit)
#     if write.isError():
#         print(f"[ERROR] Write Multiple Coils: {write}")
#         add_log("Modbus", f"Write Multiple Coils Error: {write}")
#     else:
#         print(f"[OK] Wrote coils at {address}: {values}")
#         add_log("Modbus", f"Wrote Multiple Coils Success: {address} = {values}")

# #=================================================================================
# # --- 0x02: Discrete Inputs ---
# async def read_discrete_inputs(client, address, count, unit):
#     read = await client.read_discrete_inputs(address, count, unit)
#     print(f"read value: {read}")
#     if read.isError():
#         print(f"[ERROR] Discrete Inputs: {read}")
#         add_log("Modbus", f"Read Discrete Inputs Error: {read}")
#     else:
#         print(f"[OK] Discrete Inputs at {address}: {read.bits[:count]}")
#         add_log("Modbus", f"Read Discrete Inputs Success: {read.bits[:count]}")

# #=================================================================================
# # --- 0x03: Holding Registers ---
# async def read_holding_registers(client, address, count, unit):
#     read = await client.read_holding_registers(address, count, unit)
#     print(f"read value: {read}")
#     if read.isError():
#         print(f"[ERROR] Read Holding Registers: {read}")
#         add_log("Modbus", f"Read Holding Registers Error: {read}")

#     else:
#         print(f"[OK] Holding Registers at {address}: {read.registers[:count]}")
#         add_log("Modbus", f"Read Holding Registers Success: {read.registers[:count]}")

# async def write_single_register(client, address, value, unit):
#     write = await client.write_register(address, value, unit)
#     if write.isError():
#         print(f"[ERROR] Write Single Register: {write}")
#         add_log("Modbus", f"Write Single Register Error: {write}")
#     else:
#         print(f"[OK] Wrote register {address} = {value}")
#         add_log("Modbus", f"Wrote Single Register Success: {address} = {value}")

# async def write_multiple_registers(client, address, values, unit):
#     write = await client.write_registers(address, values, unit)
#     if write.isError():
#         print(f"[ERROR] Write Multiple Registers: {write}")
#         add_log("Modbus", f"Write Multiple Registers Error: {write}")
#     else:
#         print(f"[OK] Wrote registers at {address}: {values}")
#         add_log("Modbus", f"Wrote Multiple Registers Success: {address} = {values}")

# #=================================================================================
# # --- 0x04: Input Registers ---
# async def read_input_registers(client, address, count, unit):
#     read = await client.read_input_registers(address, count, unit)
#     if read.isError():
#         print(f"[ERROR] Read Input Registers: {read}")
#         add_log("Modbus", f"Read Input Registers Error: {read}")
#     else:
#         print(f"[OK] Input Registers at {address}: {read.registers[:count]}")
#         add_log("Modbus", f"Read Input Registers Success: {read.registers[:count]}")


# #==================================================================================
# # --- Coil Functions ---
# async def read_coils(client, address, count, unit):
#     read = await client.read_coils(address, count, unit)
#     if read.isError():
#         msg = f"[ERROR] Read Coils: {read}"
#         print(msg)
#         add_log("Modbus", msg)
#         return {"error": str(read)}
#     else:
#         msg = f"[OK] Coils at {address}: {read.bits[:count]}"
#         print(msg)
#         add_log("Modbus", msg)
#         return {"bits": read.bits[:count]}

# async def write_single_coil(client, address, value, unit):
#     write = await client.write_coil(address, value, unit)
#     if write.isError():
#         msg = f"[ERROR] Write Single Coil: {write}"
#         print(msg)
#         add_log("Modbus", msg)
#         return {"error": str(write)}
#     else:
#         msg = f"[OK] Wrote coil {address} = {value}"
#         print(msg)
#         add_log("Modbus", msg)
#         return {"ok": True}

# async def write_multiple_coils(client, address, values, unit):
#     write = await client.write_coils(address, values, unit=unit)
#     if write.isError():
#         msg = f"[ERROR] Write Multiple Coils: {write}"
#         print(msg)
#         add_log("Modbus", msg)
#         return {"error": str(write)}
#     else:
#         msg = f"[OK] Wrote coils at {address}: {values}"
#         print(msg)
#         add_log("Modbus", msg)
#         return {"ok": True}

# #=================================================================================
# # --- Discrete Inputs ---
# async def read_discrete_inputs(client, address, count, unit):
#     read = await client.read_discrete_inputs(address, count, unit)
#     if read.isError():
#         msg = f"[ERROR] Discrete Inputs: {read}"
#         print(msg)
#         add_log("Modbus", msg)
#         return {"error": str(read)}
#     else:
#         msg = f"[OK] Discrete Inputs at {address}: {read.bits[:count]}"
#         print(msg)
#         add_log("Modbus", msg)
#         return {"bits": read.bits[:count]}

# #=================================================================================
# # --- Holding Registers ---
# async def read_holding_registers(client, address, count, unit):
#     read = await client.read_holding_registers(address, count, unit)
#     if read.isError():
#         msg = f"[ERROR] Read Holding Registers: {read}"
#         print(msg)
#         add_log("Modbus", msg)
#         return {"error": str(read)}
#     else:
#         msg = f"[OK] Holding Registers at {address}: {read.registers[:count]}"
#         print(msg)
#         add_log("Modbus", msg)
#         return {"registers": read.registers[:count]}

# async def write_single_register(client, address, value, unit):
#     write = await client.write_register(address, value, unit)
#     if write.isError():
#         msg = f"[ERROR] Write Single Register: {write}"
#         print(msg)
#         add_log("Modbus", msg)
#         return {"error": str(write)}
#     else:
#         msg = f"[OK] Wrote register {address} = {value}"
#         print(msg)
#         add_log("Modbus", msg)
#         return {"ok": True}

# async def write_multiple_registers(client, address, values, unit):
#     write = await client.write_registers(address, values, unit)
#     if write.isError():
#         msg = f"[ERROR] Write Multiple Registers: {write}"
#         print(msg)
#         add_log("Modbus", msg)
#         return {"error": str(write)}
#     else:
#         msg = f"[OK] Wrote registers at {address}: {values}"
#         print(msg)
#         add_log("Modbus", msg)
#         return {"ok": True}

# #=================================================================================
# # --- Input Registers ---
# async def read_input_registers(client, address, count, unit):
#     read = await client.read_input_registers(address, count, unit)
#     if read.isError():
#         msg = f"[ERROR] Read Input Registers: {read}"
#         print(msg)
#         add_log("Modbus", msg)
#         return {"error": str(read)}
#     else:
#         msg = f"[OK] Input Registers at {address}: {read.registers[:count]}"
#         print(msg)
#         add_log("Modbus", msg)
#         return {"registers": read.registers[:count]}

# #=================================================================================
# # --- Redis Handler ---
# async def handle_redis_commands(client, redis_client):
#     pubsub = redis_client.pubsub()
#     await pubsub.subscribe("modbus_request")
#     print("Listening for Redis messages on 'modbus_request'...")

#     async for message in pubsub.listen():
#         if message['type'] != 'message':
#             continue

#         try:
#             payload = json.loads(message['data'])
#             print(f"[Redis] Received command: {payload}")

#             fn = payload.get("function")
#             address = payload.get("address", 0)
#             count = payload.get("count", 1)
#             unit = payload.get("unit", 1)
#             values = payload.get("values", [])

#             result = None
#             if fn == "read_coils":
#                 result = await read_coils(client, address, count, unit)
#             elif fn == "read_discrete_inputs":
#                 result = await read_discrete_inputs(client, address, count, unit)
#             elif fn == "read_holding_registers":
#                 result = await read_holding_registers(client, address, count, unit)
#             elif fn == "read_input_registers":
#                 result = await read_input_registers(client, address, count, unit)
#             elif fn == "write_single_coil":
#                 result = await write_single_coil(client, address, values[0], unit)
#             elif fn == "write_multiple_coils":
#                 result = await write_multiple_coils(client, address, values, unit)
#             elif fn == "write_single_register":
#                 result = await write_single_register(client, address, values[0], unit)
#             elif fn == "write_multiple_registers":
#                 result = await write_multiple_registers(client, address, values, unit)
#             else:
#                 result = {"error": f"Unknown function: {fn}"}

#             await redis_client.publish("modbus_response", json.dumps({
#                 "status": "ok",
#                 "response": result,
#                 "function": fn,
#                 "address": address
#             }))
#         except Exception as e:
#             print(f"[Redis] Exception: {e}")
#             await redis_client.publish("modbus_response", json.dumps({
#                 "status": "error",
#                 "message": str(e)
#             }))

# --- Main Function ---
async def main():
    # redis_client = aioredis.Redis(host='localhost', port=6379, decode_responses=True)

    while True:
        try:
            mode = "tcp"
            if mode == "tcp":
                client = AsyncModbusTcpClient("127.0.0.1", port=502)
            else:
                client = AsyncModbusSerialClient(
                    port="/dev/ttyUSB0", 
                    baudrate=9600,
                    stopbits=1,
                    bytesize=8,
                    parity='N'
                )

            await client.connect()

            if client.connected:
                print("Connect to Modbus server !!!")
                # add_log("Modbus", "Failed to connect to Modbus client !!!")
                await asyncio.sleep(5)
                continue

            print("Error connected to Modbus device.")

            # Lắng nghe và xử lý Redis command
            await asyncio.gather(
                # handle_redis_commands(client, redis_client)
            )

        except Exception as e:
            print(f"[MAIN] Exception: {e}")
            # add_log("Modbus", f"Exception: {str(e)}")
            await asyncio.sleep(5)

#=================================================================================
if __name__ == "__main__":
    asyncio.run(main())
