#!/usr/bin/python
#contacts.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    All rights reserved.
#
#  We only talk with limited sets of people and in limited ways for each type:
#   1)  datahaven.net    - central command
#   2)  supplierids      - ids for nodes who supply us with storage services (customerservice.py stuff)
#   3)  customerids      - ids for nodes we provide customerservice.py stuff for
#   4)  scrubberids      - only activated for customers who are offline more than 30 hours (or something)
#                             Rights the same as that customer number they scrub for
#   5)  correspondentids - ids for people we accept messages from
#
#  We keep around URLIDs and Identities for each.
#  We can get all the info from datahaven.net
#
#  We get a list of customers and suppliers from datahaven.net
#  We have to get an identity record for each of these contacts.
#  We have to record bandwidth between us and each contact for
#    each 24 hour period.
#  We have to report bandwidth sometime in the following 24 hour period.
#  From User/GUI or backup_monitor.py we might replace one contact at a time.
#


import os
import string
import sys


import settings
import dhnio
import misc
import contactsdb
import identitydb
import nameurl


#-------------------------------------------------------------------------------

_SuppliersChangedCallback = None
_CustomersChangedCallback = None
_ContactsChangedCallback = None
_CorrespondentsChangedCallback = None

#------------------------------------------------------------------------------ 

#  We read from disk and if we have all the info we are set.
#  If we don't have enough, then we have to ask DHN to listcontacts and use
#  that list to get and then store all the identities for our contacts.
def init():
    dhnio.Dprint(4, "contacts.init ")
    contactsdb.load_suppliers(settings.SupplierIDsFilename())
    contactsdb.load_customers(settings.CustomerIDsFilename())
    contactsdb.load_correspondents(settings.CorrespondentIDsFilename())
    contactsdb.add_correspondent(misc.getLocalID())

#------------------------------------------------------------------------------ 

def SetSuppliersChangedCallback(cb):
    global _SuppliersChangedCallback
    _SuppliersChangedCallback = cb

def SetCustomersChangedCallback(cb):
    global _CustomersChangedCallback
    _CustomersChangedCallback = cb

def SetContactsChangedCallback(cb):
    global _ContactsChangedCallback
    _ContactsChangedCallback = cb

def SetCorrespondentsChangedCallback(cb):
    global _CorrespondentsChangedCallback
    _CorrespondentsChangedCallback = cb

#-------------------------------------------------------------------------------

#  Sometimes we want to loop through all the IDs we make contact with
def getContactIDs():
    return contactsdb.contacts()

def IsCustomer(custid):
    return contactsdb.is_customer(custid)

def IsSupplier(supid):
    return contactsdb.is_supplier(supid)

def numSuppliers():
    return contactsdb.num_suppliers()

def numCustomers():
    return contactsdb.num_customers()

def getSupplierIDs():
    return contactsdb.suppliers()

def getCustomerIDs():
    return contactsdb.customers()

def getCustomerNames():
    return map(nameurl.GetName, contactsdb.customers())

def setSupplierIDs(idslist):
    global _SuppliersChangedCallback
    global _ContactsChangedCallback
    oldsuppliers = contactsdb.suppliers()
    oldcontacts = contactsdb.contacts()
    contactsdb.set_suppliers(idslist)
    if _SuppliersChangedCallback is not None:
        _SuppliersChangedCallback(oldsuppliers, contactsdb.suppliers())
    if _ContactsChangedCallback is not None:
        _ContactsChangedCallback(oldcontacts, contactsdb.contacts())

def setCustomerIDs(idslist):
    global _CustomersChangedCallback
    global _ContactsChangedCallback
    oldcustomers = contactsdb.customers()
    oldcontacts = contactsdb.contacts()
    contactsdb.set_customers(idslist)
    if _CustomersChangedCallback is not None:
        _CustomersChangedCallback(oldcustomers, contactsdb.customers())
    if _ContactsChangedCallback is not None:
        _ContactsChangedCallback(oldcontacts, contactsdb.contacts())

