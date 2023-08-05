from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, Unicode, Date, ForeignKey
from sqlalchemy.orm import sessionmaker, scoped_session,  relation

from wsmeext.sqlalchemy.types import generate_types, Base

engine = create_engine('sqlite:///C:\\Users\\NMQAFLEET\\Desktop\\database.db',  echo=True)
DBSession = scoped_session(sessionmaker(autocommit=False,
                                      autoflush=False,
                                      bind=engine))

DBBase = declarative_base()

class Customer(DBBase):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True)
    forename = Column(Unicode(50))
    surname = Column(Unicode(50))

    def __init__(self, fname, sname):
        self.forename = forename
        self.surname = surname

DBBase.metadata.create_all(DBSession.bind)