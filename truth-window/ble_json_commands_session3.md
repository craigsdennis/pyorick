# BLE JSON Commands & Utils Refactor Session 3

## User Request
User requested two enhancements:
1. Extract `get_available_action_groups` function into a shared utils file
2. Add JSON command support to BLE server with `{"type": "list_available_action_groups"}` command

## Tasks Completed

### 1. Code Refactoring - Utils Extraction

**Created `utils.py`**:
- Extracted `get_available_action_groups()` function for reusability
- Clean, documented function with proper return type documentation
- Handles file pattern matching and extension stripping

**Updated `fiddle.py`**:
- Removed duplicate `get_available_action_groups()` function
- Added import from utils module
- Maintains same functionality with cleaner code

**Updated `action_group_debugger.py`**:
- Added utils import (then removed as it wasn't actually needed)
- Maintained existing functionality

### 2. BLE Server JSON Command System

**Enhanced `ble_server.py`** with comprehensive JSON command support:

#### New Features:
1. **Response Characteristic**: `"12345678-1234-5678-1234-56789abcdef2"`
   - Flags: READ | NOTIFY
   - Returns JSON responses to commands

2. **JSON Command Parsing**:
   - Parses incoming commands as JSON
   - Falls back to plain text for backward compatibility
   - Error handling for malformed JSON

3. **Command Handler System**:
   - `handle_json_command()` method processes structured commands
   - Extensible architecture for adding new command types

4. **List Available Action Groups Command**:
   - Input: `{"type": "list_available_action_groups"}`
   - Output: 
     ```json
     {
       "type": "action_groups_list",
       "action_groups": ["hello", "left_test", "rock"],
       "success": true
     }
     ```

5. **Error Handling**:
   - Returns structured error responses for unknown commands
   - Format: `{"type": "error", "message": "...", "success": false}`

#### Technical Implementation:
- **Notification System**: Uses BLE characteristic notifications to push responses
- **State Management**: `_response_data` stores current response
- **Dual Protocol**: Supports both JSON and plain text commands
- **Imports**: Added json module and utils integration

### 3. System Architecture Improvements

**Shared Utilities**:
- Single source of truth for action group discovery
- Consistent behavior across all applications
- Easy maintenance and updates

**BLE Protocol Enhancement**:
- Two-way communication via command/response characteristics  
- Structured JSON protocol for complex interactions
- Maintains backward compatibility with existing plain text commands

## Files Modified/Created

1. **Created**: `utils.py` - Shared utility functions
2. **Modified**: `fiddle.py` - Uses shared utils
3. **Modified**: `action_group_debugger.py` - Import cleanup
4. **Modified**: `ble_server.py` - JSON command system

## Testing Results

### Utils Function Test:
- Successfully discovers action groups: hello, left_test, rock
- Proper extension removal (.d6a → name)
- Integration working in fiddle.py

### BLE JSON Command Test:
```python
test_command = {'type': 'list_available_action_groups'}
response = service.handle_json_command(test_command)
# Returns: {"type": "action_groups_list", "action_groups": [...], "success": true}
```

## Communication Protocol

### Command Characteristic (`...def1`):
**Write-only** - Send commands here

Examples:
- JSON: `{"type": "list_available_action_groups"}`
- Plain text: `"some_action_command"` (legacy support)

### Response Characteristic (`...def2`):
**Read/Notify** - Receive responses here

Response always in JSON format with:
- `type`: Response type identifier
- `success`: Boolean success indicator  
- Additional data fields based on command type

## Educational Value

This session demonstrates:
- **Code refactoring**: Extracting shared functionality into utils
- **Protocol design**: Creating extensible command/response systems
- **BLE characteristics**: Using multiple characteristics for bidirectional communication
- **Error handling**: Graceful degradation and structured error responses
- **Backward compatibility**: Maintaining existing functionality while adding new features
- **JSON serialization**: Structured data exchange over BLE
- **Notification patterns**: Push-based response delivery in BLE