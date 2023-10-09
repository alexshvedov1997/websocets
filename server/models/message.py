from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text

from db import postgres


class Messages(postgres.Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))
    created_date = Column(DateTime, default=datetime.utcnow)
    parent_id = Column(Integer, ForeignKey("messages.id"))
