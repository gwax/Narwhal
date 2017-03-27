# this file is for the Noise application with VAR tree like this:
##EXPERIENCE( experienceD )
##  PROBLEM( problemD )
##  SOUND( soundD )
##    NOISE( noiseD | quietD )
##    INTENSITY( loudD | softD )
##    SOURCE( peopleD + equipmentD + ... + oceanD )
##  LOC( locationD )
##    ROOM( roomD )
##    HOTEL( hotelD )
##    PROX( nearD | farD )
# INSULATION()
##    BARRIER( windowD + wallD )
##    STATE( openD | closedD )
##    TRANSPARENCY( letInD | keepOutD )
##  TOD( timeofdayD )
##  AFFECT( stressD | relaxD )

import os

import yaml
try:
    from yaml import CSafeLoader as Loader
except ImportError:
    from yaml import SafeLoader as Loader

from narwhal.nwtypes import KList


DATADIR = os.path.join(os.path.dirname(__file__), 'data')
DATAFILENAME = os.path.join(DATADIR, 'noise.yaml')
with open(DATAFILENAME, 'rt') as datafile:
    NOISEDATA = yaml.load(datafile, Loader=Loader)

KLISTS = {}
for klistdata in NOISEDATA['klists']:
    name = klistdata['name']
    keywords = ','.join(klistdata['keywords'])
    KLISTS[name] = KList(name, keywords)

############################################################################
#------------- KLists
# add to this list
# note: expericence shoule be made as the | of two KList VARs
# For example "was bad" belongs in a negative KList
experienceD = KLISTS['experience']
problemD = KLISTS['problem']
soundD = KLISTS['sound']
noiseD = KLISTS['noise']
quietD = KLISTS['quiet']
loudD = KLISTS['loud']
softD = KLISTS['soft']
peopleD = KLISTS['people']
partyD = KLISTS['party']
equipmentD = KLISTS['equip']
trafficD = KLISTS['traffic']
constructionD = KLISTS['constr']
oasisD = KLISTS['oasis']
# unfotunately, to work around a bug:
nsourceD = KList('nsource', ','.join(
    peopleD.list +
    partyD.list +
    equipmentD.list +
    trafficD.list +
    constructionD.list))
qsourceD = KList('oasis', ','.join(oasisD.list))
roomD = KLISTS['room']
hotelD = KLISTS['hotel']
nearD = KLISTS['near']
farD = KLISTS['far']
insulationD = KLISTS['insul']
windowD = KLISTS['window']
wallD = KLISTS['wall']
openD = KLISTS['open']
closedD = KLISTS['closed']
letinD = KLISTS['letin']
keepoutD = KLISTS['keepout']
timeofdayD = KLISTS['tod']
relaxD = KLISTS['relax']
stressD = KLISTS['stress']

############################################################################
############################################################################
############################################################################

#-----------define the VARs from the KeyLists
EXPERIENCE = experienceD.var()
PROBLEM = problemD.var()
SOUND = soundD.var()

NOISE = noiseD.var() | quietD.var()

INTENSITY = loudD.var() | softD.var()


SOURCE = nsourceD.var() | qsourceD.var()

#SOURCE = (peopleD.var() + partyD.var() + equipmentD.var()+ trafficD.var() + constructionD.var()) | oasisD.var()


LOC = KList("loc", "").var()  # VAR()
ROOM = roomD.var()
HOTEL = hotelD.var()

PROX = nearD.var() | farD.var()  # typically an adjective val
INSULATION = insulationD.var()
BARRIER = windowD.var() + wallD.var()
STATE = openD.var() | closedD.var()
LETINOUT = letinD.var() | keepoutD.var()  # typically a verb
TOD = timeofdayD .var()
AFFECT = stressD.var() | relaxD.var()

#--------------define the tree built from these VARs
EXPERIENCE.sub(PROBLEM)
EXPERIENCE.sub(SOUND)
EXPERIENCE.sub(LOC)
EXPERIENCE.sub(PROX)
EXPERIENCE.sub(INSULATION)
EXPERIENCE.sub(TOD)
EXPERIENCE.sub(AFFECT)

# PROBLEM
#
SOUND.sub(NOISE)
SOUND.sub(INTENSITY)
SOUND.sub(SOURCE)
#
LOC.sub(ROOM)
LOC.sub(HOTEL)
# LOC.sub(PROX) moved up
#
INSULATION.sub(BARRIER)
INSULATION.sub(STATE)
INSULATION.sub(LETINOUT)
#
# TOD - no children
#
# AFFECT - no children


# Some NARs
#                       sound->me :: me_/affect
#                       sound_/intensity_/source_/timeOfDay (use implicits)
#                       problem_/sound
#                       (barrier_/state)-letInOut->sound
#                       location _nearfar_/ source
#                       X_/Y :: sound
