def validate_user(data):
    if 'email' not in data or '@' not in data['email']:
        raise ValueError('Email inválido')
    if 'password' not in data or len(data['password']) < 6:
        raise ValueError('Senha muito curta')

def validate_especie(data):
    if not data.get('nome_cientifico'):
        raise ValueError('Nome científico obrigatório')

def validate_ordem_servico(data):
    if not data.get('tipo'):
        raise ValueError('Tipo de ordem obrigatório')

def validate_vistoria(data):
    if not data.get('data'):
        raise ValueError('Data da vistoria obrigatória')
    
def validate_coordinates(data):
    if 'latitude' not in data or 'longitude' not in data:
        raise ValueError('Coordenadas inválidas')
    if not (-90 <= data['latitude'] <= 90) or not (-180 <= data['longitude'] <= 180):
        raise ValueError('Coordenadas fora do intervalo válido')
    
def validate_required_fields(data, required_fields):
    for field in required_fields:
        if field not in data or not data[field]:
            raise ValueError(f'O campo {field} é obrigatório')

def validate_date(date_str, date_format='%Y-%m-%d'):
    from datetime import datetime
    try:
        datetime.strptime(date_str, date_format)
    except ValueError:
        raise ValueError(f'Data inválida, deve estar no formato {date_format}')