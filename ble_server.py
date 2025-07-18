import asyncio
from bluez_peripheral import (Service, Characteristic, Peripheral)

SERVICE_UUID = '12345678-1234-5678-1234-56789abcdef0'
CHAR_UUID    = '12345678-1234-5678-1234-56789abcdef1'

class CommandChar(Characteristic):
    def __init__(self):
        super().__init__(CHAR_UUID, ['write'], max_len=20)

    def on_write_request(self, value, options):
        cmd = value.decode()
        print(f"Command from WebBluetooth: {cmd}")
        # 🔧 Trigger your GPIO/servo here

async def main():
    svc = Service(SERVICE_UUID)
    svc.add_characteristic(CommandChar())

    periph = Peripheral("uHandPi", [svc])
    await periph.publish()  # starts advertising + GATT server
    print("Advertising uHandPi...")
    await asyncio.Event().wait()

asyncio.run(main())
