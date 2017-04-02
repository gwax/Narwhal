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


def app():
    """Create a new narwhal app."""
    nwv = nt.nwvars()

    # problem_/noise
    nar_problem = nwt.attribute(nwv['problem'], nwv['sound'])

    # sound_/intensity_/source_/timeOfDay ::[me_/affect]
    nar_sound = nwt.attribute(
        nwt.attribute(
            nwt.attribute(nwv['sound'], nwv['source']),
            nwv['intensity']),
        nwv['tod'])

    # [sound->me] :: me_/affect
    nar_affect = nwt.cause(
        nwt.attribute(nwv['sound'], [nwv['tod']]),
        nwv['affect'])

    # location _nearfar_/ source
    nar_prox = nwt.attribute(nwv['loc'], nwv['source'], nwv['prox'])

    # (barrier_/state)-letInOut->sound
    nar_letin = nwt.event(
        nwt.attribute(nwv['barrier'], [nwv['state']]),
        nwv['sound'],
        nwv['letinout'])

    nars_calibs_thresholds = [
        (nar_problem, True, 0.6),
        (nar_sound, True, 0.6),
        (nar_affect, True, 0.6),
        (nar_prox, True, 0.6),
        (nar_letin, True, 0.6),
    ]
    return nwa.NWApp(nwv['experience'], *zip(*nars_calibs_thresholds))


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
        app_noise = app()
        print('Sentence: ' + sentence)
        app_noise.readText(sentence)
        report = app_noise.report(sentence)
        print(report)


if __name__ == '__main__':
    main()
