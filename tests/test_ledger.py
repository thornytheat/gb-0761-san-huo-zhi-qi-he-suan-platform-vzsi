from app.pipeline import evaluate


def ledger(sources):
    return evaluate(sources)['ledger']


def test_dirty_price_and_bill(dirty):
    result = ledger(dirty)
    assert (result['expected_usd'], result['seen_invoice_usd'], result['delta_usd']) == ('160.00', '155.00', '5.00')
    assert result['rows'][1]['invoice_line'] == 3


def test_clean_has_two_zero_brackets(clean):
    assert [r['code'] for r in ledger(clean)['rows']] == ['MATCH', 'MATCH']


def test_missing_invoice_is_unknown_not_zero(dirty):
    dirty['invoice'] = 'tier,minutes,usd\n1,20,60\n'
    result = ledger(dirty)
    assert result['delta_usd'] is None and result['rows'][1]['code'] == 'INVOICE_MISSING'


def test_conflicting_bill_keeps_both_lines(dirty):
    dirty['invoice'] += '2,20,100\n'
    result = ledger(dirty)
    assert result['rows'][1]['conflict_lines'] == [3, 4]
    assert result['rows'][1]['code'] == 'INVOICE_CONFLICT'


def test_equal_money_different_minutes_is_disputed(dirty):
    dirty['invoice'] = dirty['invoice'].replace('19,95', '19,100')
    result = ledger(dirty)
    assert (result['delta_usd'], result['differences']) == ('0.00', 1)


def test_decimal_cents_without_float(dirty):
    dirty['terms'] = dirty['terms'].replace(',20,3,5', ',20,0.17,0.12')
    assert ledger(dirty)['expected_usd'] == '5.80'
