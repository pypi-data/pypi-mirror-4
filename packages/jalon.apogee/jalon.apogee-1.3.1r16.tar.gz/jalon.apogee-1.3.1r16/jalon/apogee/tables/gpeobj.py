# -*- coding: utf-8 -*-

from groupe import Groupe

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, Boolean, DateTime, TIMESTAMP, ForeignKey
from sqlalchemy import Text, Float, ForeignKey, Sequence
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy

Base = declarative_base()

class GpeObj(Base):
    __tablename__ = "gpe_obj"

    COD_GPO = Column(Integer, primary_key=True)
    VV_COD_GPE = Column(Integer)
    COD_ELP = Column(String(8))
    COD_ETP = Column(String(6))
    COD_VRS_VET = Column(Integer)
    TYP_OBJ_GPO = Column(String(3))
    COD_GPE = Column(Integer, ForeignKey(Groupe.COD_GPE))

    V_COD_GPE = relationship(Groupe, backref=backref('gpe_obj', order_by=VV_COD_GPE))

    def __init__(self, COD_GPO=None, COD_GPE=None):
        self.COD_GPO = COD_GPO
        self.COD_GPE = COD_GPE

    def __repr__(self):
        return "<GpeObj COD_GPO=%d COD_GPE=%d>" % (self.COD_GPO, self.COD_GPE)