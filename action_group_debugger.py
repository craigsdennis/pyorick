import sqlite3
import json
import argparse
import os

def read_action_group(filename):
    """Read SQLite database and return rows as JSON objects."""
    db_path = os.path.join("action_groups", f"{filename}.d6a")
    
    if not os.path.exists(db_path):
        print(f"Error: Database file {db_path} not found")
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # This makes rows behave like dictionaries
        cursor = conn.cursor()
        
        # Get all tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        result = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            # Convert rows to list of dictionaries
            result[table_name] = [dict(row) for row in rows]
        
        conn.close()
        return result
        
    except Exception as e:
        print(f"Error reading database: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Debug action groups SQLite databases")
    parser.add_argument("action_group", help="Name of the action group (without .d6a extension)")
    parser.add_argument("--pretty", "-p", action="store_true", help="Pretty print JSON output")
    
    args = parser.parse_args()
    
    data = read_action_group(args.action_group)
    if data:
        if args.pretty:
            print(json.dumps(data, indent=2))
        else:
            print(json.dumps(data))

if __name__ == "__main__":
    main()