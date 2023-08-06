# -*- coding: utf-8 -*-

from versionetape import VersionEtape

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, Boolean, DateTime, TIMESTAMP, ForeignKey
from sqlalchemy import Text, Float, ForeignKey, Sequence
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy

Base = declarative_base()

class VdiFractionnerVet(Base):
    __tablename__ = "vdi_fractionner_vet"

    VV_COD_ETP = Column(String(6), primary_key=True)
    COD_VRS_VET = Column(Integer)
    DAA_FIN_VAL_VET = Column(String(4))
    DAA_FIN_RCT_VET = Column(String(4))
    COD_ETP = Column(String(6), ForeignKey(VersionEtape.COD_ETP))

    V_COD_ETP = relationship(VersionEtape, backref=backref('vdi_fractionner_vet', order_by=VV_COD_ETP))

    def __init__(self, COD_ETP=None, COD_VRS_VET=None):
        self.COD_ETP = COD_ETP
        self.COD_VRS_VET = COD_VRS_VET

    def __repr__(self):
        return "<VdiFractionnerVet COD_ETP=%d COD_VRS_VET=%s>" % (self.COD_ETP, self.COD_VRS_VET)