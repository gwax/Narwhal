#!/usr/bin/env python
"""Hotel noise analysis example.

This example uses the tree defined in noise_tree.py
"""
import os
import sys

# Add local narwhal to the module path
this_file = os.path.abspath(__file__)
narwhal_dir = os.path.join(os.path.dirname(this_file), '..')
narwhal_dir = os.path.normpath(narwhal_dir)
sys.path.insert(0, narwhal_dir)

from narwhal import nwtypes as nwt
from narwhal import nwapp as nwa

import noise_tree as nt

PROBLEM = nwt.attribute(nt.PROBLEM, nt.SOUND)
SOUND = nwt.attribute(
    nwt.attribute(
        nwt.attribute(nt.SOUND, nt.SOURCE),
        nt.INTENSITY),
    nt.TOD)
AFFECT = nwt.cause(
    nwt.attribute(nt.SOUND, [nt.TOD]),
    nt.AFFECT)
PROXIMITY = nwt.attribute(nt.LOC, nt.SOURCE, nt.PROX)
LETIN = nwt.event(
    nwt.attribute(nt.BARRIER, [nt.STATE]),
    nt.SOUND,
    nt.LETINOUT)

NARS_CALIBS_THRESHOLDS = [
    (PROBLEM, True, 0.6),
    (SOUND, True, 0.6),
    (AFFECT, True, 0.6),
    (PROXIMITY, True, 0.6),
    (LETIN, True, 0.6),
]
NARS, CALIBS, THRESHOLDS = zip(*NARS_CALIBS_THRESHOLDS)

APP_NOISE = nwa.NWApp(nt.EXPERIENCE, NARS, CALIBS, THRESHOLDS)

SENTENCES = [
    'word spoken was heard through the walls',
    'My room was far from the elevator and far from the lobby, so it was very quiet.',
    'Although my room was next to the elevator, it was perfectly quiet and dark at night so I was able to sleep much better than most European cities',
    'it was perfectly quiet and dark at night',
    'We did find it a bit noisy with the balcony doors open due to the McDonalds next door.',
]


def main():
    """Run the model against some sentences."""
    for sentence in SENTENCES:
        print('Sentence: ' + sentence)
        APP_NOISE.readText(sentence)
        report = APP_NOISE.report(sentence)
        print(report)


if __name__ == '__main__':
    main()
