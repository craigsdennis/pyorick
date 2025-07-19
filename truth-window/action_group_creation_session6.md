# Action Group Creation Session 6

## User Request
Following the successful implementation of action group execution in Session 5, user requested the ability to create new action groups dynamically via BLE. The frontend will send action group data and name, which should be saved as SQLite .d6a database files.

## Implementation Overview

### Requirements Analysis
- **Storage Format**: SQLite databases with `.d6a` extension
- **Database Schema**: Existing `ActionGroup` table with Index (auto-increment), Time, and 6 servo columns
- **Input Format**: JSON array with Time and Servo1-6 values for each step
- **Integration**: Add to BLE server as new `save_action_group` command

### Key Components Implemented

#### 1. Database Creation Function (utils.py)
**File**: `utils.py:15-86`

**Function**: `create_action_group(name, action_steps)`

**Features**:
- **Schema Compliance**: Uses exact CREATE TABLE statement from existing code
- **Auto-increment Index**: Maintains compatibility with existing action groups
- **Directory Management**: Ensures `action_groups/` directory exists
- **Error Handling**: Comprehensive exception catching and reporting
- **Exact Value Usage**: Uses passed servo values without defaults

**Database Schema**:
```sql
CREATE TABLE ActionGroup(
    [Index] INTEGER PRIMARY KEY AUTOINCREMENT
    NOT NULL ON CONFLICT FAIL
    UNIQUE ON CONFLICT ABORT,
    Time INT,
    Servo1 INT, Servo2 INT, Servo3 INT,
    Servo4 INT, Servo5 INT, Servo6 INT
)
```

**Return Format**:
```python
{
    "success": True,
    "message": "Action group 'Test' created successfully with 2 steps",
    "file_path": "action_groups/Test.d6a"
}
```

#### 2. BLE Command Integration
**File**: `ble_server.py:119-146`

**Command Format**:
```json
{
    "type": "save_action_group",
    "name": "Test",
    "action_group": [
        {
            "Time": 400,
            "Servo1": 1500, "Servo2": 200, "Servo3": 1500,
            "Servo4": 1500, "Servo5": 1500, "Servo6": 1500
        },
        {
            "Time": 400,  
            "Servo1": 1500, "Servo2": 1500, "Servo3": 2800,
            "Servo4": 2800, "Servo5": 1500, "Servo6": 1500
        }
    ]
}
```

**Validation Steps**:
1. **Parameter Presence**: Ensures both `name` and `action_group` are provided
2. **Empty Array Check**: Rejects empty action_group arrays
3. **Database Creation**: Delegates to utils function for actual creation
4. **Response Formatting**: Returns standardized JSON response

**Response Format**:
```json
{
    "type": "action_group_saved",
    "action_name": "Test",
    "success": true,
    "message": "Action group 'Test' created successfully with 2 steps",
    "steps_count": 2
}
```

## Testing Results

### Functionality Verification
✓ **Database Creation**: SQLite files created with proper schema  
✓ **Data Integrity**: Servo values stored exactly as provided  
✓ **BLE Integration**: Command handler processes requests correctly  
✓ **File Discovery**: New action groups appear in available lists  
✓ **Debugger Compatibility**: Created files readable by action_group_debugger.py

### Created Database Verification
```json
{
  "ActionGroup": [
    {
      "Index": 1, "Time": 400,
      "Servo1": 1500, "Servo2": 200, "Servo3": 1500,
      "Servo4": 1500, "Servo5": 1500, "Servo6": 1500
    },
    {
      "Index": 2, "Time": 400,
      "Servo1": 1500, "Servo2": 1500, "Servo3": 2800,
      "Servo4": 2800, "Servo5": 1500, "Servo6": 1500
    }
  ]
}
```

### Edge Case Handling
✓ **Missing Name**: Returns appropriate error message  
✓ **Missing Action Group**: Validates action_group parameter presence  
✓ **Empty Array**: Rejects empty action step arrays  
✓ **Database Errors**: Catches and reports SQLite exceptions

### Integration Testing
✓ **List Integration**: New action groups appear in `list_available_action_groups`  
✓ **Execute Integration**: Created action groups can be run via `run_action_group`  
✓ **File System**: Files created in correct location with proper extensions

## Complete BLE Command Protocol (Updated)

### Available Commands
1. **List Action Groups**:
   ```json
   {"type": "list_available_action_groups"}
   ```

2. **Run Action Group**:
   ```json
   {"type": "run_action_group", "name": "hello"}
   ```

3. **Save Action Group** (NEW):
   ```json
   {
       "type": "save_action_group",
       "name": "CustomAction",
       "action_group": [
           {"Time": 500, "Servo1": 1500, "Servo2": 1800, "Servo3": 1200, "Servo4": 1500, "Servo5": 1500, "Servo6": 1500}
       ]
   }
   ```

## Workflow Integration

### Complete Action Group Lifecycle
```
Frontend                    BLE Server                   Filesystem
    │                          │                            │
    ├── Save Request ────────► │                            │
    │                          ├── Validate params         │
    │                          ├── Create SQLite ─────────► │
    │   ◄────── Response ──────┤                            ├── Write .d6a file
    │                          │                            │
    ├── List Request ─────────► │                            │
    │   ◄────── Available ─────├── Scan directory ◄────────┤
    │                          │                            │
    ├── Execute Request ──────► │                            │
    │                          ├── Load from file ◄────────┤
    │   ◄────── Status ────────┤ ├── Run servo sequence     │
    │                          │                            │
```

## Technical Architecture

### Data Flow
1. **Frontend Creation**: User designs servo sequence in web interface
2. **BLE Transmission**: JSON command sent via Web Bluetooth write
3. **Server Validation**: Parameters checked and action steps validated
4. **Database Creation**: SQLite file created with proper schema
5. **Immediate Availability**: New action group instantly available for execution

### File System Integration
- **Location**: `./action_groups/` directory
- **Naming**: `{name}.d6a` format maintains consistency
- **Discovery**: Automatic inclusion in directory scans
- **Compatibility**: Full compatibility with existing tools and execution

### Error Resilience
- **Validation Layers**: Multiple validation steps prevent invalid data
- **Exception Handling**: Database errors caught and reported gracefully
- **Parameter Checking**: Missing or invalid parameters detected early
- **File System Safety**: Directory creation ensures write location exists

## Educational Value
This session demonstrates:
- **Dynamic Database Creation** from JSON data structures
- **SQLite Schema Compliance** with existing database formats
- **BLE Protocol Extension** adding new command types seamlessly  
- **File System Integration** with automatic discovery mechanisms
- **Validation Strategies** for complex nested data structures
- **Error Handling Patterns** across multiple architectural layers
- **Cross-Tool Compatibility** ensuring new files work with existing utilities
- **Data Persistence** from temporary JSON to permanent SQLite storage