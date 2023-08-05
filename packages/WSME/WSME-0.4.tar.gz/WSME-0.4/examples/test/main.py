import logging

import bottle

from wsmeext.sqlalchemy.types import Base
from wsme import expose, validate, WSRoot

import models

DBSession = models.DBSession

class Customer(Base):
    __saclass__ = models.Customer

class CustomerController(object):
    __dbsession__ = DBSession
    __datatype__ = Customer

    @expose(Customer)
    @validate(Customer)
    def create(self, data):
        customer = Customer()
        customer.forename = data.forename
        customer.surname = data.surname
        DBSession.add(customer)
        try:
            DBSession.commit()
            return Customer(customer)
        except:
            print "Failure"

class MainRoot(WSRoot):
    customer = CustomerController()

root = MainRoot(webpath='/ws')

root.addprotocol('soap',
        tns='http://example.com/demo',
        typenamespace='http://example.com/demo/types',
        baseURL='http://localhost:8080/ws/',
)

bottle.mount('/ws/', root.wsgiapp())

logging.basicConfig(level=logging.DEBUG)
bottle.run()
