DELETE FROM restaurants
    WHERE name IS NULL
    OR id NOT IN (
        SELECT MIN(id)
        FROM restaurants
        GROUP BY name,address
    )
    OR lower(NAME) LIKE '%nil'
    OR lower(NAME) LIKE '-%'
    OR LENGTH(name) < 3
    OR LOWER(name) LIKE 'halal%'
    OR name LIKE '-%'
    OR LOWER(name) LIKE 'vegetarian%'
    OR unit_no = ''
    OR unit_no = '0'
    OR unit_no IS NULL
    OR level = ''
    OR level = '0'
    OR level IS NULL
    OR latitude IS NULL
    OR longitude IS NULL
    OR address is NULL
    OR address = '';






