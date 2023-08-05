#!/usr/bin/python
#dhntester.py

import os
import sys

import time

if __name__ == "__main__":
    dirpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    sys.path.insert(0, os.path.abspath('datahaven'))
    sys.path.insert(0, os.path.abspath(os.path.join(dirpath, '..')))
    sys.path.insert(0, os.path.abspath(os.path.join(dirpath, '..', '..')))

try:
    import lib.dhnio as dhnio
    ##import dhnio.DprintStd, ReadBinaryFile, _read_dict, _dir_remove, SetDebug, LowerPriority
    from lib.dhnpacket import Unserialize
    from lib.nameurl import FilenameUrl
    from lib.settings import init as settings_init
    from lib.settings import CustomersSpaceFile, getCustomersFilesDir, LocalTesterLogFilename
    from lib.contacts import init as contacts_init
    from lib.commands import init as commands_init
except:
    import traceback
    logfile = open('dhntester.log', 'a')
    traceback.print_exc(file=logfile)
    logfile.close()
    sys.exit(2)

# need to make sure the dhntester log is in a directory the user has permissions for,
# such as the customer data directory.  Possibly move to temp directory?
# myoutput = open(LocalTesterLogFilename(), 'w')
# sys.stdout = myoutput
# sys.stderr = myoutput

#-------------------------------------------------------------------------------
#test all packets for each customer.
#check if he use more space than we gave him and if packets is too old.
def SpaceTime():
    dhnio.DprintStd(2, 'dhntester.SpaceTime ' + str(time.strftime("%a, %d %b %Y %H:%M:%S +0000")))
    space = dhnio._read_dict(CustomersSpaceFile())
    if space is None:
        dhnio.DprintStd(2, 'dhntester.SpaceTime ERROR can not read file ' + CustomersSpaceFile())
        return
    customers_dir = getCustomersFilesDir()
    if not os.path.exists(customers_dir):
        dhnio.DprintStd(2, 'dhntester.SpaceTime ERROR customers folder not exist')
        return

    remove_list = {}
    for customer_filename in os.listdir(customers_dir):
        onecustdir = os.path.join(customers_dir, customer_filename)
        if not os.path.isdir(onecustdir):
            remove_list[onecustdir] = 'is not a folder'
            continue
        idurl = FilenameUrl(customer_filename)
        if idurl is None:
            remove_list[onecustdir] = 'wrong folder name'
            continue
        curspace = space.get(idurl, None)
        if curspace is None:
            continue
        try:
            maxspaceV = float(curspace) * 1024 * 1024 #in bytes
        except:
            remove_list[onecustdir] = 'wrong space value'
            continue

        timedict = {}
        sizedict = {}
        for filename in os.listdir(onecustdir):
            path = os.path.join(onecustdir, filename)
            if not os.path.isfile(path):
                continue
            stats = os.stat(path)
            timedict[path] = stats.st_ctime
            sizedict[path] = stats.st_size

        timelist = timedict.keys()
        currentV = 0
        for path in sorted( timelist, key=lambda x:timedict[x], reverse=True ):
            currentV += sizedict.get(path, 0)
            if currentV < maxspaceV:
                continue
            try:
                os.remove(path)
                dhnio.DprintStd(4, 'dhntester.SpaceTime ' + path + ' removed (current %s/ maximum %s)' % (str(currentV), str(maxspaceV)) )
            except:
                dhnio.DprintStd(4, 'dhntester.SpaceTime ERROR removing ' + path)

            time.sleep(0.1)
        del timelist
        timedict.clear()
        sizedict.clear()

    for path in remove_list.keys():
        if not os.path.exists(path):
            continue
        if os.path.isdir(path):
            try:
                dhnio._dir_remove(path)
                dhnio.DprintStd(4, 'dhntester.SpaceTime ' + path + ' removed (%s)' % (remove_list[path]))
            except:
                dhnio.DprintStd(4, 'dhntester.SpaceTime ERROR removing ' + path)
            continue
        if not os.access(path, os.W_OK):
            os.chmod(path, 0600)
        try:
            os.remove(path)
            dhnio.DprintStd(4, 'dhntester.SpaceTime ' + path + ' removed (%s)' % (remove_list[path]))
        except:
            dhnio.DprintStd(4, 'dhntester.SpaceTime ERROR removing ' + path)

    del remove_list

