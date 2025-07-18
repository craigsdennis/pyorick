import asyncio
from bluez_peripheral.gatt.service import Service, ServiceCollection
from bluez_peripheral.gatt.characteristic import characteristic, CharacteristicFlags as CharFlags
from bluez_peripheral.advert import Advertisement
from bluez_peripheral.util import get_message_bus

SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"

class MyCommandService(Service):
    def __init__(self):
        super().__init__(SERVICE_UUID, True)

    @characteristic("1234", CharFlags.WRITE)
    def command(self, value, options):
        # This handler is invoked on writes
        cmd = bytes(value).decode("utf-8")
        print("Received:", cmd)
        # TODO: trigger GPIO/servo here

async def main():
    bus = await get_message_bus()

    svc = MyCommandService()
    await svc.register(bus)

    ad = Advertisement(bus, 0, "peripheral")
    ad.add_service_uuid(SERVICE_UUID)
    ad.include_tx_power = True
    ad.local_name = "uHandPi"
    await ad.register(bus)

    print("Advertising BLE service", SERVICE_UUID)
    await asyncio.get_event_loop().create_future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
