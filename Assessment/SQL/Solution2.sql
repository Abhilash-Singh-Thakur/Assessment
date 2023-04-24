SELECT 
  date_trunc('month', date) AS month,
  room_type,
  sum(booking_amount) AS total_bookings,
  avg(booking_amount) AS average_bookings,
  rank() OVER (PARTITION BY date_trunc('month', date) ORDER BY sum(booking_amount) DESC) AS rank
FROM 
  bookings
GROUP BY 
  GROUPING SETS (
    (date_trunc('month', date), room_type),
    (date_trunc('month', date))
  )
ORDER BY 
  month, 
  rank
