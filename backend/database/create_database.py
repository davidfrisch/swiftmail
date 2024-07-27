from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from models import Base

engine = create_engine('sqlite:///sqlalchemy_example.db')
Base.metadata.create_all(engine) 