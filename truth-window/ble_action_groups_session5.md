# BLE Action Group Execution Session 5

## User Request  
After successfully fixing BLE notifications, user requested adding action group execution capability to the BLE server. Specifically: handle `{"type":"run_action_group","name":"hello"}` commands similar to the fiddle.py implementation.

## Implementation Overview

### Integration Strategy
Analyzed `fiddle.py` to understand the action group execution pattern:
- Uses `ActionGroupController` and `Board` from `common` SDK
- Executes actions via `agc.runAction()` in separate threads
- Provides path configuration for action group files

### Key Features Implemented

#### 1. Dynamic Import System
**File**: `ble_server.py:13-19`
```python
try:
    from common.action_group_controller import ActionGroupController
    from common.ros_robot_controller_sdk import Board
    ACTION_GROUPS_AVAILABLE = True
except ImportError:
    print("Warning: Action group controller not available (not on Pi)")
    ACTION_GROUPS_AVAILABLE = False
```

**Benefits**:
- Works on both Pi (with hardware) and development machines
- Graceful degradation when hardware not available
- Clear status reporting for debugging

#### 2. Service Initialization Enhancement  
**File**: `ble_server.py:28-38`
```python
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
```

#### 3. Action Execution Method
**File**: `ble_server.py:68-80`  
```python
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
```

**Features**:
- Thread-based execution (non-blocking for BLE server)
- Error handling and status reporting
- Matches fiddle.py execution pattern exactly

#### 4. JSON Command Handler Extension
**File**: `ble_server.py:93-118`

**Command Format**: `{"type": "run_action_group", "name": "hello"}`

**Validation Steps**:
1. **Parameter Check**: Ensures `name` field is provided
2. **Existence Validation**: Verifies action group exists in filesystem  
3. **Execution Attempt**: Runs action group via controller
4. **Status Response**: Returns success/failure with details

**Response Formats**:
```json
// Success
{
    "type": "action_group_result",
    "action_name": "hello", 
    "success": true,
    "message": "Action group 'hello' started successfully"
}

// Error - Missing parameter
{
    "type": "error",
    "message": "Missing 'name' parameter for run_action_group command",
    "success": false
}

// Error - Action group not found
{
    "type": "error",
    "message": "Action group 'nonexistent' not found. Available: hello, left_test, rock",
    "success": false
}
```

## Testing Results

### Command Validation Tests
✓ **List Command**: Returns available action groups  
✓ **Valid Action**: Processes `hello` action group command  
✓ **Invalid Action**: Rejects `nonexistent` with helpful error message  
✓ **Missing Parameter**: Handles missing `name` field gracefully  
✓ **Hardware Simulation**: Graceful degradation without Pi hardware

### Expected Pi Behavior
When running on actual Pi with hardware:
1. **Initialization**: Action group controller connects to servo board
2. **Execution**: `hello` action group runs servo sequences
3. **Response**: JSON confirmation sent via BLE notification
4. **Threading**: Non-blocking execution allows continued BLE operation

## BLE Command Protocol (Updated)

### Available Commands
1. **List Action Groups**:
   ```json
   {"type": "list_available_action_groups"}
   ```

2. **Run Action Group**:
   ```json
   {"type": "run_action_group", "name": "hello"}
   ```

### Communication Flow
```
Client                          Pi BLE Server
  │                                   │
  ├── Write JSON command ──────────► │
  │                                   ├── Parse & validate
  │                                   ├── Execute action (threaded)
  │ ◄─────────── Notification ───────┤ Send JSON response
  │                                   │
```

## Architecture Benefits

### 1. **Non-Blocking Execution**
- Action groups run in separate threads
- BLE server remains responsive during servo operations
- Multiple commands can be queued/processed

### 2. **Robust Error Handling**
- Hardware availability detection
- Action group existence validation  
- Execution error catching and reporting
- Graceful degradation patterns

### 3. **Development Compatibility**
- Works on development machines without hardware
- Consistent API regardless of hardware availability
- Clear status messages for debugging

### 4. **Protocol Consistency**
- Same JSON command/response pattern as listing
- Standardized error message formats
- Success/failure indicators in all responses

## Educational Value
This session demonstrates:
- **Hardware abstraction** for cross-platform development
- **Thread-based execution** for non-blocking operations
- **Robust validation** patterns for user input
- **Error handling** strategies for hardware dependencies
- **Protocol design** for BLE command/response systems
- **Code reuse** patterns from existing implementations (fiddle.py)
- **Graceful degradation** when dependencies unavailable