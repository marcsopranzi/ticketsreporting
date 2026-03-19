-- 1. Create the pipe that listens to Redpanda/Kafka
CREATE TABLE IF NOT EXISTS kafka_ticket_queue (
    transaction_id String,
    user_id String,
    event_name String,
    timestamp String
) ENGINE = Kafka
SETTINGS kafka_broker_list = 'redpanda:9092',
         kafka_topic_list = 'ticket_sales',
         kafka_group_name = 'clickhouse_consumer',
         kafka_format = 'JSONEachRow';

-- 2. Create the fast, permanent OLAP table
CREATE TABLE IF NOT EXISTS live_ticket_sales (
    transaction_id String,
    user_id String,
    event_name String,
    timestamp String
) ENGINE = MergeTree()
ORDER BY timestamp;

-- 3. Create the Materialized View that moves data
CREATE MATERIALIZED VIEW IF NOT EXISTS ticket_consumer TO live_ticket_sales AS
SELECT * FROM kafka_ticket_queue;