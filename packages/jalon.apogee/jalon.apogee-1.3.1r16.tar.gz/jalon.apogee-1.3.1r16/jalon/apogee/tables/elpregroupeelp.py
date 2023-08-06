# -*- coding: utf-8 -*-

from elementpedagogi import ElementPedagogi, ElementPedagogiSQLITE

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, ForeignKey, Text, Integer
from sqlalchemy.orm import relationship, backref

Base = declarative_base()


class ElpRegroupeElp(Base):
    __tablename__ = "elp_regroupe_elp"

    VV_COD_ELP_FILS = Column(String(8), primary_key=True)
    COD_LSE = Column(String(8))
    ETA_LSE = Column(String(1))
    COD_ELP_PERE = Column(String(8))
    COD_ELP_FILS = Column(String(8), ForeignKey(ElementPedagogi.COD_ELP))

    V_COD_ELP_FILS = relationship(ElementPedagogi, backref=backref('elp_regroupe_elp', order_by=VV_COD_ELP_FILS))

    def __init__(self, COD_ELP_FILS=None, ETA_LSE=None):
        self.COD_ELP_FILS = COD_ELP_FILS
        self.ETA_LSE = ETA_LSE

    def __repr__(self):
        return "<ElpRegroupeElp COD_ELP_FILS=%d ETA_LSE=%s>" % (self.COD_ETP_FILS, self.ETA_LSE)


class ETPRegroupeELPSQLITE(Base):
    __tablename__ = "etp_regroupe_elp_lite"

    PKEY = Column(Integer, primary_key=True, autoincrement=True)
    COD_ELP_PERE = Column(Text, ForeignKey(ElementPedagogiSQLITE.COD_ELP))
    COD_ELP_FILS = Column(Text, ForeignKey(ElementPedagogiSQLITE.COD_ELP))
    TYP_ELP = Column(Text)

    def __init__(self, COD_ELP_PERE=None, COD_ELP_FILS=None, TYP_ELP=None):
        self.COD_ELP_PERE = COD_ELP_PERE
        self.COD_ELP_FILS = COD_ELP_FILS
        self.TYP_ELP = TYP_ELP

    def __repr__(self):
        return "<ElpRegroupeElp COD_ELP_PERE=%s COD_ELP_FILS=%s TYP_ELP=%s>" % (self.COD_ELP_PERE, self.COD_ELP_FILS, self.TYP_ELP)
