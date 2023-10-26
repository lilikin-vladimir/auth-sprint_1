MOVIES_SQL = (
    """
WITH FilmsForUpdate AS (
    SELECT DISTINCT fw.id
    FROM content.film_work fw
    """,
    'fw.id > %s AND ({where_str})',
    """
    ORDER BY fw.id
    LIMIT %s
)
SELECT
    fw.id,
    fw.title,
    COALESCE (fw.description, '') AS description,
    COALESCE (fw.rating, 0) AS imdb_rating,
    COALESCE (array_agg(DISTINCT g.name), '{}') AS genres_names,
    COALESCE (array_agg(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'director'), '{}') AS directors_names,
    COALESCE (array_agg(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'actor'), '{}') AS actors_names,
    COALESCE (array_agg(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'writer'), '{}') AS writers_names,
    COALESCE (
        json_agg(
            DISTINCT jsonb_build_object(
                'id', p.id,
                'full_name', p.full_name
            )
        ) FILTER (WHERE pfw.role = 'actor'),
        '[]'
    ) AS actors,
    COALESCE (
        json_agg(
            DISTINCT jsonb_build_object(
                'id', p.id,
                'full_name', p.full_name
            )
        ) FILTER (WHERE pfw.role = 'writer'),
        '[]'
    ) AS writers,
    COALESCE (
        json_agg(
            DISTINCT jsonb_build_object(
                'id', p.id,
                'full_name', p.full_name
            )
        ) FILTER (WHERE pfw.role = 'director'),
        '[]'
    ) AS directors,
    COALESCE (
        json_agg(
            DISTINCT jsonb_build_object(
                'id', g.id,
                'name', g.name
            )
        ),
        '[]'
    ) AS genres
FROM content.film_work fw
LEFT JOIN FilmsForUpdate ffu ON ffu.id = fw.id
LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
LEFT JOIN content.person p ON p.id = pfw.person_id
LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
LEFT JOIN content.genre g ON g.id = gfw.genre_id
WHERE ffu.id IS NOT NULL
GROUP BY fw.id
ORDER BY fw.id
""")

PERSONS_SQL = (
    """
WITH PersonsForUpdate AS (
    SELECT DISTINCT p.id, p.full_name
    FROM content.person p
    """,
    'p.id > %s AND ({where_str})',
    """
    ORDER BY p.id
    LIMIT %s
),
FilmRoles AS (
    SELECT 
        pfw.person_id,
        pfw.film_work_id,
        array_agg(pfw."role") AS roles
    FROM content.person_film_work pfw
    INNER JOIN PersonsForUpdate pfu ON pfu.id = pfw.person_id
    GROUP BY pfw.person_id, pfw.film_work_id
)
SELECT 
    pfu.id,
    pfu.full_name,
    COALESCE(
	    jsonb_agg(
	        jsonb_build_object(
	            'id', fr.film_work_id,
	            'roles', fr.roles
	        ) ORDER BY fr.film_work_id
        ) FILTER (WHERE fr.film_work_id IS NOT NULL), 
        '[]'::jsonb
    ) AS films
FROM PersonsForUpdate pfu
LEFT JOIN FilmRoles fr ON pfu.id = fr.person_id
GROUP BY pfu.id, pfu.full_name;
""")
