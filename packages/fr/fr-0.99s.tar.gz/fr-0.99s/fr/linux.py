import os, locale
from os.path import basename
from fr.utils import Info, run

devfilter   = ('none', 'tmpfs', 'udev')
diskcmd     = '/bin/df --portability'
memfname    = '/proc/meminfo'
coloravail  = True
encoding    = 'utf8'
col_lblw    = 'MOUNT CACHE'
col_lbls    = 'MNT CACHE'

if os.environ.get('TERM') == 'linux':  # to ascii
    _ramico         = 'r'
    _diskico        = 'd'
    _unmnico        = 'u'
    _remvico        = 'm'
    _netwico        = 'n'
    _discico        = 'o'
    _emptico        = '0'
    _ellpico        = '>'
    _usedico        = '#'
    _freeico        = '='
    _brckico        = ('|', '|')
locale.setlocale(locale.LC_ALL, '')

try:
    import dbus
    dbus_api = 'org.freedesktop.UDisks'
    dbus_dev = 'org.freedesktop.UDisks.Device'
except ImportError:
    dbus = None


def get_diskinfo(outunit, show_all=False, debug=False):
    ''' Returns a list holding the current disk info,
        divided by the ouptut unit.

        Udisks doesn't provide free/used info, so it is currently gathered
        via the df command.
    '''
    disks = {}
    try:
        lines = run(diskcmd).splitlines()[1:]  # dump header
        for i, line in enumerate(lines):
            if line:
                tokens  = line.split()
                dev = basename(tokens[0])
                disk = Info()
                disk.isram  = None
                if dev in devfilter:
                    if show_all:
                        dev += str(i)
                        disk.isram = True
                    else:
                        disk.isram = False; continue
                disk.dev = dev
                # convert to bytes, then output units
                disk.ocap   = float(tokens[1]) * 1024
                disk.cap    = disk.ocap / outunit
                disk.free   = float(tokens[3]) * 1024 / outunit
                disk.label  = '' # dummy values for now
                disk.mntp   = ' '.join( tokens[5:] )
                disk.pcnt   = int(tokens[4][:-1])
                disk.used   = float(tokens[2]) * 1024 / outunit
                disk.ismntd = True
                disk.isnet  = None
                disk.isopt  = None
                disk.isrem  = None
                disk.rw     = True

                disks[dev] = disk
    except IOError:
        return None

    if dbus:  # request volume details, add to disks
        try:
            bus = dbus.SystemBus() # Get on the bus... and pay your fare...
            udisks = bus.get_object(dbus_api, '/' + dbus_api.replace('.','/'))
            udisks = dbus.Interface(udisks, 'org.freedesktop.UDisks')

            for devpath in udisks.EnumerateDevices():
                devobj = bus.get_object(dbus_api, devpath)
                devobj = dbus.Interface(devobj, dbus.PROPERTIES_IFACE)

                lbl = unicode(devobj.Get(dbus_dev, 'IdLabel'))
                ismntd = bool(devobj.Get(dbus_dev, 'DeviceIsMounted'))
                ispart = devobj.Get(dbus_dev, 'DeviceIsPartition')
                dtype = devobj.Get(dbus_dev, 'IdType')
                ptype = devobj.Get(dbus_dev, 'PartitionType')
                psize = devobj.Get(dbus_dev, 'PartitionSize')
                isopt = bool(devobj.Get(dbus_dev, 'DeviceIsOpticalDisc'))
                #~ isrem = devobj.Get(dbus_dev, 'DeviceIsRemovable')
                isrem = not devobj.Get(dbus_dev, 'DeviceIsSystemInternal')
                if debug:
                    print devpath, dtype, ptype, psize, isrem, isopt, ispart

                rw = False
                if ismntd:
                    firstmnt = devobj.Get(dbus_dev, 'DeviceMountPaths')[0]
                    if firstmnt == '/':   rw = True
                    else:                 rw = os.access(firstmnt, os.W_OK)

                if ispart or isopt:
                    dev = basename(devpath)
                    if ismntd:
                        thisone = dict(dev=dev, label=lbl, rw=rw,
                                       ismntd=ismntd, isopt=isopt, isrem=isrem,
                                       isram=False)
                        if dev in disks:
                            disks[dev].update(thisone)
                        else:
                            disks[dev] = Info(**thisone)

                        disks[dev].setdefault('mntp', '')
                        disks[dev].setdefault('pcnt', 0)
                    else:
                        if show_all:
                            if dtype != 'swap' and ptype != '0x05': # extended part.
                                disk = Info(dev=dev, cap=0, used=0, free=0,
                                        pcnt=0, ocap=0, mntp='', label=lbl,
                                        rw=rw, ismntd=ismntd, isrem=isrem,
                                        isopt=isopt, isram=0, isnet=0)
                                disks[dev] = disk

        except dbus.exceptions.DBusException, e:
            if 'ServiceUnknown' in str(e):
                print ' Warning: Udisks not found.',
            else:
                raise

    if debug:  print disks
    keys = sorted(disks.keys())
    return [ disks[dev]  for dev in keys ]


def get_meminfo(outunit, debug=False):
    ''' Returns a dictionary holding the current memory info,
        divided by the ouptut unit.  If mem info can't be read, returns None.
    '''
    meminfo = Info()
    if os.access(memfname, os.R_OK):
        memf = file(memfname, 'r')
    else:
        return None

    for line in memf:  # format: 'MemTotal:  511456 kB\n'
        tokens = line.split()
        if tokens:
            name, value = tokens[0][:-1], tokens[1]  # rm :
            if len(tokens) > 2:
                unit = tokens[2].lower()
            # parse_result to bytes
            value = int(value)
            if   unit == 'kb': value = value * 1024  # most likely
            elif unit ==  'b': value = value
            elif unit == 'mb': value = value * 1024 * 1024
            elif unit == 'gb': value = value * 1024 * 1024 * 1024
            setattr(meminfo, name, value / float(outunit))

    cach = meminfo.Cached + meminfo.Buffers
    meminfo.Used = meminfo.MemTotal - meminfo.MemFree - cach
    meminfo.SwapUsed = (meminfo.SwapTotal - meminfo.SwapCached -
                        meminfo.SwapFree)
    return meminfo

