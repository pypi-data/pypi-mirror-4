'''
    ansilib, a library of common console color functions.
    (C) 2005-12, Mike Miller - Released under the GPL, version 3+.
'''
if True:
    import sys, os

    # A list of ansi escape sequences.
    fred        = '[00;31m%s[00m'
    fbred       = '[01;31m%s[00m'
    fgreen      = '[00;32m%s[00m'
    fbgreen     = '[01;32m%s[00m'
    forange     = '[00;33m%s[00m'
    fbyellow    = '[01;33m%s[00m'
    fblue       = '[00;34m%s[00m'
    fbblue      = '[01;34m%s[00m'
    fpurple     = '[00;35m%s[00m'
    fbpurple    = '[01;35m%s[00m'
    fcyan       = '[00;36m%s[00m'
    fbcyan      = '[01;36m%s[00m'
    fgrey       = '[00;37m%s[00m'
    fwhite      = '[01;37m%s[00m'
    #fgrey       = '[00;38m%s[00m'
    #fwhite      = '[01;38m%s[00m'

    redrev      = '[00;05;37;41m%s[00m'
    grerev      = '[00;05;37;42m%s[00m'
    yelrev      = '[01;05;37;43m%s[00m'

    rev         = '[07m%s[00m'
    fbold       = '[01m%s[00m'
    fdim        = '[02m%s[00m'

    # Readline encoded escape sequences:
    greenprompt  = '\001[01;32m\002%s\001[00m\002'
    yellowprompt = '\001[01;33m\002%s\001[00m\002'
    redprompt    = '\001[01;31m\002%s\001[00m\002'

    #fg
    black       = '30'
    red         = '31'
    green       = '32'
    orange      = '33'
    blue        = '34'
    purple      = '35'
    cyan        = '36'
    grey        = '37'

    #bg
    blackbg     = '40'
    redbg       = '41'
    greenbg     = '42'
    orangebg    = '43'
    bluebg      = '44'
    purplebg    = '45'
    cyanbg      = '46'
    greybg      = '47'

    # misc
    underline   = '38'
    underline   = '48'
    norm        = '00'
    bold        = '01'
    dim         = '02'


def colorstart(fgcolor, bgcolor, weight):
    '''Begin a text style.'''
    if weight:          weight = bold
    else:               weight = norm
    if bgcolor:
        sys.stdout.write('[%s;%s;%sm' % (weight, fgcolor, bgcolor))
    else:
        sys.stdout.write('[%s;%sm' % (weight, fgcolor))


def colorend(cr=False):
    '''End color styles.  Resets to default terminal colors.'''
    sys.stdout.write('[00m')
    if cr: sys.stdout.write('\n')
    sys.stdout.flush()


def cprint(text, fg=grey, bg=blackbg, w=norm, cr=False, encoding='utf8'):
    ''' Print a string in a specified color style and then return to normal.
        def cprint(text, fg=white, bg=blackbg, w=norm, cr=True):
    '''
    colorstart(fg, bg, w)
    sys.stdout.write(text)
    colorend(cr)


def bargraph(data, maxwidth, incolor=True, cbrackets=(u'\u2595', u'\u258F')):
    'Creates a bar graph.'
    threshold = 100.0 / (maxwidth * 2)  # if smaller than 1/2 of one char wide
    position = 0
    begpcnt = data[0][1] * 100
    endpcnt = data[-1][1] * 100

    if len(data) < 1: return        # Nada to do
    maxwidth = maxwidth - 2         # because of brackets
    datalen = len(data)

    # Print left bracket in correct color:
    if cbrackets and incolor: # and not (begpcnt == 0 and endpcnt == 0):
        if begpcnt < threshold: lbkcolor = data[-1][2]  # greenbg
        else:                   lbkcolor = data[0][2]   # redbg
        cprint(cbrackets[0], data[0][2], lbkcolor, None, None)
    else:   sys.stdout.write(cbrackets[0])

    for i, part in enumerate(data):
        # unpack data
        char, pcnt, fgcolor, bgcolor, bold = part
        width = int( round(pcnt/100.0 * maxwidth, 0) )
        position = position + width

        # and graph
        if incolor and not ( fgcolor is None):
            cprint(char * width, fgcolor, bgcolor, bold, False)
        else:
            sys.stdout.write((char * width))

        if (i == datalen-1):   # last one
            if position < maxwidth:
                if incolor: # char
                    cprint(char * (maxwidth-position), fgcolor, bgcolor,
                           bold, False)
                else:
                    sys.stdout.write(char * (maxwidth-position))
            elif position > maxwidth:
                sys.stdout.write(chr(8) + ' ' + chr(8))  # backspace

    # Print right bracket in correct color:
    if cbrackets and incolor:
        if endpcnt < threshold: lbkcolor = data[0][3] # redbg
        else:                   lbkcolor = data[1][3] # greenbg
        cprint(cbrackets[1], data[-1][2], lbkcolor, None, None)
    else:    sys.stdout.write(cbrackets[1])


# -------------------------------------------------------------------
# modified from gentoo portage "output" module
# Copyright 1998-2004 Gentoo Foundation
def set_xterm_title(mystr):
    'set the title of an xterm'
    if os.environ.has_key('TERM') and sys.stderr.isatty():
        terms = ['xterm', 'Eterm', 'aterm', 'rxvt', 'screen', 'kterm',
                 'rxvt-unicode']
        term = os.environ['TERM']
        if term in terms:
            sys.stderr.write('\x1b]2;'+str(mystr)+'\x07')
            sys.stderr.flush()

#def xtermTitleReset():
    #if os.environ.has_key("TERM"):
        #myt=os.environ["TERM"]
        #xtermTitle(os.environ["TERM"])

# -------------------------------------------------------------------
# from avkutil.py - Andrei Kulakov <ak@silmarill.org>
def get_term_size():
    '''Return terminal size as tuple (width, height).'''
    x, y = 0, 0
    if sys.platform.startswith('linux'):
        import struct, fcntl, termios
        try:
            y, x = struct.unpack('hhhh', fcntl.ioctl(0,
                termios.TIOCGWINSZ, '\000'*8))[0:2]
        except IOError: pass
    elif sys.platform.startswith('win'):
        #~ http://code.activestate.com/recipes/440694-determine-size-of-console-window-on-windows/
        res = None
        try:
            from ctypes import windll, create_string_buffer
            # stdin handle is -10
            # stdout handle is -11
            # stderr handle is -12
            h = windll.kernel32.GetStdHandle(-12)
            csbi = create_string_buffer(22)
            res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
        except Exception: pass
        if res:
            import struct
            (bufx, bufy, curx, cury, wattr, left, top, right, bottom,
             maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
            x = right - left + 1
            y = bottom - top + 1
    return x, y

