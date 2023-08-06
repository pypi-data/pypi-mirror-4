# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text

Base = declarative_base()


class Individu(Base):
    __tablename__ = "individu"

    COD_IND = Column(Integer, primary_key=True)
    DATE_NAI_IND = Column(String(10))
    LIB_NOM_PAT_IND = Column(String(30))
    LIB_NOM_USU_IND = Column(String(30))
    LIB_PR1_IND = Column(String(20))
    COD_ETU = Column(Integer)
    LIB_VIL_NAI_ETU = Column(String(20))

    def __init__(self, COD_IND=None):
        self.COD_IND = COD_IND

    def __repr__(self):
        return "<Individu COD_IND=%s>" % str(self.COD_IND)


class IndividuSQLITE(Base):
    __tablename__ = "individu_lite"

    SESAME_ETU = Column(Text, primary_key=True)
    DATE_NAI_IND = Column(Text)
    LIB_NOM_PAT_IND = Column(Text)
    LIB_NOM_USU_IND = Column(Text)
    LIB_PR1_IND = Column(Text)
    COD_ETU = Column(Integer)
    EMAIL_ETU = Column(Text)

    def __init__(self, SESAME_ETU=None, COD_ETU=0, LIB_NOM_PAT_IND=None, LIB_PR1_IND=None):
        self.SESAME_ETU = SESAME_ETU
        self.COD_ETU = COD_ETU
        self.LIB_NOM_PAT_IND = LIB_NOM_PAT_IND
        self.LIB_PR1_IND = LIB_PR1_IND

    def __repr__(self):
        return "<Individu SESAME_ETU=%s COD_ETU=%s LIB_NOM_PAT_IND=%s LIB_PR1_IND=%s>" % (self.COD_IND, str(self.COD_ETU), self.LIB_NOM_PAT_IND, self.LIB_PR1_IND)
