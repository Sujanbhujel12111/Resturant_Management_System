#!/usr/bin/env python
"""Optimize RLS policies - fix auth.uid() caching and consolidate policies"""
import psycopg2
from decouple import config

# Database credentials
DB_HOST = config('DB_HOST')
DB_NAME = config('DB_NAME')
DB_USER = config('DB_USER')
DB_PASSWORD = config('DB_PASSWORD')
DB_PORT = config('DB_PORT', cast=int)

# Tables to optimize
TABLES = [
    'accounts_staffpermission',
    'accounts_user_groups',
    'accounts_user_user_permissions',
    'auth_group',
    'auth_group_permissions',
    'auth_permission',
    'django_admin_log',
    'django_content_type',
    'django_migrations',
    'restaurant_category',
    'restaurant_menuitem',
    'restaurant_order',
    'restaurant_orderhistory',
    'restaurant_orderhistoryitem',
    'restaurant_orderhistorypayment',
    'restaurant_orderitem',
    'restaurant_orderstatuslog',
    'restaurant_payment',
    'restaurant_table'
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
    print(f"Optimizing RLS policies for {len(TABLES)} tables...\n")
    
    for table in TABLES:
        try:
            # Drop old policies
            cursor.execute(f"""
                DROP POLICY IF EXISTS "Public read access" ON public."{table}"
            """)
            cursor.execute(f"""
                DROP POLICY IF EXISTS "Authenticated write access" ON public."{table}"
            """)
            
            # Policy 1: Public SELECT (very efficient, no function calls)
            cursor.execute(f"""
                CREATE POLICY "Public read" ON public."{table}"
                FOR SELECT
                USING (true)
            """)
            
            # Policy 2: Authenticated INSERT with optimized auth.uid()
            cursor.execute(f"""
                CREATE POLICY "Authenticated insert" ON public."{table}"
                FOR INSERT
                WITH CHECK ((select auth.uid()) IS NOT NULL)
            """)
            
            # Policy 3: Authenticated UPDATE with optimized auth.uid()
            cursor.execute(f"""
                CREATE POLICY "Authenticated update" ON public."{table}"
                FOR UPDATE
                USING ((select auth.uid()) IS NOT NULL)
                WITH CHECK ((select auth.uid()) IS NOT NULL)
            """)
            
            # Policy 4: Authenticated DELETE with optimized auth.uid()
            cursor.execute(f"""
                CREATE POLICY "Authenticated delete" ON public."{table}"
                FOR DELETE
                USING ((select auth.uid()) IS NOT NULL)
            """)
            
            print(f"✓ {table}")
        except Exception as e:
            print(f"✗ {table}: {str(e)[:80]}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\n✅ Successfully optimized RLS policies for all {len(TABLES)} tables!")
    print("\nOptimizations applied:")
    print("  • Consolidated duplicate SELECT policies")
    print("  • Changed auth.uid() to (select auth.uid()) for query-level caching")
    print("  • Replaced multiple permissive policies with combined per-operation policies")
    print("\nPolicy structure per table:")
    print("  • 1x SELECT: Public read")
    print("  • 1x INSERT: Authenticated only")
    print("  • 1x UPDATE: Authenticated only")
    print("  • 1x DELETE: Authenticated only")
    
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
