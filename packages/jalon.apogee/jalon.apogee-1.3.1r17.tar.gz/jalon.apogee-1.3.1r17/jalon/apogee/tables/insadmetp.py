# -*- coding: utf-8 -*-

from versionetape import VersionEtape
from individu import Individu

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, Boolean, DateTime, TIMESTAMP, ForeignKey
from sqlalchemy import Text, Float, ForeignKey, Sequence
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy

Base = declarative_base()

class InsAdmEtp(Base):
    __tablename__ = "ins_adm_etp"

    VV_COD_ETP = Column(String(6), primary_key=True)
    COD_VRS_VET = Column(Integer, primary_key=True)
    COD_ETP = Column(String(6), ForeignKey(VersionEtape.COD_ETP))
    VV_COD_IND = Column(Integer)
    COD_IND = Column(Integer, ForeignKey(Individu.COD_IND))
    COD_ANU = Column(String(4))

    V_COD_ETP = relationship(VersionEtape, backref=backref('ins_adm_etp', order_by=VV_COD_ETP))
    V_COD_IND = relationship(Individu, backref=backref('ins_adm_etp', order_by=VV_COD_IND))
    
    def __init__(self, COD_ETP=None, COD_VRS_VET=None):
        self.COD_ETP = COD_ETP
        self.COD_VRS_VET = COD_VRS_VET

    def __repr__(self):
        return "<InsAdmEtp COD_ETP=%d COD_VRS_VET=%s>" % (self.COD_ETP, self.COD_VRS_VET)