def getCorrespondentIDs():
    return contactsdb.correspondents()

def getContactsAndCorrespondents():
    return contactsdb.contacts_full()

def getRemoteContacts():
    allcontacts = getContactsAndCorrespondents()
    if misc.getLocalID() in allcontacts:
        allcontacts.remove(misc.getLocalID())
    return allcontacts

def getSupplierID(N):
    return contactsdb.supplier(N)

# Suppliers should be numbered 0 to 63 with customers after that
def getSupplierN(N):
    return identitydb.get(getSupplierID(N))

def getSupplier(ID):
    if contactsdb.is_supplier(ID):
        return identitydb.get(ID)
    return ''

def getCorrespondent(ID):
    if contactsdb.is_correspondent(ID):
        return identitydb.get(ID)
    if ID in [settings.CentralID(), settings.MoneyServerID()]:
        return identitydb.get(ID) 
    return ''

def isKnown(idurl):
    if idurl == settings.CentralID():
        return True
    if idurl == settings.MoneyServerID():
        return True
    if contactsdb.is_supplier(idurl):
        return True
    if contactsdb.is_customer(idurl):
        return True
    if contactsdb.is_correspondent(idurl):
        return True
    return False
    
# Suppliers should be numbered 0 to 63 with customers after that 
# not sure we can count on numbers staying
def numberForContact(idurl):
    return contactsdb.contact_index(idurl)

def numberForCustomer(idurl):
    return contactsdb.customer_index(idurl)

def numberForSupplier(idurl):
    return contactsdb.supplier_index(idurl)

def getCustomerIndex(idurl):
    return contactsdb.customer_index(idurl)

def addCustomer(idurl):
    global _CustomersChangedCallback
    global _ContactsChangedCallback
    oldcustomers = contactsdb.customers()
    oldcontacts = contactsdb.contacts()
    res = contactsdb.add_customer(idurl)
    if _CustomersChangedCallback is not None:
        _CustomersChangedCallback(oldcustomers, contactsdb.customers())
    if _ContactsChangedCallback is not None:
        _ContactsChangedCallback(oldcontacts, contactsdb.contacts())
    return res

def getCustomerID(N):
    return contactsdb.customer(N)

def getCustomerN(N):
    return identitydb.get(contactsdb.customer(N))

# Only valid contacts for dhnpackets will be signed by localidentity, suppliers, customers
# and eventually dhn central command - PREPRO
def getContact(idurl):
    if idurl is None:
        return None
    if idurl == misc.getLocalID():
        return misc.getLocalIdentity()
    if idurl == settings.CentralID():
        return identitydb.get(idurl)
    if idurl == settings.MoneyServerID():
        return identitydb.get(idurl)
    if contactsdb.is_supplier(idurl):
        return identitydb.get(idurl)
    if contactsdb.is_customer(idurl):
        return identitydb.get(idurl)
    if contactsdb.is_correspondent(idurl):
        return identitydb.get(idurl)
    if identitydb.has_key(idurl):
        # dhnio.Dprint(2, "contacts.getContact WARNING who is %s ?" % nameurl.GetName(idurl))
        return identitydb.get(idurl)
    dhnio.Dprint(2, "contacts.getContact WARNING %s not found!" % nameurl.GetName(idurl))
    return None

#------------------------------------------------------------------------------ 

def saveCustomerIDs():
    contactsdb.save_customers(settings.CustomerIDsFilename())

def saveSupplierIDs():
    contactsdb.save_suppliers(settings.SupplierIDsFilename())
    
def saveCorrespondentIDs():
    contactsdb.save_correspondents(settings.CorrespondentIDsFilename())

#-------------------------------------------------------------------------------

def addCorrespondent(idurl):
    return contactsdb.add_correspondent(idurl)
    
def removeCorrespondent(idurl):
    return contactsdb.remove_correspondent(idurl)

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    init()




