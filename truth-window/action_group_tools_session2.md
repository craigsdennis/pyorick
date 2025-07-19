# Action Group Tools Development Session 2

## User Request
User requested two main enhancements:
1. Create a command line debugger for action groups (SQLite databases with .d6a extension)
2. Add command line argument support to the fiddle application with dynamic action group discovery

## Tasks Completed

### 1. Action Group Debugger (`action_group_debugger.py`)

**Purpose**: Read SQLite .d6a files and export rows as JSON objects with column names as keys.

**Features Implemented**:
- Command line argument parsing for action group names
- SQLite database reader with proper row-to-dict conversion
- JSON output with both compact and pretty-print options
- Error handling for missing files
- Multi-table support (reads all tables in database)

**Usage**:
```bash
python action_group_debugger.py <action_group_name> [--pretty]
```

**Example Output** (from `left_test.d6a`):
- ActionGroup table with 8 servo positions (Index, Time, Servo1-6 columns)
- Each row becomes a JSON object with column names as keys
- Also includes sqlite_sequence metadata table

**Key Implementation Details**:
- Uses `sqlite3.Row` for dictionary-like row access
- Scans all tables using `sqlite_master` query
- Handles file path construction: `./action_groups/<name>.d6a`

### 2. Enhanced Fiddle Application (`fiddle.py`)

**Original State**: Hardcoded to run "left_test" action group

**Enhancements Added**:
1. **Command line argument support**:
   - Optional action_group parameter with "left_test" as default
   - Maintains backward compatibility

2. **Dynamic action group discovery**:
   - `get_available_action_groups()` function scans `./action_groups/` directory
   - Finds all `.d6a` files and strips extensions
   - Updates help text dynamically

**Usage**:
```bash
# Run default (left_test)
python fiddle.py

# Run specific action group
python fiddle.py my_action_group

# Show help with available options
python fiddle.py --help
```

**Help Output Example**:
```
Name of the action group to run (default: left_test). Available: hello, left_test, rock
```

## Technical Implementation Notes

### Action Group Debugger
- **File**: `action_group_debugger.py`
- **Key functions**: `read_action_group()`, argument parsing
- **Dependencies**: `sqlite3`, `json`, `argparse`, `os`
- **Error handling**: Missing files, database connection issues

### Fiddle Application  
- **File**: `fiddle.py`
- **Key functions**: `get_available_action_groups()`
- **New imports**: `argparse`, `os`, `glob`
- **Backward compatibility**: Preserved default behavior

## Files Modified/Created
1. **Created**: `action_group_debugger.py` - Complete SQLite to JSON debugger
2. **Enhanced**: `fiddle.py` - Added CLI args and dynamic discovery

## Testing Results
- Action group debugger successfully reads `left_test.d6a`
- Outputs proper JSON with servo position data
- Dynamic discovery correctly finds: hello, left_test, rock action groups
- Both compact and pretty-print JSON formats work correctly

## Educational Value
This session demonstrates:
- SQLite database interaction in Python
- Command line argument parsing with argparse
- File system operations and pattern matching
- JSON serialization and formatting
- Backward compatibility maintenance
- Dynamic content discovery for user interfaces