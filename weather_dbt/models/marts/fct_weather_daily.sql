select
    date(created_at) as date,
    avg(temperature) as avg_temp,
    max(temperature) as max_temp,
    min(temperature) as min_temp,
    avg(humidity) as avg_humidity
from {{ ref('stg_weather') }}
group by date(created_at)