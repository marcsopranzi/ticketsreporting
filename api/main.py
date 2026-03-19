from fastapi import FastAPI
from pydantic import BaseModel
from kafka import KafkaProducer
import json
import uuid
from datetime import datetime
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Postgres Setup (The Batch/dbt Layer)
engine = create_engine("postgresql://admin:password@postgres:5432/airflowdb")
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Ticket(Base):
    __tablename__ = "raw_tickets"
    transaction_id = Column(String, primary_key=True)
    user_id = Column(String)
    event_name = Column(String)
    timestamp = Column(String)

Base.metadata.create_all(bind=engine)

# 2. Kafka/Redpanda Setup (The Real-Time Layer)
producer = KafkaProducer(
    bootstrap_servers=['redpanda:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

app = FastAPI()

class TicketRequest(BaseModel):
    user_id: str
    event_name: str

@app.post("/buy-ticket")
def buy_ticket(ticket: TicketRequest):
    tx_id = str(uuid.uuid4())
    ts = datetime.utcnow().isoformat()
    
    # 1. Save to Postgres (For dbt later)
    db = SessionLocal()
    new_ticket = Ticket(transaction_id=tx_id, user_id=ticket.user_id, event_name=ticket.event_name, timestamp=ts)
    db.add(new_ticket)
    db.commit()
    db.close()

    # 2. Push to Kafka (For ClickHouse now)
    event = {
        "transaction_id": tx_id,
        "user_id": ticket.user_id,
        "event_name": ticket.event_name,
        "timestamp": ts
    }
    producer.send('ticket_sales', event)
    producer.flush()

    return {"status": "success", "transaction_id": tx_id}