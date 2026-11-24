from app.pipeline import evaluate


def cuts(sources):
    return evaluate(sources, 'exceptions')['exceptions']


def test_precedence_permutation(dirty):  # TRAP-19
    actual = cuts(dirty)
    header, *rows = dirty['stops'].splitlines()
    dirty['stops'] = '\n'.join([header, *reversed(rows)])
    assert [(r['start'], r['winner']) for r in cuts(dirty)['segments']] == [(r['start'], r['winner']) for r in actual['segments']]
    assert actual['overlaps'] == 1


def test_touching_window_is_outside(dirty):  # TRAP-23
    assert [r['id'] for r in cuts(dirty)['outside']] == ['S04', 'S05']


def test_overlap_keeps_losing_source(dirty):
    overlap, = [r for r in cuts(dirty)['segments'] if len(r['sources']) == 2]
    assert (overlap['winner'], [r['id'] for r in overlap['sources']]) == ('S02', ['S02', 'S01'])


def test_gap_overrules_exemption(dirty):
    dirty['stops'] += 'S99,GAP,2026-12-31T23:35Z,2026-12-31T23:40Z\n'
    segment, = [r for r in cuts(dirty)['segments'] if r['winner'] == 'S99']
    assert segment['bucket'] == 'missing'
    assert len(segment['sources']) == 3


def test_no_stops_one_counted_interval(clean):
    clean['stops'] = clean['stops'].splitlines()[0] + '\n'
    assert [r['reason'] for r in cuts(clean)['segments']] == ['WORKING_CLOCK']


def test_stop_crossing_start_clipped(clean):
    clean['stops'] = clean['stops'].replace('06:40Z', '06:10Z')
    first = cuts(clean)['segments'][0]
    assert (first['start'], first['reason'], first['sources'][0]['start']) == ('2026-11-20T06:20+00:00', 'RAIN', '2026-11-20T06:10+00:00')
