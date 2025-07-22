from pymodbus.client import AsyncModbusTcpClient
import asyncio

async def test_client():
    client = AsyncModbusTcpClient("localhost", port=502) # Connect with TCP server
    await client.connect()
    if client.connected:

        # Gửi yêu cầu đọc Holding Registers (function code 3)
        response = await client.read_holding_registers(address=40001, count=9)
        print(f"Values: {response.registers}")

        # # Gửi yêu cầu đọc Input Registers (function code 4)
        response = await client.read_input_registers(address=40002, count=5)
        if not response.isError():
            print(f"Values: {response.registers}")
        else:
            print(f"Error: {response}")

        # # Gửi yêu cầu ghi Single Register (function code 6)
        # response = await client.write_register(address=1000, value=123)
        # if not response.isError():
        #     print(f"Write successful: address={response.address}, value={response.registers}")
        # else:
        #     print(f"Error: {response}")

        # # Gửi yêu cầu ghi Multi Registers (function code 16) 
        # response = await client.write_registers(address=1000, values=[12,13,14])
        # if not response.isError():
        #     print(f"Write successful: address={response.address}, count={response.count}")
        # else:
        #     print(f"Error: {response}")
    client.close()

asyncio.run(test_client())
