
CREATE TABLE room_states
WITH (
  format = 'PARQUET',
  partitioned_by = ARRAY['checkin_date']
) AS 
SELECT 
  room_id,
  room_type,
  hotel_location,
  timestamp,
  reservation_status,
  checkin_date
FROM (
  SELECT 
    *,
    ROW_NUMBER() OVER (
      PARTITION BY room_id 
      ORDER BY timestamp DESC
    ) AS row_num
  FROM reservations
  WHERE reservation_status = 'checked_out'
)
WHERE row_num = 1;
