# SNHS-63

# MAIN VALIDATION PROCESSES

# Process a sorted v3 Update file, creating a v4 file with acceptable records,
# and separate files for Rejects and Queries
# Also create a file of Area Mismatch ... BUT ... add them to the Accepted file too (unless previously rejected)

# SUGGESTION: If a record is dubious, check if (a later) (ANY) accepted sighting exists in the DB, if so discard the bad one
# *** If ANY sighting exists for "S" area, Discard dubious.
# To this end, read the SNHS Master List into a dictionary

# Jan 2019: First read the GL Seaford list into a dict. If our processes produce "?S" AND the year matches GL year,
# then force oldarea to "S"   ### SHOULD USE LATEST SWT ALL RESERVES LIST WITH SEAFORD EXTRACT ###

from timeit import default_timer as timer  # set up a timer function


def matchgoodwords(thelist, theinput):      # find if any of the words in the list "thelist" exist in "theinput"
    wipline = theinput.lower()
    idx3 = 0
    maxi = len(thelist)
    while idx3 < maxi:
        argx = thelist[idx3]
        rm = wipline.find(argx)
        if rm != -1:
            rc = thelist[idx3+1]
            if rc == "**S":                 # e.g. Lagoon, definitely SWT, force S
                rc = "S"
            return rc
        idx3 += 2
    return 'X'


def matchbadwords(thelist, theinput):
    wipline = theinput.lower()
    idx3 = 0
    maxi = len(thelist)
    while idx3 < maxi:
        argx = thelist[idx3]
        rm = wipline.find(argx)
        if rm != -1:
            return 'Y'
        idx3 += 1
    return 'X'


def verifygrid(wgridref, startidx, btaxgroup, precorder):
    # REVISED 01/01/2018
    # Check if record is within the LNR
    # Can only do this if Grid Ref is 8 or 10 or 12 characters

    global bigreflist

    checkeast = ''
    checknorth = ''
    if wgridref == 'tv51539775':
        checkeast = ''

    lengr = len(wgridref)
    if lengr < 6:
        return 'Q'
    if lengr == 6:
        checkeast = wgridref[2:4] + '00'
        checknorth = wgridref[4:6] + '00'
    if lengr == 8:
        checkeast = wgridref[2:5] + '0'
        checknorth = wgridref[5:8] + '0'
    if lengr == 10:
        checkeast = wgridref[2:6]
        checknorth = wgridref[6:10]
    if lengr == 12:
        checkeast = wgridref[2:6]
        checknorth = wgridref[7:11]

    # Create a 4-digit east-numeric
    # Check the Eastings part is in the range TV49 - TV51
    if checkeast < '4900':
        return 'X'
    if checkeast > '5199':
        return 'X'
    if checkeast < '5100':
        if checknorth > '9860':
            return 'X'

    if checkeast == '':
        return 'Q'           # return 'uncertain' result

    if lengr < 8:
        return 'Q'

    # Look for an array entry that encompasses this Grid Ref
    idxv = startidx
    checkgr = checkeast[0:3] + checknorth[0:3]
    while idxv < maxrefidx:
        gra = bigreflist[idxv]
        grb = bigreflist[idxv + 1]
        areax = bigreflist[idxv + 2]
        aux = bigreflist[idxv + 3]
        if (checkgr >= gra) and (checkgr <= grb):
            if lengr > 8:
                if aux == "DR":            # Diagonal Down-Right
                    if ( int(checknorth[-1:]) + int(checkeast[-1:])) > 9:      # TR is 1st (X) BL is 2nd (F)
                        areax = areax[:1]
                    else:
                        areax = areax[-1:]
                    return areax
                if aux == "DL":            # Diagonal Down-Left. TopLeft is 1st code, BR is 2nd
                    if checknorth[-1:] >= checkeast[-1:]:
                        areax = areax[:1]  # (S)
                    else:
                        areax = areax[-1:]  # (F)
                    return areax
            if aux == 'H':     # Bee or Beetle ?
                if " bee" in btaxgroup or "hymen" in btaxgroup:
                    areax = areax[:1]  # (S)
                else:
                    areax = areax[-1:]  # (F)
                return areax
            if aux == 'B':     # Bird ?
                if "bird" in btaxgroup:
                    areax = areax[:1]  # (S)
                else:
                    areax = areax[-1:]  # (X)
                return areax
            if aux != 'Y':
                # Try and validate a point within 100m square. Needs a 10 character grid ref
                # There are so few, it's not worth trying
                # print("Examine Grid Ref on line: ", lino, gridref)
                return 'Q'
            return areax
        if grb > checkgr:
            return 'X'
        idxv += 4
    return 'X'


