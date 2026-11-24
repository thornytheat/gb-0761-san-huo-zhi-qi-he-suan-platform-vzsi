import pytest

from app.errors import Rejected
from app.pipeline import evaluate


def test_notice_picks_active_priority(dirty):  # TRAP-25
    result = evaluate(dirty, 'notice')['notice']
    assert result['term']['version'] == 'R2'
    assert result['decisions'][1]['shadowed_terms'] == ['R1']
    assert result['start'] == '2026-12-31T23:00+00:00'


def test_pre_tender_and_retender_have_different_reasons(dirty):
    result = evaluate(dirty, 'notice')['notice']
    assert [d['code'] for d in result['decisions']] == ['PREMATURE_OR_WRONG_PARTY', 'ACCEPTED_NOR', 'ALREADY_TENDERED']


def test_completion_uses_port_on_reordered_file(dirty):
    result = evaluate(dirty, 'notice')['notice']
    assert (result['completion_line'], result['loading_line'], result['end']) == (2, 5, '2027-01-01T01:30+00:00')


def test_readiness_tie_at_same_minute(clean):
    result = evaluate(clean, 'notice')['notice']
    assert (result['readiness_line'], result['notice_line']) == (2, 3)


def test_equal_contract_priority_rejected(dirty):
    dirty['terms'] = dirty['terms'].replace(',20,30,35,', ',10,30,35,')
    with pytest.raises(Rejected, match='TERM_PRIORITY_TIE'):
        evaluate(dirty, 'notice')


def test_no_port_finish(clean):
    clean['events'] = clean['events'].replace('07:30Z,PORT', '07:30Z,SHIP')
    with pytest.raises(Rejected, match='NO_PORT_COMPLETION'):
        evaluate(clean, 'notice')


def test_term_end_excluded(clean):
    clean['terms'] = clean['terms'].replace('2026-12-01T00:00Z', '2026-11-20T06:00Z')
    with pytest.raises(Rejected, match='NO_VALID_NOTICE'):
        evaluate(clean, 'notice')
