import hashlib
import json


def certificate(client, sample):
    run_id = client.post('/api/runs', json={'sample': sample}).json['run_id']
    return client.get(f'/api/evidence/{run_id}').json


def test_dirty_withheld_certificate(client):
    pack = certificate(client, 'dirty')
    assert pack['can_settle'] is False
    assert pack['evidence_counts'] == {'intervals': 7, 'tiers': 2, 'isolated': 6}


def test_clean_certificate_settleable(client):
    assert certificate(client, 'clean')['can_settle'] is True


def test_integrity_digest_can_be_recomputed(client):
    pack = certificate(client, 'dirty')
    serialized = json.dumps(pack['snapshot'], sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()
    assert pack['integrity_sha256'] == hashlib.sha256(serialized).hexdigest()


def test_download_matches_review(client):
    pack = certificate(client, 'dirty')
    response = client.get('/api/export/' + pack['snapshot']['run_id'])
    assert response.json == pack and response.headers['Content-Disposition'].startswith('attachment;')


def test_evidence_has_actual_source_rows(client):
    pack = certificate(client, 'dirty')
    assert pack['snapshot']['results']['intake']['isolated'][0]['raw'][0] == 'E03'
    assert pack['snapshot']['results']['notice']['completion_line'] == 2


def test_missing_evidence_cannot_be_downloaded(client):
    reply = client.get('/api/export/missing')
    assert (reply.status_code, reply.json['code']) == (404, 'UNKNOWN_RUN')
