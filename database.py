#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: Binux<i@binux.me>
#         http://binux.me
# Created on 2013-01-24 21:29:41

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, UniqueConstraint
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

import utils

Base = declarative_base()

class Portal(Base):
    __tablename__ = 'portal'

    guid = Column(String, primary_key=True)
    uptime = Column(Integer)
    control = Column(String)
    latE6 = Column(Integer)
    lngE6 = Column(Integer)
    level = Column(Integer)
    energy = Column(Integer)
    ignore = Column(Integer, default=0)

    @property
    def latlng(self):
        return utils.LatLng(self.latE6*1e-6, self.lngE6*1e-6)

    def __repr__(self):
        return '<Portal#%s %s+%d @%f,%f>' % (self.guid, self.control, self.level, self.latE6*1e-6, self.lngE6*1e-6)

class GEOCell(Base):
    __tablename__ = 'geo_cell'
    __table_args__ = (
        UniqueConstraint('latE6', 'lngE6', 'cell'),
        {},
    )

    latE6 = Column(Integer, primary_key=True)
    lngE6 = Column(Integer, primary_key=True)
    cell = Column(String, primary_key=True)

engine = create_engine('sqlite:///aio.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
