from sqlalchemy import *
from sqlalchemy.orm import relationship, backref, exc
from sqlalchemy.dialects.mysql import INTEGER as Integer

from rfk.database import Base, UTCDateTime
import rfk.database
from rfk.helper import now
from rfk.types import ENUM

class Statistic(Base):
    __tablename__ = 'statistics'
    statistic = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    identifier = Column(String(50), unique=True,  nullable=False)
    
    def set(self, timestamp, value):
        try:
            ls = StatsistcsData.query.filter(StatsistcsData.timestamp == timestamp,
                                             StatsistcsData.statistic == self).one()
            ls.value = value
            rfk.database.session.flush()
        except exc.NoResultFound:
            ls = StatsistcsData(statistic=self, timestamp=timestamp, value=value)
            rfk.database.session.add(ls)
            rfk.database.session.flush()
            
    def get(self, start=None, stop=None, num=None, reverse=False):
        clauses = []
        if start is not None:
            clauses.append(StatsistcsData.timestamp >= start)
        if stop is not None:
            clauses.append(StatsistcsData.timestamp <= stop)
        clauses.append(StatsistcsData.statistic == self)
        qry = StatsistcsData.query.filter(*clauses)
        if reverse:
            qry = qry.order_by(StatsistcsData.timestamp.desc() )
        else:
            qry = qry.order_by(StatsistcsData.timestamp.asc() )
        if num is not None:
            qry = qry.limit(num)
        return qry.yield_per(100)
        
    def current_value(self):
        ret = self.get(stop=now(), num=1, reverse=True)
        if len(ret) == 1:
            return ret[0]
        else:
            return None


class StatsistcsData(Base):
    __tablename__ = 'statisticsdata'
    stat = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    statistic_id = Column("statistic", Integer(unsigned=True), ForeignKey('statistics.statistic',
                                                                          onupdate="CASCADE",
                                                                          ondelete="RESTRICT"))
    statistic = relationship("Statistic")
    timestamp = Column(UTCDateTime(), nullable=False)
    value = Column(Integer(unsigned=True), nullable=False)
    

class RelayStatistic(Base):
    __tablename__ = 'relay_statistics'
    relaystat = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
    statistic_id = Column("statistic", Integer(unsigned=True), ForeignKey('statistics.statistic',
                                                                          onupdate="CASCADE",
                                                                          ondelete="RESTRICT"))
    statistic = relationship("Statistic")
    relay_id = Column("relay", Integer(unsigned=True), ForeignKey('relays.relay',
                                                                          onupdate="CASCADE",
                                                                          ondelete="RESTRICT"))
    relay = relationship("Relay")    
    type = Column(Integer(unsigned=True))
    TYPE = ENUM(['TRAFFIC', 'LISTENERCOUNT'])
    
    @staticmethod
    def get_relaystatistic(relay, type):
        try:
            return RelayStatistic.query.filter(RelayStatistic.relay == relay, RelayStatistic.type == type).one()
        except exc.NoResultFound:
            s = Statistic(name='{0}:{1}-{2}'.format(relay.address, relay.port, type),
                          identifier='{0}:{1}-{2}'.format(relay.address, relay.port, type))
            rfk.database.session.add(s)
            rs = RelayStatistic(relay=relay, type=type, statistic=s)
            rfk.database.session.add(rs)
            rfk.database.session.flush()
            return rs