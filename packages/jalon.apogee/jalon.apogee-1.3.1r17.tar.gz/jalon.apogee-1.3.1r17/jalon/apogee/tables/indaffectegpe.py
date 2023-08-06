# -*- coding: utf-8 -*-

from groupe import Groupe

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, Boolean, DateTime, TIMESTAMP, ForeignKey
from sqlalchemy import Text, Float, ForeignKey, Sequence
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy

Base = declarative_base()

class IndAffecteGpe(Base):
    __tablename__ = "ind_affecte_gpe"

    VV_COD_GPE = Column(Integer, primary_key=True)
    COD_IND = Column(Integer)
    COD_ANU = Column(String(4))
    COD_GPE = Column(Integer, ForeignKey(Groupe.COD_GPE))

    V_COD_GPE = relationship(Groupe, backref=backref('ind_affecte_gpe', order_by=VV_COD_GPE))

    def __init__(self, COD_GPE=None, COD_IND=None):
        self.COD_GPE = COD_GPE
        self.COD_IND = COD_IND

    def __repr__(self):
        return "<IndAffecteGpe COD_GPE=%d COD_IND=%s>" % (self.COD_GPE, self.COD_IND)