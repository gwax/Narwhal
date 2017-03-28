import pytest

from narwhal import nwtypes
from narwhal.nwapp import NWApp
from narwhal_noise import NoiseTree as NT


@pytest.fixture
def noise_app():
    problem = nwtypes.attribute(NT.PROBLEM, NT.SOUND)
    sound = nwtypes.attribute(
        nwtypes.attribute(
            nwtypes.attribute(
                NT.SOUND,
                NT.SOURCE,
            ),
            NT.INTENSITY,
        ),
        NT.TOD
    )
    affect = nwtypes.cause(
        nwtypes.attribute(
            NT.SOUND,
            [NT.TOD],
        ),
        NT.AFFECT
    )
    proximity = nwtypes.attribute(
        NT.LOC,
        NT.SOURCE,
        rel=NT.PROX,
    )
    letin = nwtypes.event(
        nwtypes.attribute(NT.BARRIER, [NT.STATE]),
        NT.SOUND,
        NT.LETINOUT,
    )
    nars_calibs_thresholds = [
        (problem, True, 0.6),
        (sound, True, 0.6),
        (affect, True, 0.6),
        (proximity, True, 0.6),
        (letin, True, 0.6),
    ]
    nars, calibs, thresholds = zip(*nars_calibs_thresholds)
    return NWApp(NT.EXPERIENCE, nars, calibs, thresholds)


def postprocess_report(report):
    """Reports are human readable matrices, convert to a machine format."""
    report = report.strip()
    for i, line in enumerate(report.splitlines()):
        line = line.strip()
        name, *values = line.split()
        values = [0 if v == '.' else float(v) for v in values]
        if any(values):
            yield [i, name] + values


@pytest.mark.parametrize('text, expected', [
    (
        'word spoken was heard through the walls',
        [
            [4, 'through', -0.5, -0.3333, -0.3333, 0, 0],
            [7, 'END', 0, 0, 0, 0, -1.0],
        ],
    ),
    (
        'My room was far from the elevator and far from the lobby, so it was very quiet.',
        [
            [7, 'and', 0, -0.6667, 0, 1.0, 0],
            [12, '_comma_', 0, 0, 0, 1.0, 0],
            [15, 'was', 0, 0, 0, -1.0, 0],
            [18, '_period_', 0.5, 1.0, 0.3333, 0, 0.3333],
        ],
    ),
    (
        'Although my room was next to the elevator, it was perfectly quiet and dark at night so I was able to sleep much better than most European cities',
        [
            [8, '_comma_', 0, 0.6667, 0, 1.0, 0],
            [10, 'was', 0, 0, 0, -1.0, 0],
            [13, 'and', 0.5, 0.6667, 0.3333, 0, 0.3333],
            [17, 'so', 0, 0.75, 0, 0, 0],
            [23, 'much', 0, 0, -0.4286, 0, 0],
        ],
    ),
    (
        'it was perfectly quiet and dark at night ',
        [
            [1, 'was', 0, 0, 0, -0.3333, 0],
            [4, 'and', 0.5, 0.3333, 0.3333, 0, 0.3333],
            [8, 'END', 0, 0.5, 0.5, 0, 0],
        ],
    ),
    (
        'We did find it a bit noisy with the balcony doors open due to the McDonalds next door.',
        [
            [16, 'next', -0.375, -0.75, -0.25, 0, -0.75],
            [18, '_period_', 0, 0, 0, -0.6, 0],
        ],
    ),

])
def test_noise_app(noise_app, text, expected):
    noise_app.readText(text)
    report = noise_app.report(text)
    assert list(postprocess_report(report)) == expected