def doallverify(agrid, alocation, arecorder, astart, ataxgroup):
    # verify using Grid Ref,  Location,  Recorder

    if "==reject" in alocation:
        return 'X'

    wgridref = agrid
    wrest = alocation + ' ' + arecorder
    startidx = astart

    rv = verifygrid(wgridref, startidx, ataxgroup, arecorder)
    if len(rv) > 2:
        longcode = 1

    if rv == 'X':       # If definitely rejected on Grid. Ref. ...
        # if 'graeme lyons' in arecorder:   bumkum
        #    return 'S'
        return rv

    if rv[:1] == "*":
        return rv

    if rv in ["E", "F", "N", "S", "X"]:
        return rv

    if "S" in rv and "brewer" in arecorder and "lnr" in alocation:
        return "S"
    if "S" in rv and "whiteman" in arecorder and "lnr" in alocation:
        return "S"
    if "S" in rv and "lagoon" in alocation:
        return "S"
    if "F" in rv and "beach" in arecorder:
        return "F"
    if "F" in rv and "foreshore" in alocation:
        return "F"
    if rv != "Q":
        return rv

    rv = matchbadwords(rejectlist, alocation)
    if rv == 'Y':
        return 'W'
    # Grid ref is vague.  If the line contains a good keyword, then accept the line
    rv2 = matchgoodwords(acceptlist, wrest)
    if rv2 == 'X':
        return rv
    else:
        return rv2                     # mayba A or ?A (if less certain)


# fileREF = open('GLS-SeafordHeadSWTList-Work.txt', 'r')

acceptlist = ['south side of lagoon', '**F', 'lagoon', '**S',
              'foreshore', 'F', 'shingle', '?F',
              'cental', 'F', 'centroid', 'F', 'meander', '?E', 'cuckmere lower', '?N',
              'lnr', 'S', 'swt', 'S', 'nature res', 'S',
              'scallop', '**S', 'graeme lyons', '?S',
              'trench', '**S', 'hope bot', 'S', 'hope gap', '?S', 'pond near barn', '**S',
              'seaford head', '?S', 'transect', 'S',
              'cuckmere haven', '?N', 'cuckmere valley', '?N',
              'national trust', 'N' ]

rejectlist = ["churchyard", "peters", "peter's", "leonard", "splash", "chyngton rd.", "chyngton farm",
              "chyngton way", "cottage", "coastguard", "garden", "exceat", "lullington", "ington pond", "blatchington",
              "seaford beach", " town", "==reject"]

# universalerror = ''

start = timer()

gldict = {}
snhsdict = {}

# Read GL Seaford list into a dictionary  *** USING LATEST SWT All-Reserves Master List ***
filenameGL = "AllReservesMasterDec2019"
fileGL = open(filenameGL + '.txt', 'r')

ftaxonGL = 3
fyearGL = 32

ignor = fileGL.readline()  # skip header
igno2 = fileGL.readline()  # skip header2
line1 = fileGL.readline()
while line1:
    splitgl = line1.split('%')
    if len(splitgl) > 30:
        taxa = splitgl[ftaxonGL].lower()
        pp = taxa.find('#')             # if any synonym ...   *** hummmmmmmm
        if pp > -1:
            taxa = taxa[:pp]            # use preferred name only
        glyear = splitgl[fyearGL]
        gldict[taxa] = glyear
    line1 = fileGL.readline()

fileGL.close()

# ===========================================

# Now read the SNHS old master database into a dictionary
# filename = 'v2 MasterBookCopy2'
# fileMaster = 'v2 SNHS-MasterBookRevised'            # ********** USE LATER DATABASE ***********
fileMaster = "v5 U05-Jly2019"                         # effectively latest SNHS sheet
fileIN1 = open(fileMaster + '.txt', 'r')

# These field numbers get derived from the header line :)
ftaxgroup = 99       # the field number of Taxon Group
ftaxname = 99        # the field number of Taxon Name
fvernac = 99         # field number of common name
farea = 99           # Area code field# ' F ', ' E ', ' N ', ' S ', ' Sn'
fdate = 99
flocation = 99

headerlist = ["taxon", "group", "date", "grid", "common", "vernacular", "recomm"]

line1 = fileIN1.readline()
lino = 1
# Process the SNHS Master header line

RefSize = 0
line1 = line1.strip()
line1_lower = line1.lower()
splitlow = line1_lower.split('%')

