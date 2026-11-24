import pytest

from app.errors import Rejected
from app.modules.intake.reader import rows
from app.modules.intake.service import accept


def test_bom_and_repeated_header(dirty):  # TRAP-02 TRAP-04
    out = accept(dirty)
    assert out['statistics']['events'] == dict(input=14, blank=1, headers=2, accepted=7, isolated=5, balanced=True)
    assert out['accepted']['events'][0]['event_id'] == 'E01'


def test_column_count_isolated(dirty):  # TRAP-05
    errors = accept(dirty)['isolated']
    assert next(row for row in errors if row['code'] == 'COLUMN_COUNT')['line'] == 12


def test_sentinel_kept_as_evidence(dirty):  # TRAP-07
    errors = accept(dirty)['isolated']
    assert next(row for row in errors if row['code'] == 'MISSING_SENTINEL')['raw'][2] == 'N/A'


def test_offsets_dedupe_by_instant(dirty):  # TRAP-11
    out = accept(dirty)
    assert out['reason_counts']['EXACT_DUPLICATE'] == 1
    assert next(r for r in out['accepted']['events'] if r['event_id'] == 'E03')['time'] == '2026-12-31T22:30+00:00'


def test_conflicting_key_is_withdrawn(dirty):  # TRAP-14
    out = accept(dirty)
    assert [r['line'] for r in out['isolated'] if r['code'] == 'KEY_CONFLICT'] == [13, 14]
    assert 'E11' not in [r['event_id'] for r in out['accepted']['events']]


@pytest.mark.parametrize('raw,code', [('', 'EMPTY_FILE'), ('\n , ,\n', 'BLANK_FILE'), ('event_id,kind,time,party\n', 'HEADER_ONLY')])
def test_three_file_empty_states(raw, code):
    with pytest.raises(Rejected, match=code):
        rows('events', raw)


def test_header_reorder(clean):
    clean['invoice'] = 'usd,tier,minutes\n0,1,0\n0,2,0\n'
    assert accept(clean)['accepted']['invoice'][1]['tier'] == 2
