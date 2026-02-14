-- Supabase RLS remediation script
-- Review and run in Supabase SQL Editor (https://app.supabase.com)
-- This script enables RLS on flagged public tables, revokes anon access,
-- creates safe views for sensitive tables, and creates basic authenticated
-- SELECT policies. Adjust policies to match your schema and access model.

-- 1) Revoke anonymous access on all public tables (quick block)
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM anon;

-- 2) Enable RLS and add basic authenticated-only SELECT policy for each table
-- Replace or extend policies as needed for owner-only or role-specific access.

-- Listed tables from linter
ALTER TABLE public.django_migrations ENABLE ROW LEVEL SECURITY;
CREATE POLICY allow_authenticated_select_django_migrations ON public.django_migrations
  FOR SELECT TO authenticated USING (true);
REVOKE SELECT ON public.django_migrations FROM anon;

ALTER TABLE public.django_content_type ENABLE ROW LEVEL SECURITY;
CREATE POLICY allow_authenticated_select_django_content_type ON public.django_content_type
  FOR SELECT TO authenticated USING (true);
REVOKE SELECT ON public.django_content_type FROM anon;

ALTER TABLE public.auth_permission ENABLE ROW LEVEL SECURITY;
CREATE POLICY allow_authenticated_select_auth_permission ON public.auth_permission
  FOR SELECT TO authenticated USING (true);
REVOKE SELECT ON public.auth_permission FROM anon;

ALTER TABLE public.auth_group ENABLE ROW LEVEL SECURITY;
CREATE POLICY allow_authenticated_select_auth_group ON public.auth_group
  FOR SELECT TO authenticated USING (true);
REVOKE SELECT ON public.auth_group FROM anon;

ALTER TABLE public.auth_group_permissions ENABLE ROW LEVEL SECURITY;
CREATE POLICY allow_authenticated_select_auth_group_permissions ON public.auth_group_permissions
  FOR SELECT TO authenticated USING (true);
REVOKE SELECT ON public.auth_group_permissions FROM anon;

ALTER TABLE public.accounts_user ENABLE ROW LEVEL SECURITY;
CREATE POLICY allow_authenticated_select_accounts_user ON public.accounts_user
  FOR SELECT TO authenticated USING (true);
REVOKE SELECT ON public.accounts_user FROM anon;

ALTER TABLE public.accounts_user_groups ENABLE ROW LEVEL SECURITY;
CREATE POLICY allow_authenticated_select_accounts_user_groups ON public.accounts_user_groups
  FOR SELECT TO authenticated USING (true);
REVOKE SELECT ON public.accounts_user_groups FROM anon;

ALTER TABLE public.accounts_user_user_permissions ENABLE ROW LEVEL SECURITY;
CREATE POLICY allow_authenticated_select_accounts_user_user_permissions ON public.accounts_user_user_permissions
  FOR SELECT TO authenticated USING (true);
REVOKE SELECT ON public.accounts_user_user_permissions FROM anon;

ALTER TABLE public.accounts_staff ENABLE ROW LEVEL SECURITY;
CREATE POLICY allow_authenticated_select_accounts_staff ON public.accounts_staff
  FOR SELECT TO authenticated USING (true);
REVOKE SELECT ON public.accounts_staff FROM anon;

ALTER TABLE public.accounts_staffpermission ENABLE ROW LEVEL SECURITY;
CREATE POLICY allow_authenticated_select_accounts_staffpermission ON public.accounts_staffpermission
  FOR SELECT TO authenticated USING (true);
REVOKE SELECT ON public.accounts_staffpermission FROM anon;

ALTER TABLE public.django_admin_log ENABLE ROW LEVEL SECURITY;
CREATE POLICY allow_authenticated_select_django_admin_log ON public.django_admin_log
  FOR SELECT TO authenticated USING (true);
REVOKE SELECT ON public.django_admin_log FROM anon;

ALTER TABLE public.restaurant_table ENABLE ROW LEVEL SECURITY;
CREATE POLICY allow_authenticated_select_restaurant_table ON public.restaurant_table
  FOR SELECT TO authenticated USING (true);
REVOKE SELECT ON public.restaurant_table FROM anon;

ALTER TABLE public.restaurant_category ENABLE ROW LEVEL SECURITY;
CREATE POLICY allow_authenticated_select_restaurant_category ON public.restaurant_category
  FOR SELECT TO authenticated USING (true);