# Find the field numbers
maxfield = len(splitlow)
idx = 0
while idx < maxfield:
    fieldx = splitlow[idx]
    if 'recomm' in fieldx or 'taxonname' in fieldx or 'taxon name' in fieldx:
        ftaxname = idx
    elif 'area' in fieldx:
        farea = idx
    elif 'date' in fieldx and fdate == 99:   # get first date field only (this is Sort Date)
        fdate = idx

    idx += 1

# ----------------------------
# Header has been found
# Read the SNHS Master List into a table  storing Area Code and Sort Date per Taxon Name
line1 = fileIN1.readline()
while line1:
    line1 = line1.strip()
    line1_lower = line1.lower()
    splitorig = line1.split('%')
    splitlow = line1_lower.split('%')

    taxname = splitlow[ftaxname]
    sortdate = splitorig[fdate]
    area = splitorig[farea]

    # insert in SNHS Dictionary
    keydata = taxname
    AssocData = area + '@' + sortdate
    snhsdict[keydata] = AssocData
    RefSize += 1

    line1 = fileIN1.readline()

fileIN1.close()
print('SNHS LIST LOADED: ', RefSize, ' ENTRIIES')

fileCONFIG = open("config.txt")
ConfigData = fileCONFIG.readline()          # contains name of file to read, and max Taxon Group (for speed testing)
ConfigSplit = ConfigData.split('%')
fileMain = ConfigSplit[0].strip()
ConfigMaxGroup = ConfigSplit[1].strip().lower()
ConfigFilesToProcess = ConfigSplit[2].strip().lower()
fileCONFIG.close()
print("SNHS-63 Processing: v3 ", fileMain)

print("Processing: v3 ", fileMain)
filepfx = 'v4 '

fileIN = open('v3 ' + fileMain + '.txt', 'r')              # read file created by SNHS-62
fileACCEPT = open(filepfx + fileMain + '.txt', 'w')
fileREJECT = open(filepfx + fileMain + ' Reject.txt', 'w')
fileQUERY = open(filepfx + fileMain + ' Query.txt', 'w')
fileMISMATCH = open(filepfx + fileMain + ' Mismatch.txt', 'w')
fileDISCARD = open(filepfx + fileMain + ' Discard.txt', 'w')

header = 'File%Seq%Old Area%New Area%Taxon Group%Recommended Taxon Name%Common Name%Sort Date%Given Date%Given Year%'
header += 'Grid Ref%Given Taxon%Location%Recorder%Abundance%Nonsp%\n'

fileACCEPT.write(header)
fileREJECT.write(header)
fileQUERY.write(header)
fileMISMATCH.write(header)
fileDISCARD.write(header)

fileGR = open('GridRefDefinesFauna.txt', 'r')   # Open file (which is within the project directory) for Reading
# **** NEED SEPARATE FILES FOR FAUNA/FLORA  *** CREATE ONE LOOKUP TABLE FOR FAUNA AND APPEND FLORA

# Read the first line
line = fileGR.readline()

# Keep reading until a null line is returned

bigreflist = []
maxrefidx = 0

while line:
    line = line.strip()    # strip trailing whitespace
    line_split = line.split(',')
    if len(line_split) > 2:
        # print (line_split)
        if line_split[1] == '':
            line_split[1] = line_split[0]   # duplicate the first Grid Ref into 2nd field
        templist = line_split[0], line_split[1], line_split[2], 'Y'  # 4th field  defaults to 'Y'
        if len(line_split) > 3:
            templist = line_split[0], line_split[1], line_split[2], line_split[3]
        print (templist)
        bigreflist += templist
        maxrefidx += 4     # keep a running total of the size of biglist
        # print (biglist)
    line = fileGR.readline()
fileGR.close()

fileGR = open('GridRefDefinesFlora.txt', 'r')   # Open file (which is within the project directory) for Reading
# **** NEED SEPARATE FILES FOR FAUNA/FLORA  *** NOW APPEND FLORA. REMEMBER WHERE FLORA STARTS IN TABLE
startflora = maxrefidx

# Read the first line
line = fileGR.readline()

# Keep reading until a null line is returned

while line:
    line = line.strip()    # strip trailing whitespace
    line_split = line.split(',')
    if len(line_split) > 2:
        # print (line_split)
        if line_split[1] == '':
            line_split[1] = line_split[0]   # duplicate the first Grid Ref into 2nd field
        templist = line_split[0], line_split[1], line_split[2], 'Y'  # 4th field  defaults to 'Y'
        if len(line_split) > 3:
            templist = line_split[0], line_split[1], line_split[2], line_split[3]
        print (templist)
        bigreflist += templist
        maxrefidx += 4     # keep a running total of the size of biglist
        # print (biglist)
    line = fileGR.readline()
