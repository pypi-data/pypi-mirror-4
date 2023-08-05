import sys
import os
import errno
import xml.etree.ElementTree as ET

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date


Base = declarative_base()


"""This module illustrates how to write your docstring in OpenAlea
and other projects related to OpenAlea."""


class Stock(Base):
    """A generic Stock class."""
    __tablename__ = 'stocks'

    id = Column(Integer, primary_key=True)
    data = Column(Date)
    codneg = Column(String)
    nomres = Column(String)

    def __init__(self, data, codneg):
        self.data = data
        self.codneg = codneg

    def __str__(self):
        return "%s %s" % (self.data, self.codneg)


    def __repr__(self):
        return "<Stock('%s','%s')>" % (self.data, self.codneg)