REVOKE SELECT ON public.restaurant_category FROM anon;

ALTER TABLE public.restaurant_orderitem ENABLE ROW LEVEL SECURITY;
CREATE POLICY allow_authenticated_select_restaurant_orderitem ON public.restaurant_orderitem
  FOR SELECT TO authenticated USING (true);
REVOKE SELECT ON public.restaurant_orderitem FROM anon;

ALTER TABLE public.restaurant_payment ENABLE ROW LEVEL SECURITY;
CREATE POLICY allow_authenticated_select_restaurant_payment ON public.restaurant_payment
  FOR SELECT TO authenticated USING (true);
REVOKE SELECT ON public.restaurant_payment FROM anon;

ALTER TABLE public.restaurant_menuitem ENABLE ROW LEVEL SECURITY;
CREATE POLICY allow_authenticated_select_restaurant_menuitem ON public.restaurant_menuitem
  FOR SELECT TO authenticated USING (true);
REVOKE SELECT ON public.restaurant_menuitem FROM anon;

ALTER TABLE public.restaurant_order ENABLE ROW LEVEL SECURITY;
CREATE POLICY allow_authenticated_select_restaurant_order ON public.restaurant_order
  FOR SELECT TO authenticated USING (true);
REVOKE SELECT ON public.restaurant_order FROM anon;

ALTER TABLE public.restaurant_orderhistory ENABLE ROW LEVEL SECURITY;
CREATE POLICY allow_authenticated_select_restaurant_orderhistory ON public.restaurant_orderhistory
  FOR SELECT TO authenticated USING (true);
REVOKE SELECT ON public.restaurant_orderhistory FROM anon;

ALTER TABLE public.restaurant_orderhistoryitem ENABLE ROW LEVEL SECURITY;
CREATE POLICY allow_authenticated_select_restaurant_orderhistoryitem ON public.restaurant_orderhistoryitem
  FOR SELECT TO authenticated USING (true);
REVOKE SELECT ON public.restaurant_orderhistoryitem FROM anon;

ALTER TABLE public.restaurant_orderhistorypayment ENABLE ROW LEVEL SECURITY;
CREATE POLICY allow_authenticated_select_restaurant_orderhistorypayment ON public.restaurant_orderhistorypayment
  FOR SELECT TO authenticated USING (true);
REVOKE SELECT ON public.restaurant_orderhistorypayment FROM anon;

ALTER TABLE public.restaurant_orderhistorystatus ENABLE ROW LEVEL SECURITY;
CREATE POLICY allow_authenticated_select_restaurant_orderhistorystatus ON public.restaurant_orderhistorystatus
  FOR SELECT TO authenticated USING (true);
REVOKE SELECT ON public.restaurant_orderhistorystatus FROM anon;

ALTER TABLE public.restaurant_orderstatuslog ENABLE ROW LEVEL SECURITY;
CREATE POLICY allow_authenticated_select_restaurant_orderstatuslog ON public.restaurant_orderstatuslog
  FOR SELECT TO authenticated USING (true);
REVOKE SELECT ON public.restaurant_orderstatuslog FROM anon;

ALTER TABLE public.django_session ENABLE ROW LEVEL SECURITY;
CREATE POLICY allow_authenticated_select_django_session ON public.django_session
  FOR SELECT TO authenticated USING (true);
REVOKE SELECT ON public.django_session FROM anon;

-- 3) Create safe views for tables with sensitive columns and grant controlled access
-- Accounts user: avoid exposing password column
CREATE OR REPLACE VIEW public.accounts_user_safe AS
SELECT id, username, email, first_name, last_name, role, is_active, created_at
FROM public.accounts_user;
GRANT SELECT ON public.accounts_user_safe TO anon;
REVOKE SELECT ON public.accounts_user FROM anon;

-- Django session: do not expose session_data or session_key; provide expire dates only (if needed)
CREATE OR REPLACE VIEW public.django_session_safe AS
SELECT expire_date
FROM public.django_session;
-- Keep base session table protected (no anon)
REVOKE SELECT ON public.django_session FROM anon;

-- 4) Example owner-only policy (adapt column names/types to your schema)
-- ALTER TABLE public.restaurant_order ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY owner_only_restaurant_order ON public.restaurant_order
--   FOR ALL
--   USING (owner_id::text = auth.uid())
--   WITH CHECK (owner_id::text = auth.uid());

-- End of script.