#------------------------------------------------------------------------------
#test packets after list of customers was changed
def UpdateCustomers():
    dhnio.DprintStd(2, 'dhntester.UpdateCustomers ' + str(time.strftime("%a, %d %b %Y %H:%M:%S +0000")))
    space = dhnio._read_dict(CustomersSpaceFile())
    if space is None:
        dhnio.DprintStd(2, 'dhntester.UpdateCustomers ERROR space file can not read' )
        return
    customers_dir = getCustomersFilesDir()
    if not os.path.exists(customers_dir):
        dhnio.DprintStd(2, 'dhntester.UpdateCustomers ERROR customers folder not exist')
        return

    remove_list = {}
    for customer_filename in os.listdir(customers_dir):
        onecustdir = os.path.join(customers_dir, customer_filename)
        if not os.path.isdir(onecustdir):
            remove_list[onecustdir] = 'is not a folder'
            continue
        idurl = FilenameUrl(customer_filename)
        if idurl is None:
            remove_list[onecustdir] = 'wrong folder name'
            continue
        curspace = space.get(idurl, None)
        if curspace is None:
            remove_list[onecustdir] = 'is not a customer'
            continue

    for path in remove_list.keys():
        if not os.path.exists(path):
            continue
        if os.path.isdir(path):
            try:
                dhnio._dir_remove(path)
                dhnio.DprintStd(4, 'dhntester.UpdateCustomers ' + path + ' removed (%s)' % (remove_list[path]))
            except:
                dhnio.DprintStd(4, 'dhntester.UpdateCustomers ERROR removing ' + path)
            continue
        if not os.access(path, os.W_OK):
            os.chmod(path, 0600)
        try:
            os.remove(path)
            dhnio.DprintStd(4, 'dhntester.UpdateCustomers ' + path + ' removed (%s)' % (remove_list[path]))
        except:
            dhnio.DprintStd(4, 'dhntester.UpdateCustomers ERROR removing ' + path)

#------------------------------------------------------------------------------
#check all packets to be valid
def Validate():
    dhnio.DprintStd(2, 'dhntester.Validate ' + str(time.strftime("%a, %d %b %Y %H:%M:%S +0000")))
    contacts_init()
    commands_init()

    customers_dir = getCustomersFilesDir()
    if not os.path.exists(customers_dir):
        return
    for customer_filename in os.listdir(customers_dir):
        onecustdir = os.path.join(customers_dir, customer_filename)
        if not os.path.isdir(onecustdir):
            continue
        for filename in os.listdir(onecustdir):
            path = os.path.join(onecustdir, filename)
            if not os.path.isfile(path):
                continue

            packetsrc = dhnio.ReadBinaryFile(path)
            packet = Unserialize(packetsrc)
            result = packet.Valid()
            packetsrc = ''
            del packet

            if not result:
                try:
                    os.remove(path) # if is is no good it is of no use to anyone
                    dhnio.DprintStd(4, 'dhntester.Validate ' + path + ' removed (invalid packet)')
                except:
                    dhnio.DprintStd(4, 'dhntester.Validate ERROR removing ' + path)

            time.sleep(0.1)

#------------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        return

    settings_init()

    dhnio.OpenLogFile(LocalTesterLogFilename(), True)
        
    dhnio.StdOutRedirectingStart()

    dhnio.LifeBegins()

    dhnio.SetDebug(0)

    dhnio.InstallLocale()

    dhnio.SetDebug(4)

    commands = {
        'update_customers' : UpdateCustomers,
        'validate' : Validate,
        'space_time' : SpaceTime,
    }

    cmd = commands.get(sys.argv[1], None)

    if not cmd:
        dhnio.DprintStd(2, 'dhntester.main ERROR wrong command')
        return

    dhnio.LowerPriority()

    cmd()

    dhnio.StdOutRedirectingStop()
    
    dhnio.CloseLogFile()

#------------------------------------------------------------------------------ 

if __name__ == "__main__":
    main()






