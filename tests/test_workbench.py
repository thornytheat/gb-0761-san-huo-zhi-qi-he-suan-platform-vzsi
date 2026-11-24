from app.presentation import NAMES


def test_seven_workbench_entries(client):
    for path, label in NAMES.items():
        response = client.get('/' + path)
        assert response.status_code == 200 and label.encode() in response.data


def test_main_page_and_clean_form(client):
    response = client.get('/')
    assert '滞期费分档对照'.encode() in response.data and b'160.00 USD' in response.data
    response = client.post('/ledger', data={'sample': 'clean'})
    assert b'0.00 USD' in response.data and b'160.00 USD' not in response.data


def test_bad_custom_source_recovers_in_place(client, dirty):
    dirty['events'] = 'bad,name\nvalue,keep\n'
    response = client.post('/notice', data={'sample': 'custom', **dirty})
    assert b'BAD_HEADER' in response.data and b'value,keep' in response.data


def test_api_path_all_stages(client):
    for path, key in [('intake', 'statistics'), ('notice', 'decisions'), ('exceptions', 'segments'), ('clock', 'counted'), ('ledger', 'differences')]:
        reply = client.post('/api/' + path, json={'sample': 'dirty'})
        assert reply.status_code == 200 and key in reply.json
