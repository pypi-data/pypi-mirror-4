# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text

Base = declarative_base()


class VersionEtape(Base):
    __tablename__ = "version_etape"

    COD_ETP = Column(String(6), primary_key=True)
    COD_VRS_VET = Column(Integer, primary_key=True)
    LIB_WEB_VET = Column(String(120))

    def __init__(self, COD_ETP=None, COD_VRS_VET=None):
        self.COD_ETP = COD_ETP
        self.COD_VRS_VET = COD_VRS_VET

    def __repr__(self):
        return "<VersionEtape COD_ETP=%d COD_VRS_VET=%s>" % (self.COD_ETP, self.COD_VRS_VET)

