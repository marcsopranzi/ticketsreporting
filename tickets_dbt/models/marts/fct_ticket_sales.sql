{{
    config(
        materialized='incremental',
        unique_key='transaction_id'
    )
}}

WITH new_tickets AS (
    SELECT 
        transaction_id,
        user_id,
        event_name,
        -- Cast the string timestamp from the API into an actual timestamp
        CAST(timestamp AS TIMESTAMP) AS sold_at
    FROM {{ source('postgres_raw', 'raw_tickets') }}
    
    {% if is_incremental() %}
        -- Only grab tickets sold AFTER the latest timestamp currently in this table
        WHERE CAST(timestamp AS TIMESTAMP) > (SELECT MAX(sold_at) FROM {{ this }})
    {% endif %}
)

SELECT * FROM new_tickets