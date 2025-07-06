-- Enable Row Level Security (RLS) for all public tables.
-- This is a critical security measure to prevent unauthorized access.
ALTER TABLE public.nse_announcements ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.nse_annual_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.nse_board_meetings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.nse_brsr ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.nse_circulars ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.nse_corporate_actions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.nse_insider_trading ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.nse_investor_complaints ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.nse_offer_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.nse_reason_for_encumbrance ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.nse_regulation29 ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.nse_regulation31 ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.nse_related_party_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.nse_secretarial_compliance ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.nse_share_transfers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.nse_shareholding_pattern ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.nse_statement_of_deviation ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.nse_unit_holding_pattern ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.nse_voting_results ENABLE ROW LEVEL SECURITY;

-- Create policies to allow public read-only access to the data.
-- This allows anyone using the public `anon` key to read data, but not modify it.
-- Your backend script using the `service_role` key will bypass these policies.

-- Drop policies if they exist to make this script idempotent.
DROP POLICY IF EXISTS "Allow public read-only access" ON public.nse_announcements;
DROP POLICY IF EXISTS "Allow public read-only access" ON public.nse_annual_reports;
DROP POLICY IF EXISTS "Allow public read-only access" ON public.nse_board_meetings;
DROP POLICY IF EXISTS "Allow public read-only access" ON public.nse_brsr;
DROP POLICY IF EXISTS "Allow public read-only access" ON public.nse_circulars;
DROP POLICY IF EXISTS "Allow public read-only access" ON public.nse_corporate_actions;
DROP POLICY IF EXISTS "Allow public read-only access" ON public.nse_insider_trading;
DROP POLICY IF EXISTS "Allow public read-only access" ON public.nse_investor_complaints;
DROP POLICY IF EXISTS "Allow public read-only access" ON public.nse_offer_documents;
DROP POLICY IF EXISTS "Allow public read-only access" ON public.nse_reason_for_encumbrance;
DROP POLICY IF EXISTS "Allow public read-only access" ON public.nse_regulation29;
DROP POLICY IF EXISTS "Allow public read-only access" ON public.nse_regulation31;
DROP POLICY IF EXISTS "Allow public read-only access" ON public.nse_related_party_transactions;
DROP POLICY IF EXISTS "Allow public read-only access" ON public.nse_secretarial_compliance;
DROP POLICY IF EXISTS "Allow public read-only access" ON public.nse_share_transfers;
DROP POLICY IF EXISTS "Allow public read-only access" ON public.nse_shareholding_pattern;
DROP POLICY IF EXISTS "Allow public read-only access" ON public.nse_statement_of_deviation;
DROP POLICY IF EXISTS "Allow public read-only access" ON public.nse_unit_holding_pattern;
DROP POLICY IF EXISTS "Allow public read-only access" ON public.nse_voting_results;

-- Create the actual policies
CREATE POLICY "Allow public read-only access" ON public.nse_announcements FOR SELECT USING (true);
CREATE POLICY "Allow public read-only access" ON public.nse_annual_reports FOR SELECT USING (true);
CREATE POLICY "Allow public read-only access" ON public.nse_board_meetings FOR SELECT USING (true);
CREATE POLICY "Allow public read-only access" ON public.nse_brsr FOR SELECT USING (true);
CREATE POLICY "Allow public read-only access" ON public.nse_circulars FOR SELECT USING (true);
CREATE POLICY "Allow public read-only access" ON public.nse_corporate_actions FOR SELECT USING (true);
CREATE POLICY "Allow public read-only access" ON public.nse_insider_trading FOR SELECT USING (true);
CREATE POLICY "Allow public read-only access" ON public.nse_investor_complaints FOR SELECT USING (true);
CREATE POLICY "Allow public read-only access" ON public.nse_offer_documents FOR SELECT USING (true);
CREATE POLICY "Allow public read-only access" ON public.nse_reason_for_encumbrance FOR SELECT USING (true);
CREATE POLICY "Allow public read-only access" ON public.nse_regulation29 FOR SELECT USING (true);
CREATE POLICY "Allow public read-only access" ON public.nse_regulation31 FOR SELECT USING (true);
CREATE POLICY "Allow public read-only access" ON public.nse_related_party_transactions FOR SELECT USING (true);
CREATE POLICY "Allow public read-only access" ON public.nse_secretarial_compliance FOR SELECT USING (true);
CREATE POLICY "Allow public read-only access" ON public.nse_share_transfers FOR SELECT USING (true);
CREATE POLICY "Allow public read-only access" ON public.nse_shareholding_pattern FOR SELECT USING (true);
CREATE POLICY "Allow public read-only access" ON public.nse_statement_of_deviation FOR SELECT USING (true);
CREATE POLICY "Allow public read-only access" ON public.nse_unit_holding_pattern FOR SELECT USING (true);
CREATE POLICY "Allow public read-only access" ON public.nse_voting_results FOR SELECT USING (true);