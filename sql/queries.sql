-- Q1: Top Inventors
SELECT name, COUNT(DISTINCT patent_id) AS patent_count
FROM inventors
WHERE name != ''
GROUP BY inventor_id
ORDER BY patent_count DESC
LIMIT 10;

-- Q2: Top Companies
SELECT name, COUNT(DISTINCT patent_id) AS patent_count
FROM companies
WHERE name IS NOT NULL
GROUP BY company_id
ORDER BY patent_count DESC
LIMIT 10;

-- Q3: Countries
SELECT country, COUNT(DISTINCT patent_id) AS patent_count
FROM inventors
WHERE country IS NOT NULL
GROUP BY country
ORDER BY patent_count DESC
LIMIT 10;

-- Q4: Trends Over Time
SELECT year, COUNT(*) AS patent_count
FROM patents
WHERE year IS NOT NULL
GROUP BY year
ORDER BY year DESC;

-- Q5: JOIN Query
SELECT p.patent_id, p.title, i.name AS inventor, c.name AS company
FROM patents p
JOIN inventors i ON p.patent_id = i.patent_id
LEFT JOIN companies c ON p.patent_id = c.patent_id
LIMIT 10;

-- Q6: CTE Query
WITH inventor_counts AS (
    SELECT inventor_id, name, COUNT(DISTINCT patent_id) AS patent_count
    FROM inventors
    GROUP BY inventor_id
)
SELECT name, patent_count
FROM inventor_counts
WHERE patent_count > 50
ORDER BY patent_count DESC
LIMIT 10;

-- Q7: Ranking Query
SELECT name, patent_count,
       RANK() OVER (ORDER BY patent_count DESC) AS rank
FROM (
    SELECT inventor_id, name, COUNT(DISTINCT patent_id) AS patent_count
    FROM inventors
    GROUP BY inventor_id
)
LIMIT 10;
