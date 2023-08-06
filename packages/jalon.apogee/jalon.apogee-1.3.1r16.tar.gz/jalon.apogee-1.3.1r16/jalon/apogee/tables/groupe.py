# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text

Base = declarative_base()


class Groupe(Base):
    __tablename__ = "groupe"

    COD_GPE = Column(Integer, primary_key=True)
    COD_EXT_GPE = Column(String(10))
    LIB_GPE = Column(String(40))

    def __init__(self, COD_GPE=None, COD_EXT_GPE=None, LIB_GPE=None):
        self.COD_GPE = COD_GPE
        self.COD_EXT_GPE = COD_EXT_GPE
        self.LIB_GPE = LIB_GPE

    def __repr__(self):
        return "<Groupe COD_GPE=%s COD_EXT_GPE=%s LIB_GPE=%s>" % (self.COD_GPE, self.COD_EXT_GPE, self.LIB_GPE)
