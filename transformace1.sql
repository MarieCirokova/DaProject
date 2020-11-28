--a) vytvoření pomocné tabulky s výdejními místy
CREATE TABLE order_pick_up_2 AS 
SELECT "orderId"
    , "rideId"
    , "legStartedAt" AS orderCreatedAt
    , CASE
   WHEN "legDestinationLat" = XX.XXX AND "legDestinationLon" = XX.XXX THEN 'LUZINY'
   WHEN "legDestinationLat" = XX.XXX AND "legDestinationLon" = XX.XXX THEN 'ANDEL'
   WHEN "legDestinationLat" = XX.XXX AND "legDestinationLon" = XX.XXX THEN 'DEJVICKA'
   WHEN "legDestinationLat" = XX.XXX AND "legDestinationLon" = XX.XXX THEN 'HAJE'
   ELSE 'CHYBA'
   END AS pick_up_place
FROM delivery_legs
WHERE "legKind" = 'PICKUP';

--b) rozdělení balíčků AM/PM c) odstranění oulierů 
CREATE TABLE STACKING_VYDEJNA_2 AS
SELECT row_number() over ( order by OPU."orderId", DL1."legDestinationLat" ) as id
    , OPU."orderId"
    , TO_DATE(OPU.ordercreatedat) || ','|| CASE 
            WHEN TO_TIME(OPU.ordercreatedat) < '12:00:00' THEN 'AM'
            WHEN TO_TIME(OPU.ordercreatedat) >= '12:00:00' THEN 'PM'
            ELSE 'chyba'
            END  AS date_midd
   , OPU.pick_up_place
   , CASE 
    WHEN OPU.pick_up_place = 'HAJE' then 'XX.XXX'
    WHEN OPU.pick_up_place = 'LUZINY' then 'XX.XXX'
    WHEN OPU.pick_up_place = 'DEJVICKA' then 'XX.XXX'
    WHEN OPU.pick_up_place = 'ANDEL' then 'XX.XXX'
    ELSE 'CHYBA'
    END AS PICK_UP_LAT
     , CASE 
    WHEN OPU.pick_up_place = 'HAJE' then 'XX.XXX'
    WHEN OPU.pick_up_place = 'LUZINY' then 'XX.XXX'
    WHEN OPU.pick_up_place = 'DEJVICKA' then 'XX.XXX'
    WHEN OPU.pick_up_place = 'ANDEL' then 'XX.XXX'
    ELSE 'CHYBA'
    END AS PICK_UP_LON
   , DL1."legDestinationLat"
   , DL1."legDestinationLon"
FROM order_pick_up_2 AS OPU
JOIN delivery_legs AS DL1
ON OPU."orderId" = DL1."orderId"
WHERE "legKind" = 'DROP_OFF' AND HAVERSINE (50.08804, 14.42076, "legDestinationLat", "legDestinationLon") <= 18
ORDER BY (id, "orderId", "legStartedAt");
