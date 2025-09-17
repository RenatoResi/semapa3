import json

def test_criar_ordem_servico(client, db):
    # criar requerimento prévio
    res_req = client.post('/requerimentos', json={"tipo": "transplante", "descricao": "Transplante na Av B", "requerente_id": 1})
    req_id = res_req.get_json()['id']

    payload = {"requerimento_id": req_id, "responsavel": "Técnico A"}
    res = client.post('/ordens', json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data['responsavel'] == payload['responsavel']


def test_alterar_ordem_servico(client, db):
    res_req = client.post('/requerimentos', json={"tipo": "poda", "descricao": "Poda na Rua C", "requerente_id": 1})
    req_id = res_req.get_json()['id']
    res_ord = client.post('/ordens', json={"requerimento_id": req_id, "responsavel": "Técnico B"})
    ord_id = res_ord.get_json()['id']

    update = {"responsavel": "Técnico C"}
    res2 = client.put(f'/ordens/{ord_id}', json=update)
    assert res2.status_code == 200
    data2 = res2.get_json()
    assert data2['responsavel'] == update['responsavel']
