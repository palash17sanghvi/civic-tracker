-- Civic Data Aggregator — Phase 4 Analytics Queries
-- ----------------------------------------------------
-- These queries cross-reference member fundraising data (FEC) with
-- legislative activity (Congress.gov sponsorships) to surface real
-- insights from the ingested dataset.

-- 1. Top fundraisers, with how many bills they've sponsored
--    (sponsorship data scoped to a 300-bill sample — see README for scope notes)
SELECT m.first_name, m.last_name, m.party, d.total_receipts, COUNT(s.id) AS bills_sponsored
FROM api_member m
JOIN api_donor d ON d.member_id = m.id
LEFT JOIN api_sponsorship s ON s.member_id = m.id
GROUP BY m.id, d.total_receipts
ORDER BY d.total_receipts DESC
LIMIT 10;

-- 2. Average fundraising by party
SELECT m.party, COUNT(d.id) AS num_members, ROUND(AVG(d.total_receipts), 2) AS avg_receipts
FROM api_donor d
JOIN api_member m ON d.member_id = m.id
GROUP BY m.party
ORDER BY avg_receipts DESC;

-- 3. Top sponsors (most bills sponsored in our sample)
SELECT m.first_name, m.last_name, m.party, COUNT(s.id) AS bills_sponsored
FROM api_member m
JOIN api_sponsorship s ON s.member_id = m.id
GROUP BY m.id
ORDER BY bills_sponsored DESC
LIMIT 10;


-- ----------------------------------------------------
-- Indexing note (EXPLAIN ANALYZE finding)
-- ----------------------------------------------------
-- Ran EXPLAIN ANALYZE on query #1 filtered to high fundraisers
-- (total_receipts > 5,000,000). Result: Postgres used Seq Scan on both
-- api_member (2,693 rows) and api_donor (596 rows), completing in ~1ms.
--
-- At this data volume, a sequential scan is the correct and fastest
-- strategy — the tables are small enough that scanning every row is
-- cheaper than the overhead of an index lookup. Adding an index here
-- would not meaningfully improve performance and could be premature
-- optimization.
--
-- Indexes on total_receipts / member_id would become worthwhile once
-- these tables scale into the tens of thousands of rows or more —
-- e.g., if this pipeline ingested full individual-donor-level FEC data
-- (Schedule A) rather than per-candidate aggregate totals.
