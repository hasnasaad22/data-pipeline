select
    created_at,
    temperature,
    humidity
from {{ source('raw', 'weather_data') }}