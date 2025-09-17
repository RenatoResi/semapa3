import json

def test_criar_vistoria(client, db):
    # criar ordem prévia
    res_req = client.post('/requerimentos', json={"tipo": "poda", "descricao": "Poda na Rua D", "requerente_id": 1})
    req_id = res_req.get_json()['id']
    res_ord = client.post('/ordens', json={"requerimento_id": req_id, "responsavel": "Técnico D"})
    ord_id = res_ord.get_json()['id']

    payload = {"ordem_id": ord_id, "observacoes": "Vistoria concluída"}
    res = client.post('/vistorias', json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data['observacoes'] == payload['observacoes']


def test_alterar_vistoria(client, db):
    res_req = client.post('/requerimentos', json={"tipo": "remoção", "descricao": "Remoção na Rua E", "requerente_id": 1})
    req_id = res_req.get_json()['id']
    res_ord = client.post('/ordens', json={"requerimento_id": req_id, "responsavel": "Técnico E"})
    ord_id = res_ord.get_json()['id']
    res_vis = client.post('/vistorias', json={"ordem_id": ord_id, "observacoes": "Vistoria inicial"})
    vis_id = res_vis.get_json()['id']

    update = {"observacoes": "Vistoria revisada"}
    res2 = client.put(f'/vistorias/{vis_id}', json=update)
    assert res2.status_code == 200
    data2 = res2.get_json()
    assert data2['observacoes'] == update['observacoes']
