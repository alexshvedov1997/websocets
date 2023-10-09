from sqlalchemy import Column, Integer, String

from db import postgres


class User(postgres.Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    user_id = Column(String, nullable=False)
    report_count = Column(Integer, default=0)
