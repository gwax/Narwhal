#!/usr/bin/env python
"""Basic example.

Shows how to construct narrative attributes and apply them to a sentence.

This example uses the narrative tree:

EXPERIENCE(KW_EXP)
    FOOD(KW_FOOD)
    AFFECT()
        SAD(KW_SAD)
        | HAPPY(KW_HAPPY)
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

KW_FOOD = 'cheese,cilantro'
KW_SAD = 'sad,unhappy,angry'
KW_HAPPY = 'gleeful,not $ happy'
KW_EXPERIENCE = 'experience,we found,I found,we did find'

SENTENCES = [
    'Cheese makes me happy.',
    'Cilantro makes me sad.',
]


def app():
    """Create a new narwhal app."""
    var_food = nwt.KList('foo', KW_FOOD).var()
    var_sad = nwt.KList('sad', KW_SAD).var()
    var_happy = nwt.KList('happy', KW_HAPPY).var()

    var_affect = var_sad | var_happy
    var_experience = nwt.KList('experience', KW_EXPERIENCE).var()
    var_experience.sub(var_food)
    var_experience.sub(var_affect)

    nar_eating = nwt.cause(var_food, var_affect)
    nars_calibs_thresholds = [
        (nar_eating, True, 0.6),
    ]
    return nwa.NWApp(var_experience, *zip(*nars_calibs_thresholds))


def main():
    """Run the model against some sentences."""
    for sentence in SENTENCES:
        app_food = app()
        print('Sentence: ' + sentence)
        app_food.readText(sentence)
        report = app_food.report(sentence)
        print(report)


if __name__ == '__main__':
    main()
