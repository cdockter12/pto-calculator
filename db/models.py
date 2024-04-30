from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, DateTime, Boolean, Column, Float
from sqlalchemy.orm import backref

db = SQLAlchemy()


class Users(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    is_senior = Column(Integer, nullable=False, default=0)


class Pto(db.Model):
    __tablename__ = "pto"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey("users.id"))
    # This sets up a foreign key relationship with our users.
    user = db.relationship("Users", backref=backref("pto"))
    pto_balance = Column(Float, nullable=False, default=0)
    last_updated = Column(DateTime, nullable=False)
    is_current = Column(Boolean, nullable=False, default=False)
