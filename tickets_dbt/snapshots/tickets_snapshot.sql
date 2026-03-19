{% snapshot tickets_snapshot %}

{{
    config(
      target_database='airflowdb',
      target_schema='public',
      unique_key='transaction_id',

      strategy='timestamp',
      updated_at='timestamp'
    )
}}

SELECT * FROM {{ source('postgres_raw', 'raw_tickets') }}

{% endsnapshot %}