select place_name, visit_date from visits
INNER JOIN places
ON visits.place_id = places.place_id