fileGR.close()

# We have built a huge array containing all the Grid Reference definitions
# Now read the sightings file and check the Grid Refs against our definitions array

line = fileIN.readline()
lineout = ''
lino = 1
headerfound = 0
colourok = 0

ftaxgroup = 99       # the field number of Taxon Group
ftaxname = 99        # the field number of Taxon Name
fvernac = 99         # field number of common name
ffile = 99
fseq = 99
farea = 99
fgrid = 99
fgiventax = 99
flocation = 99
frecord = 99
fdate1 = 99
fdate2 = 99
fyear = 99
fabund = 99
fnonsp = 99

headerlist = ["taxon", "group", "date", "grid", "common", "vernacular", "recomm"]

# bigarray = ['zzzzzzzzzz', '------']
# maxidx = 2

line = line.strip()
splitorig = line.split('%')
linelow = line.lower()
splitlow = linelow.split('%')

# Reading the Sightings File header: Find the field numbers
maxfield = len(splitlow)
idx = 0
while idx < maxfield:
    fieldx = splitlow[idx]

    if 'area' in fieldx:
        farea = idx
    elif 'seq' in fieldx:
        fseq = idx
    elif 'file' in fieldx:
        ffile = idx
    elif 'recomm' in fieldx or 'taxonname' in fieldx or 'taxon name' in fieldx:
        if ftaxname == 99:
            ftaxname = idx
    elif 'group' in fieldx:
        ftaxgroup = idx
    elif 'common' in fieldx:
        fvernac = idx
    elif 'date' in fieldx and fdate1 == 99:   # get first date field only (this is Sort Date)
        fdate1 = idx
    elif 'given date' in fieldx:
        fdate2 = idx
    elif 'given' in fieldx and 'tax' in fieldx:
        fgiventax = idx
    elif 'year' in fieldx:
        fyear = idx
    elif 'grid' in fieldx and fgrid == 99:     # Get first Grid Ref field only 14-Oct-2019
        fgrid = idx
    elif 'location' in fieldx:
        flocation = idx
    elif 'recorder' in fieldx:
        frecord = idx
    elif 'abundance' in fieldx:
        fabund = idx
    elif 'nonsp' in fieldx:
        fnonsp = idx
    idx += 1

line = fileIN.readline()

