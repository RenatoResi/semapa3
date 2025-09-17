import json

def test_criar_requerimento(client, db):
    payload = {
        "tipo": "poda",
        "descricao": "Poda de árvore na Rua A",
        "requerente_id": 1
    }
    # criar requerente prévio
    client.post('/requerentes', json={"nome": "Fulano", "tipo_pessoa": "PF"})

    res = client.post('/requerimentos', json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data['tipo'] == payload['tipo']
    assert data['descricao'] == payload['descricao']


def test_alterar_requerimento(client, db):
    # criar requerimento
    res = client.post('/requerimentos', json={"tipo": "remoção", "descricao": "Remoção no Parque", "requerente_id": 1})
    req_id = res.get_json()['id']

    update = {"descricao": "Remoção no Parque Central"}
    res2 = client.put(f'/requerimentos/{req_id}', json=update)
    assert res2.status_code == 200
    data2 = res2.get_json()
    assert data2['descricao'] == update['descricao']
