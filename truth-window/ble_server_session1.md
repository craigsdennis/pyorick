# BLE Server Debugging Session 1

## User Request
User requested help with debugging a Bluetooth Low Energy (BLE) server for Raspberry Pi that had errors with the OpenAI-generated API. The goal was to create a BLE server that could be connected to via Web Bluetooth.

## Initial Issues Found

### 1. Unused Import
- **File**: `ble_server.py:2`
- **Issue**: `ServiceCollection` was imported but never used
- **Fix**: Removed unused import

### 2. Advertisement Constructor API Error
- **File**: `ble_server.py:26`
- **Issue**: `Advertisement` constructor was using incorrect parameters
- **Original**: `Advertisement(bus, 0, "peripheral")`
- **Fix**: `Advertisement("Yorick", [SERVICE_UUID], 0x0340, 0)`
- **Explanation**: The Advertisement class requires `localName`, `serviceUUIDs`, `appearance`, and `timeout` parameters

### 3. Characteristic Decorator Usage
- **File**: `ble_server.py:13-17`
- **Issue**: Write-only characteristic was not properly implemented
- **Original**: Single method with `@characteristic("1234", CharFlags.WRITE)`
- **Fix**: Added proper setter pattern:
  ```python
  @characteristic("12345678-1234-5678-1234-56789abcdef1", CharFlags.WRITE)
  def command(self, options):
      pass

  @command.setter
  def command(self, value, options):
      # Handle write operations
  ```

### 4. Missing Adapter Import and Usage
- **File**: `ble_server.py:32`
- **Issue**: Advertisement registration required adapter parameter
- **Fix**: Added `Adapter` import and `await Adapter.get_first(bus)`

### 5. UUID Improvement
- **File**: `ble_server.py:13`
- **Issue**: Short UUID "1234" was not standard
- **Fix**: Changed to proper 128-bit UUID: `"12345678-1234-5678-1234-56789abcdef1"`

## Key API Learning Points

1. **Advertisement Class**: Requires `timeout` parameter (0 = no timeout)
2. **Write Characteristics**: Use `.setter` decorator for write operations
3. **Adapter Required**: Advertisement registration needs adapter parameter
4. **UUID Format**: Use proper 128-bit UUIDs for custom characteristics

## Final Working Code Structure

```python
import asyncio
from bluez_peripheral.gatt.service import Service
from bluez_peripheral.gatt.characteristic import characteristic, CharacteristicFlags as CharFlags
from bluez_peripheral.advert import Advertisement
from bluez_peripheral.util import get_message_bus, Adapter

SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"

class MyCommandService(Service):
    def __init__(self):
        super().__init__(SERVICE_UUID, True)

    @characteristic("12345678-1234-5678-1234-56789abcdef1", CharFlags.WRITE)
    def command(self, options):
        pass

    @command.setter
    def command(self, value, options):
        cmd = bytes(value).decode("utf-8")
        print("Received:", cmd)
        # TODO: trigger GPIO/servo here

async def main():
    bus = await get_message_bus()
    svc = MyCommandService()
    await svc.register(bus)
    
    adapter = await Adapter.get_first(bus)
    ad = Advertisement("Yorick", [SERVICE_UUID], 0x0340, 0)
    await ad.register(bus, adapter)
    
    print("Advertising BLE service", SERVICE_UUID)
    await asyncio.get_event_loop().create_future()
```

## Result
The BLE server now has proper API usage and should work correctly for Web Bluetooth connections on Raspberry Pi.