# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Text, Integer, Boolean

Base = declarative_base()


class ElementPedagogi(Base):
    __tablename__ = "element_pedagogi"

    COD_ELP = Column(String(8), primary_key=True)
    LIB_ELP = Column(String(60))
    ETA_ELP = Column(String(1))

    def __init__(self, COD_ETP=None, COD_VRS_VET=None):
        self.COD_ETP = COD_ETP
        self.COD_VRS_VET = COD_VRS_VET

    def __repr__(self):
        return "<ElementPedagogi COD_ETP=%d COD_VRS_VET=%s>" % (self.COD_ETP, self.COD_VRS_VET)


class ElementPedagogiSQLITE(Base):
    __tablename__ = "element_pedagogi_lite"

    COD_ELP = Column(Text, primary_key=True)
    LIB_ELP = Column(Text)
    TYP_ELP = Column(Text)
    COD_GPE = Column(Text)
    ETU_ELP = Column(Integer)

    def __init__(self, COD_ELP=None, LIB_ELP=None, ETU_ELP=0, UEL_ELP=False):
        self.COD_ELP = COD_ELP
        self.LIB_ELP = LIB_ELP
        self.ETU_ELP = ETU_ELP

    def __repr__(self):
        return "<ElementPedagogi COD_ELP=%d LIB_ELP=%s ETU_ELP=%s UEL_ELP=%s>" % (self.COD_ELP, self.LIB_ELP, str(self.ETU_ELP), str(self.UEL_ELP))
