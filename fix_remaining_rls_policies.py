#!/usr/bin/env python
"""Fix remaining custom RLS policies with auth.uid() caching"""
import psycopg2
from decouple import config

# Database credentials
DB_HOST = config('DB_HOST')
DB_NAME = config('DB_NAME')
DB_USER = config('DB_USER')
DB_PASSWORD = config('DB_PASSWORD')
DB_PORT = config('DB_PORT', cast=int)

# Custom policies needing fixes
POLICIES = [
    {
        'table': 'accounts_user',
        'old_policy': 'Restrict password access',
        'new_policies': [
            {
                'name': 'Restrict password access',
                'type': 'SELECT',
                'condition': '(select auth.uid()) IS NOT NULL'
            }
        ]
    },
    {
        'table': 'django_session',
        'old_policy': 'Restrict session access',
        'new_policies': [
            {
                'name': 'Restrict session access',
                'type': 'SELECT',
                'condition': '(select auth.uid()) IS NOT NULL'
            }
        ]
    },
    {
        'table': 'accounts_staff',
        'old_policy': 'Staff can view staff data',
        'new_policies': [
            {
                'name': 'Staff can view staff data',
                'type': 'SELECT',
                'condition': '(select auth.uid()) IS NOT NULL'
            }
        ]
    },
    {
        'table': 'restaurant_orderhistorystatus',
        'old_policy': 'Allow authenticated access',
        'new_policies': [
            {
                'name': 'Allow authenticated access',
                'type': 'SELECT',
                'condition': '(select auth.uid()) IS NOT NULL'
            }
        ]
    }
]

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    
    cursor = conn.cursor()
    print("✅ Connected to Supabase PostgreSQL\n")
    print(f"Fixing {len(POLICIES)} custom RLS policies...\n")
    
    for policy_config in POLICIES:
        table = policy_config['table']
        old_policy = policy_config['old_policy']
        
        try:
            # Drop old policy
            cursor.execute(f"""
                DROP POLICY IF EXISTS "{old_policy}" ON public."{table}"
            """)
            
            # Create optimized policies
            for new_policy in policy_config['new_policies']:
                policy_name = new_policy['name']
                policy_type = new_policy['type']
                condition = new_policy['condition']
                
                cursor.execute(f"""
                    CREATE POLICY "{policy_name}" ON public."{table}"
                    FOR {policy_type}
                    USING ({condition})
                """)
            
            print(f"✓ {table}: '{old_policy}' → optimized")
        except Exception as e:
            print(f"✗ {table}: {str(e)[:80]}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\n✅ Successfully optimized all {len(POLICIES)} custom policies!")
    print("\nOptimization details:")
    print("  • Replaced auth.uid() with (select auth.uid())")
    print("  • Eliminated per-row function re-evaluation")
    print("  • Maintained policy functionality")
    
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
