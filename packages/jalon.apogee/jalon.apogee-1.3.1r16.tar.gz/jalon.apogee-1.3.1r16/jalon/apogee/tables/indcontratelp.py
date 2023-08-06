# -*- coding: utf-8 -*-

from versionetape import VersionEtape
from elementpedagogi import ElementPedagogi

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship, backref

Base = declarative_base()


class IndContratElp(Base):
    __tablename__ = "ind_contrat_elp"

    VV_COD_ETP = Column(String(6), primary_key=True)
    VV_COD_ELP = Column(String(8))
    COD_VRS_VET = Column(Integer)
    COD_IND = Column(Integer)
    COD_ANU = Column(String(4))
    COD_LSE = Column(String(8))
    COD_ETP = Column(String(6), ForeignKey(VersionEtape.COD_ETP))
    COD_ELP = Column(String(8), ForeignKey(ElementPedagogi.COD_ELP))

    V_COD_ETP = relationship(VersionEtape, backref=backref('ind_contrat_elp', order_by=VV_COD_ETP))
    V_COD_ELP = relationship(ElementPedagogi, backref=backref('ind_contrat_elp', order_by=VV_COD_ELP))

    def __init__(self, COD_ETP=None, COD_VRS_VET=None, COD_ELP=None):
        self.COD_ETP = COD_ETP
        self.COD_VRS_VET = COD_VRS_VET
        self.COD_ELP = COD_ELP

    def __repr__(self):
        return "<IndContratElp COD_ETP=%d COD_VRS_VET=%s COD_ELP=%s>" % (self.COD_ETP, self.COD_VRS_VET, self.COD_ELP)


class IndContratElpSQLITE(Base):
    __tablename__ = "ind_contrat_elp_lite"

    SESAME_ETU = Column(Text, primary_key=True)
    COD_ELP = Column(Text, primary_key=True)
    COD_ELP_PERE = Column(Text, primary_key=True)
    TYPE_ELP = Column(Text)

    def __init__(self, SESAME_ETU=None, COD_ELP=None, TYPE_ELP=None, COD_ELP_PERE=None):
        self.SESAME_ETU = SESAME_ETU
        self.COD_ELP = COD_ELP
        self.TYPE_ELP = TYPE_ELP
        self.COD_ELP_PERE = COD_ELP_PERE

    def __repr__(self):
        return "<IndContratElp SESAME_ETU=%s COD_ELP=%s TYPE_ELP=%s>" % (self.SESAME_ETU, self.COD_ELP, self.TYPE_ELP)
