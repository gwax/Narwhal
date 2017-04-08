
import os
import sys

# Add local narwhal to the module path
this_file = os.path.abspath(__file__)
narwhal_dir = os.path.join(os.path.dirname(this_file), '..')
narwhal_dir = os.path.normpath(narwhal_dir)
sys.path.insert(0, narwhal_dir)

#--------- some core includes
from narwhal.nwtypes import *
from narwhal.nwutils import *
from narwhal.nwcontrol import *
from narwhal.nwsreader import *
from narwhal.nwapp import *


print("\n\n")

# an original sample I wanted to handle
NoiseText = "We did find it a bit noisy with the balcony doors open due "
NoiseText += "to the McDonalds next door - especially late at night and at 6 am "
NoiseText += "when the deliveries started arriving."

#ReadSegment(letin, segment)
#G = gof(segment, letin, ifound, 0, len(text))
#x = 2
# E.clearImplicits()

#--------- app specific
from narwhal_noise.NoiseTree import *
E = EXPERIENCE


problem = attribute(PROBLEM, SOUND)
sound = attribute(attribute(attribute(SOUND, SOURCE), INTENSITY), TOD)
affect = cause(attribute(SOUND, [TOD]), AFFECT)
#affect = attribute(SOUND, [TOD])
proximity = attribute(LOC, SOURCE, PROX)
letin = event(attribute(BARRIER, [STATE]), SOUND, LETINOUT)



SENTENCES = [
    'word spoken was heard through the walls',
    'My room was far from the elevator and far from the lobby, so it was very quiet.',
    'Although my room was next to the elevator, it was perfectly quiet and dark at night so I was able to sleep much better than most European cities',
    'it was perfectly quiet and dark at night',
    'We did find it a bit noisy with the balcony doors open due to the McDonalds next door.',
]

#SENTENCES = [
#    'My room was far from the elevator and far from the lobby, so it was very quiet.'
#    #'so it was very quiet'
#]
#############################################

nars = [problem, sound, affect, proximity, letin]
calibs = [True,    True,  True,   True,      True]
#calibs = [False,  False,  False,   False,    False]
thresholds = [0.6,     0.6,   0.6,    0.6,  0.6]

#nars = [affect]
#calibs = [False]
#thresholds = [0.6]

nwa = NWApp(E, nars, calibs, thresholds)
for sent in SENTENCES:
    text = sent
    nwa.readText(text)
    s = nwa.report(text)
    print(s)
x = 2