# Reading the Sightings File
while line:
    lino += 1
    line = line.strip()
    splitorig = line.split('%')
    linelow = line.lower()
    splitlow = linelow.split('%')

    if splitlow[ffile] not in ConfigFilesToProcess:
        line = fileIN.readline()
        continue

    maxfield = len(splitlow)

    # print(line)
    if ftaxgroup >= len(splitlow):
        stoptg = 1
    if "0063" in line or "0092" in line:
        gotit = 1
    if "Dual" in line:
        gotit = 1

    taxgroup = splitlow[ftaxgroup]
    taxname = splitlow[ftaxname]
    if "cypha " in taxname:
        cypha = 1
    sortdate = splitorig[fdate1]
    givendate = splitorig[fdate2]
    year = splitorig[fyear]
    grid = splitlow[fgrid]
    location = splitlow[flocation]
    recorder = splitlow[frecord]
    oldarea = splitorig[farea].strip()      # Oldarea =  F / N / S / blank / **a
    if oldarea == '':
        oldarea = ' '
    if oldarea == 'Sn':
        oldarea = 'S'

    if "==reject" in linelow:
        eqflag = 1
        fileREJECT.write(line + '\n')
        line = fileIN.readline()
        continue

    seq = '      ' + splitorig[fseq]
    seq = seq[-5:]

    lineout = splitorig[ffile] + '%' + seq + '%'

    # See if this sighting was flagged as existing on the Exceptions File
    MasterDate = ''
    MasterArea = ''
    ForceArea = ''
    if oldarea[:1] == '*':          # e.g. '**S'
        ForceArea = oldarea
        # myarea = oldarea[2:]
        myarea = ForceArea          # Preserve the forcing indication
        print ("Exception: ", oldarea, "  ", line)

    else:
        # Get latest date from Master List for this species (to find if Master has a later date)
        MasterDate = "1800-01-01"
        MasterArea = ' '
        if taxname in snhsdict:
            # MasterDate = snhsdict[taxname]
            AssocData = snhsdict[taxname]
            AssocSplit = AssocData.split('@')
            MasterArea = AssocSplit[0]
            MasterDate = AssocSplit[1]

        classification = 'fauna'
        floralist = ['flowering', 'lichen', 'liverwort' 'moss', 'fungus']  # NOTE: might change to birds only as fauna
        for w in floralist:
            if w in taxgroup:
                classification = 'flora'

        startgrid = 0
        if classification == 'flora':
            startgrid = startflora

        # =======================================================================================================
        # do the multi-stage verification process

        myarea = doallverify(grid, location, recorder, startgrid, taxgroup)  # E/F/N/S/Q/W/X/**F/FNS etc.

        if myarea == "?S":          # Accept as "S" if matching GL list for year
            myyear = sortdate[:4]
            if taxname in gldict:
                glyear = gldict[taxname]
                if sortdate[:4] == gldict[taxname]:
                    oldarea = "S"
                    myarea = "S"
                    print("GL match forcing S:", line)

        if "F" in myarea and "diver" in splitlow[fvernac]:
            myarea = "F"
        if "F" in myarea and "scoter" in splitlow[fvernac]:
            myarea = "F"
        if "F" in myarea and " tern" in splitlow[fvernac]:
            myarea = "F"
        if "F" in myarea and "coelenterate" in taxgroup:
            myarea = "F"
        if "F" in myarea and "sea slug" in splitlow[fvernac]:
            myarea = "F"
        if "F" in myarea and "calidris" in taxname:
            myarea = "F"
        if "falk" in recorder and "dual" in location:
            splitorig[fgrid] = "TV5179"
            if oldarea == "S":
                myarea = "S"
            else:
                myarea = "X"

        if myarea == "FS" and oldarea == " " and "falk" in recorder:
            myarea = " "

        if myarea == ' ':
            myarea = oldarea                        # my validation finds no reason to doubt old area
        elif oldarea in myarea:         # e.g. r = "FNS" and oldarea = "S" :- accept as S
                                                            # or 'N' amd '?N'  / 'F' and '?F' / 'S' and '?S'
            myarea = oldarea
        elif oldarea == 'F' and myarea == '?S':      # accept as F
            myarea = 'F'
        elif oldarea == 'N' and myarea == '?S':      # accept as N
            myarea = 'N'

    lineout += oldarea
    lineout += "%"
    lineout += myarea
    lineout += '%'

    idx = ftaxgroup
    while idx < maxfield:
        lineout += splitorig[idx]
        lineout += '%'
        idx += 1
    # print(lineout)

    # examine the Taxon Name and reject if xxxxxx sp.
    if " sp." in taxname:
        fileREJECT.write(lineout + '\n')
    else:
        areas = oldarea + myarea[:1]
        if myarea[:1] == '*':
            if myarea == "**X":
                fileREJECT.write(lineout + '\n')
            else:
                fileACCEPT.write(lineout + '\n')
        elif areas == "  " or areas == "X?":
            fileREJECT.write(lineout + '\n')
        elif areas == "NE":         # acceptable
            fileACCEPT.write(lineout + '\n')
        elif myarea == 'X' or myarea == 'W':
            if MasterDate > sortdate or MasterArea == 'S':
                fileDISCARD.write(lineout + '\n')
            else:
                if oldarea in 'FNS':
                    fileQUERY.write(lineout + '\n')
                else:
                    addon = ".."
                    if MasterDate == '' or MasterDate == "1800-01-01":
                        addon = "  WANTED"
                    fileREJECT.write(lineout + addon + '\n')
        elif myarea == 'Q':
            if MasterDate > sortdate:
                fileDISCARD.write(lineout + '\n')
            else:
                fileQUERY.write(lineout + '\n')
        elif oldarea != myarea and oldarea != ' ':
            if MasterDate > sortdate:
                fileDISCARD.write(lineout + '\n')
            else:
                # if long grid ref., accept my new area, else bung in mis-matches
                if len(grid) > 6:
                    fileACCEPT.write(lineout + '\n')
                else:
                    fileMISMATCH.write(lineout + '%\n')
        else:
            fileACCEPT.write(lineout + '\n')

    line = fileIN.readline()

fileIN.close()
fileACCEPT.close()
fileREJECT.close()
fileQUERY.close()
fileMISMATCH.close()
fileDISCARD.close()
print("Finished SNHS-63 Processing: V3 ", fileMain)
end = timer()
print(end - start, " elapsed time")
