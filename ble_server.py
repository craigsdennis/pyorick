import asyncio
import json
import threading
from bluez_peripheral.gatt.service import Service
from bluez_peripheral.gatt.characteristic import characteristic, CharacteristicFlags as CharFlags
from bluez_peripheral.gatt.descriptor import descriptor, DescriptorFlags as DescFlags
from bluez_peripheral.advert import Advertisement
from bluez_peripheral.util import get_message_bus, Adapter
from bluez_peripheral.agent import NoIoAgent
from utils import get_available_action_groups, create_action_group

# Installed in the main packages on the uHandPi it's in common_sdk folder
try:
    from common.action_group_controller import ActionGroupController
    from common.ros_robot_controller_sdk import Board
    ACTION_GROUPS_AVAILABLE = True
except ImportError:
    print("Warning: Action group controller not available (not on Pi)")
    ACTION_GROUPS_AVAILABLE = False

SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"

class MyCommandService(Service):
    def __init__(self):
        super().__init__(SERVICE_UUID, True)
        self._response_data = b""
        
        # Initialize action group controller if available
        if ACTION_GROUPS_AVAILABLE:
            try:
                self.board = Board()
                self.agc = ActionGroupController(self.board, action_path="/home/pi/pyorick")
                print("Action group controller initialized")
            except Exception as e:
                print(f"Failed to initialize action group controller: {e}")
                self.agc = None
        else:
            self.agc = None

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
            # Notify subscribers that response data has changed
            self.response.changed(self._response_data)
        except json.JSONDecodeError:
            # Fallback to plain text command
            print(f"Plain text command: {cmd}")
            # TODO: trigger GPIO/servo here

    @characteristic("12345678-1234-5678-1234-56789abcdef2", CharFlags.READ | CharFlags.NOTIFY)
    def response(self, options):
        # Return the current response data
        return self._response_data
    
    def run_action_group(self, action_name):
        """Run an action group similar to fiddle.py"""
        if not self.agc:
            print(f"Cannot run action group '{action_name}': Action group controller not available")
            return False
            
        print(f"Running action group {action_name}")
        try:
            threading.Thread(target=self.agc.runAction, args=(action_name,)).start()
            return True
        except Exception as e:
            print(f"Error running action group '{action_name}': {e}")
            return False

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
        elif cmd_type == "run_action_group":
            action_name = command_data.get("name")
            if not action_name:
                return {
                    "type": "error",
                    "message": "Missing 'name' parameter for run_action_group command",
                    "success": False
                }
            
            # Check if action group exists
            available_groups = get_available_action_groups()
            if action_name not in available_groups:
                return {
                    "type": "error", 
                    "message": f"Action group '{action_name}' not found. Available: {', '.join(available_groups)}",
                    "success": False
                }
            
            # Execute the action group
            execution_success = self.run_action_group(action_name)
            return {
                "type": "action_group_result",
                "action_name": action_name,
                "success": execution_success,
                "message": f"Action group '{action_name}' {'started successfully' if execution_success else 'failed to start'}"
            }
        elif cmd_type == "save_action_group":
            action_name = command_data.get("name")
            action_group = command_data.get("action_group")
            
            if not action_name:
                return {
                    "type": "error",
                    "message": "Missing 'name' parameter for save_action_group command",
                    "success": False
                }
            
            if not action_group:
                return {
                    "type": "error", 
                    "message": "Missing 'action_group' parameter for save_action_group command",
                    "success": False
                }
            
            # Create the action group database
            result = create_action_group(action_name, action_group)
            
            return {
                "type": "action_group_saved",
                "action_name": action_name,
                "success": result["success"],
                "message": result["message"],
                "steps_count": len(action_group) if result["success"] else 0
            }
        else:
            return {
                "type": "error",
                "message": f"Unknown command type: {cmd_type}",
                "success": False
            }

async def main():
    bus = await get_message_bus()

    # Register agent for pairing support
    agent = NoIoAgent()
    await agent.register(bus)

    # Create and register service
    svc = MyCommandService()
    await svc.register(bus)

    # Get adapter
    adapter = await Adapter.get_first(bus)

    # Create advertisement with both custom and standard service UUIDs
    # Include generic device information service (full UUID format for consistency)
    device_info_service_uuid = "0000180A-0000-1000-8000-00805f9b34fb"
    advertised_services = [SERVICE_UUID, device_info_service_uuid]  
    ad = Advertisement("Yorick", advertised_services, 0x0340, 0)  # 0 = no timeout
    await ad.register(bus, adapter)

    print("=== BLE Server Status ===")
    print(f"Service UUID: {SERVICE_UUID}")
    print(f"Advertised services: {advertised_services}")
    print(f"Device name: Yorick")
    print("Agent registered: ✓")
    print("Service registered: ✓") 
    print("Advertisement started: ✓")
    print("=========================")
    print("Waiting for connections...")
    print("Note: Some clients may need to connect first, then discover services")
    
    await asyncio.get_event_loop().create_future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
