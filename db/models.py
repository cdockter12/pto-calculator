from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, DateTime, Boolean, Column, Float
from sqlalchemy.orm import backref

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    is_senior = Column(Boolean, nullable=False)


class Pto(db.Model):
    __tablename__ = "pto"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey("user.id"))
    # This sets up a foreign key relationship with our users.
    user = db.relationship("User", backref=backref("pto", lazy="dynamic"))
    current_pto_balance = Column(Float, nullable=False, default=0)
    last_updated = Column(DateTime, nullable=False)
    is_current = Column(Boolean, nullable=False, default=False)
