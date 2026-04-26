SELECT
    created_at,
    temperature,
    humidity
FROM {{ source('raw', 'weather_data') }}