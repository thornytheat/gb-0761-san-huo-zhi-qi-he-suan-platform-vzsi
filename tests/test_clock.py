from app.pipeline import evaluate


def clock(sources):
    return evaluate(sources, 'clock')['clock']


def test_cross_year_conservation(dirty):
    row = clock(dirty)
    assert (row['elapsed_min'], row['counted'], row['exempt'], row['missing']) == (150, 75, 60, 15)
    assert row['balanced'] is True


def test_exhaustion_inside_segment(dirty):
    assert clock(dirty)['overtime_start'] == '2027-01-01T00:35+00:00'


def test_allowance_exactly_consumed(clean):
    result = clock(clean)
    assert (result['counted'], result['overtime_min'], result['overtime_start']) == (60, 0, None)


def test_gap_does_not_consume_limit(dirty):
    gap = next(r for r in clock(dirty)['rows'] if r['bucket'] == 'missing')
    assert (gap['minutes'], gap['cumulative_counted_min'], gap['allowance_min'], gap['overtime_min']) == (15, 45, 0, 0)


def test_zero_duration(clean):
    clean['events'] = clean['events'].replace('06:25Z', '06:20Z').replace('07:30Z', '06:20Z')
    result = clock(clean)
    assert result['elapsed_min'] == 0 and result['balanced'] is True and result['rows'] == []


def test_zero_allowance(dirty):
    dirty['terms'] = dirty['terms'].replace(',30,35,', ',30,0,')
    result = clock(dirty)
    assert (result['overtime_min'], result['overtime_start']) == (75, '2026-12-31T23:00+00:00')
