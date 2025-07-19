import asyncio
import json
from bluez_peripheral.gatt.service import Service
from bluez_peripheral.gatt.characteristic import characteristic, CharacteristicFlags as CharFlags
from bluez_peripheral.gatt.descriptor import descriptor, DescriptorFlags as DescFlags
from bluez_peripheral.advert import Advertisement
from bluez_peripheral.util import get_message_bus, Adapter
from utils import get_available_action_groups

SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"

class MyCommandService(Service):
    def __init__(self):
        super().__init__(SERVICE_UUID, True)
        self._response_data = b""
        self._notifications_enabled = False

    @characteristic("12345678-1234-5678-1234-56789abcdef1", CharFlags.WRITE)
    def command(self, options):
        # Placeholder for write-only characteristic
        pass

    @command.setter
    def command(self, value, options):
        # This handler is invoked on writes
        cmd = bytes(value).decode("utf-8")
        print("Received:", cmd)
        
        try:
            # Try to parse as JSON command
            command_data = json.loads(cmd)
            response = self.handle_json_command(command_data)
            self._response_data = json.dumps(response).encode("utf-8")
            # Notify subscribers that response data has changed (if notifications enabled)
            if self._notifications_enabled:
                self.response.changed(self._response_data)
        except json.JSONDecodeError:
            # Fallback to plain text command
            print(f"Plain text command: {cmd}")
            # TODO: trigger GPIO/servo here

    @characteristic("12345678-1234-5678-1234-56789abcdef2", CharFlags.READ | CharFlags.NOTIFY)
    def response(self, options):
        # Return the current response data
        return self._response_data
    
    @response.descriptor("2902", DescFlags.READ | DescFlags.WRITE)
    def response_cccd(self, options):
        # Client Characteristic Configuration Descriptor
        return b"\x00\x00"
    
    @response_cccd.setter
    def response_cccd(self, value, options):
        # Handle notification enable/disable
        if value == b'\x01\x00':
            self._notifications_enabled = True
            print("Notifications enabled")
        else:
            self._notifications_enabled = False
            print("Notifications disabled")

    def handle_json_command(self, command_data):
        """Handle JSON commands and return appropriate responses."""
        cmd_type = command_data.get("type")
        
        if cmd_type == "list_available_action_groups":
            available_groups = get_available_action_groups()
            return {
                "type": "action_groups_list",
                "action_groups": available_groups,
                "success": True
            }
        else:
            return {
                "type": "error",
                "message": f"Unknown command type: {cmd_type}",
                "success": False
            }

async def main():
    bus = await get_message_bus()

    svc = MyCommandService()
    await svc.register(bus)

    # Get adapter
    adapter = await Adapter.get_first(bus)

    # Create advertisement with required timeout parameter
    ad = Advertisement("Yorick", [SERVICE_UUID], 0x0340, 0)  # 0 = no timeout
    await ad.register(bus, adapter)

    print("Advertising BLE service", SERVICE_UUID)
    await asyncio.get_event_loop().create_future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
