#!/usr/bin/env python
"""
Supabase Configuration Helper Script

This script helps you set up your Supabase credentials in the .env file.
It validates your configuration and tests the connection.

Usage:
    python setup_supabase.py              # Interactive setup
    python setup_supabase.py --skip-test  # Setup without testing connection
    python setup_supabase.py --show       # Show current configuration
"""

import os
import sys
from pathlib import Path
from decouple import config
from dotenv import dotenv_values, load_dotenv
import psycopg2

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def print_section(text):
    """Print a formatted section"""
    print(f"\n► {text}\n")

def get_supabase_credentials_interactive():
    """Get Supabase credentials through interactive prompts"""
    print_header("SUPABASE CONFIGURATION SETUP")
    
    print("This wizard will help you set up your Supabase database connection.")
    print("You can find these values in your Supabase project dashboard.")
    print("\nSettings → Database → Connection String (PostgreSQL)")
    
    print_section("Enter Your Supabase Credentials")
    
    # Get host
    while True:
        db_host = input("Database Host (db.xxxxx.supabase.co): ").strip()
        if db_host and '.supabase.co' in db_host:
            break
        print("✗ Invalid host. Must be in format: db.xxxxx.supabase.co")
    
    # Get user
    db_user = input("Database User [postgres]: ").strip() or "postgres"
    
    # Get password
    import getpass
    db_password = getpass.getpass("Database Password (input hidden): ").strip()
    if not db_password:
        print("✗ Password is required")
        return None
    
    # Get database name
    db_name = input("Database Name [postgres]: ").strip() or "postgres"
    
    # Get port
    while True:
        port_input = input("Port [5432]: ").strip() or "5432"
        try:
            db_port = int(port_input)
            break
        except ValueError:
            print("✗ Port must be a number")
    
    return {
        'DB_HOST': db_host,
        'DB_USER': db_user,
        'DB_PASSWORD': db_password,
        'DB_NAME': db_name,
        'DB_PORT': str(db_port),
    }

def test_connection(credentials):
    """Test connection to Supabase database"""
    print_section("Testing Connection to Supabase...")
    
    try:
        print("Connecting to Supabase... ", end="", flush=True)
        
        conn = psycopg2.connect(
            host=credentials['DB_HOST'],
            database=credentials['DB_NAME'],
            user=credentials['DB_USER'],
            password=credentials['DB_PASSWORD'],
            port=int(credentials['DB_PORT']),
            sslmode='require',
            connect_timeout=10
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        print("✓ Connected!")
        print(f"  Server: {version.split(',')[0]}")
        print("\n✓ Connection successful!")
        return True
        
    except psycopg2.Error as e:
        print("✗ Failed!")
        print(f"\n✗ Connection error: {e}")
        print("\nPossible causes:")
        print("  1. Incorrect credentials")
        print("  2. Supabase project not initialized yet (wait 1-2 minutes)")
        print("  3. Network connectivity issue")
        print("  4. Password contains special characters that need escaping")
        return False

def write_env_file(credentials, env_file='.env'):
    """Write credentials to .env file"""
    print_section(f"Writing Credentials to {env_file}")
    
    # Read existing .env if it exists
    env_path = Path(env_file)
    existing_content = ""
    if env_path.exists():
        with open(env_path, 'r') as f:
            existing_content = f.read()
    
    # Prepare new content
    new_credentials = f"""# Supabase PostgreSQL Database Configuration
DB_HOST={credentials['DB_HOST']}
DB_PORT={credentials['DB_PORT']}
DB_NAME={credentials['DB_NAME']}
DB_USER={credentials['DB_USER']}
DB_PASSWORD={credentials['DB_PASSWORD']}
USE_SUPABASE=True
"""
    
    # Update or create .env
    if existing_content:
        # Remove old database config
        lines = existing_content.split('\n')
        new_lines = []
        skip_until_empty = False
        
        for line in lines:
            if line.startswith(('DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'USE_SUPABASE')):
                continue
            new_lines.append(line)
        
        content = '\n'.join(new_lines).rstrip() + '\n\n' + new_credentials
    else:
        content = new_credentials
    
    with open(env_path, 'w') as f:
        f.write(content)
    
    print(f"✓ Configuration written to {env_file}")
    
    # Show what was written
    print("\nConfiguration added:")
    for key, value in credentials.items():
        if key == 'DB_PASSWORD':
            display_value = '*' * (len(value) - 4) + value[-4:]
        else:
            display_value = value
        print(f"  {key}={display_value}")
    
    return True

def show_current_config():
    """Show current Supabase configuration"""
    print_header("CURRENT CONFIGURATION")
    
    load_dotenv()
    
    db_host = os.getenv('DB_HOST', '')
    db_user = os.getenv('DB_USER', '')
    db_password = os.getenv('DB_PASSWORD', '')
    db_name = os.getenv('DB_NAME', '')
    db_port = os.getenv('DB_PORT', '')
    use_supabase = os.getenv('USE_SUPABASE', '')
    
    print("Supabase Configuration:")
    print(f"  DB_HOST:        {db_host if db_host else '(not set)'}")
    print(f"  DB_PORT:        {db_port if db_port else '(not set)'}")
    print(f"  DB_NAME:        {db_name if db_name else '(not set)'}")
    print(f"  DB_USER:        {db_user if db_user else '(not set)'}")
    print(f"  DB_PASSWORD:    {'*' * 4 + db_password[-4:] if db_password else '(not set)'}")
    print(f"  USE_SUPABASE:   {use_supabase if use_supabase else '(not set)'}")
    
    # Check if configured
    is_configured = all([db_host, db_user, db_password, db_name, db_port])
    
    print(f"\n  Status: {'✓ Configured' if is_configured else '✗ Not configured'}")
    
    if not is_configured and (db_host or db_user or db_name):
        print("\n  Missing fields:")
        if not db_host:
            print("    - DB_HOST")
        if not db_user:
            print("    - DB_USER")
        if not db_password:
            print("    - DB_PASSWORD")
        if not db_name:
            print("    - DB_NAME")
        if not db_port:
            print("    - DB_PORT")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Configure Supabase database connection'
    )
    parser.add_argument('--skip-test', action='store_true',
                       help='Skip connection test after setup')
    parser.add_argument('--show', action='store_true',
                       help='Show current configuration')
    
    args = parser.parse_args()
    
    if args.show:
        show_current_config()
        return 0
    
    # Interactive setup
    credentials = get_supabase_credentials_interactive()
    
    if not credentials:
        print("\n✗ Setup cancelled")
        return 1
    
    # Test connection unless --skip-test
    if not args.skip_test:
        if not test_connection(credentials):
            print("\n⚠ Connection test failed. Writing configuration anyway...")
    
    # Write to .env
    if write_env_file(credentials):
        print_section("Setup Complete!")
        print("You can now run the migration:")
        print("  python migrate_sqlite_to_supabase.py --backup")
        print("  python migrate_sqlite_to_supabase.py")
        return 0
    else:
        print("\n✗ Failed to write configuration")
        return 1

if __name__ == '__main__':
    sys.exit(main())
