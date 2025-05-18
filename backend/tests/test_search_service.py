import pytest
from unittest.mock import patch, MagicMock
from architectural_patterns.service.search_service import SearchService

class DummyPropiedad:
    def __init__(self, id, precio, wifi=True, piscina=True, cochera=True, pet_friendly=True, patio_trasero=True):
        self.id = id
        self.precio = precio
        self.wifi = wifi
        self.piscina = piscina
        self.cochera = cochera
        self.pet_friendly = pet_friendly
        self.patio_trasero = patio_trasero
    def to_dict(self):
        return self.__dict__

@pytest.fixture
def propiedades():
    return [
        DummyPropiedad(1, 100, wifi=True, piscina=True, cochera=True, pet_friendly=True, patio_trasero=True),
        DummyPropiedad(2, 200, wifi=False, piscina=True, cochera=True, pet_friendly=True, patio_trasero=True),
        DummyPropiedad(3, 150, wifi=True, piscina=False, cochera=True, pet_friendly=True, patio_trasero=True),
        DummyPropiedad(4, 120, wifi=True, piscina=True, cochera=False, pet_friendly=True, patio_trasero=True),
    ]

@pytest.fixture
def default_data():
    return {
        'ubicacion': 'Ciudad',
        'fecha_inicio': '2024-06-01',
        'fecha_fin': '2024-06-05',
        'caracteristicas': [],
        'precio_min': '',
        'precio_max': '',
        'orden_precio': '',
        'pagina': 1,
        'por_pagina': 3
    }

@patch('architectural_patterns.repository.propiedad_repository.PropiedadRepository')
@patch('architectural_patterns.repository.reserva_repository.ReservaRepository')
def test_search_properties_basic(mock_reserva_repo, mock_prop_repo, propiedades, default_data):
    mock_prop_repo.return_value.get_properties_by_location.return_value = propiedades
    mock_reserva_repo.return_value.get_propiedades_reservadas_entre_fechas.return_value = []
    service = SearchService()
    result = service.search_properties(default_data)
    assert result['success'] is True
    assert result['total_propiedades'] == 4
    assert result['cantidad_noches'] == 4
    assert result['propiedades'][0]['id'] == 1

@patch('architectural_patterns.repository.propiedad_repository.PropiedadRepository')
@patch('architectural_patterns.repository.reserva_repository.ReservaRepository')
def test_search_properties_with_characteristics(mock_reserva_repo, mock_prop_repo, propiedades, default_data):
    mock_prop_repo.return_value.get_properties_by_location.return_value = propiedades
    mock_reserva_repo.return_value.get_propiedades_reservadas_entre_fechas.return_value = []
    service = SearchService()
    data = default_data.copy()
    data['caracteristicas'] = ['wifi', 'pileta']
    result = service.search_properties(data)
    assert result['success'] is True
    assert all(p['wifi'] and p['piscina'] for p in result['propiedades'])

@patch('architectural_patterns.repository.propiedad_repository.PropiedadRepository')
@patch('architectural_patterns.repository.reserva_repository.ReservaRepository')
def test_search_properties_with_price_range(mock_reserva_repo, mock_prop_repo, propiedades, default_data):
    mock_prop_repo.return_value.get_properties_by_location.return_value = propiedades
    mock_reserva_repo.return_value.get_propiedades_reservadas_entre_fechas.return_value = []
    service = SearchService()
    data = default_data.copy()
    data['precio_min'] = '400'
    data['precio_max'] = '600'
    result = service.search_properties(data)
    assert result['success'] is True or result['success'] is False
    if result['success']:
        for p in result['propiedades']:
            assert 400 <= result['precios_totales'][p['id']] <= 600
    else:
        assert "No se encontraron propiedades dentro del rango de precios" in result['mensaje']

@patch('architectural_patterns.repository.propiedad_repository.PropiedadRepository')
@patch('architectural_patterns.repository.reserva_repository.ReservaRepository')
def test_search_properties_no_results_for_characteristics(mock_reserva_repo, mock_prop_repo, propiedades, default_data):
    mock_prop_repo.return_value.get_properties_by_location.return_value = propiedades
    mock_reserva_repo.return_value.get_propiedades_reservadas_entre_fechas.return_value = []
    service = SearchService()
    data = default_data.copy()
    data['caracteristicas'] = ['wifi', 'pileta', 'cochera', 'mascotas', 'patio', 'nonexistent']
    result = service.search_properties(data)
    assert result['success'] is False
    assert "caracteristicas seleccionadas" in result['mensaje']

@patch('architectural_patterns.repository.propiedad_repository.PropiedadRepository')
@patch('architectural_patterns.repository.reserva_repository.ReservaRepository')
def test_search_properties_no_results_for_location(mock_reserva_repo, mock_prop_repo, default_data):
    mock_prop_repo.return_value.get_properties_by_location.return_value = []
    mock_reserva_repo.return_value.get_propiedades_reservadas_entre_fechas.return_value = []
    service = SearchService()
    result = service.search_properties(default_data)
    assert result['success'] is False
    assert "ubicación" in result['mensaje']

@patch('architectural_patterns.repository.propiedad_repository.PropiedadRepository')
@patch('architectural_patterns.repository.reserva_repository.ReservaRepository')
def test_search_properties_with_pagination(mock_reserva_repo, mock_prop_repo, propiedades, default_data):
    mock_prop_repo.return_value.get_properties_by_location.return_value = propiedades * 2  # 8 propiedades
    mock_reserva_repo.return_value.get_propiedades_reservadas_entre_fechas.return_value = []
    service = SearchService()
    data = default_data.copy()
    data['por_pagina'] = 3
    data['pagina'] = 2
    result = service.search_properties(data)
    assert result['success'] is True
    assert result['pagina'] == 2
    assert result['por_pagina'] == 3
    assert len(result['propiedades']) == 3

@patch('architectural_patterns.repository.propiedad_repository.PropiedadRepository')
@patch('architectural_patterns.repository.reserva_repository.ReservaRepository')
def test_search_properties_with_ordering(mock_reserva_repo, mock_prop_repo, propiedades, default_data):
    mock_prop_repo.return_value.get_properties_by_location.return_value = propiedades
    mock_reserva_repo.return_value.get_propiedades_reservadas_entre_fechas.return_value = []
    service = SearchService()
    data = default_data.copy()
    data['orden_precio'] = 'asc'
    result = service.search_properties(data)
    precios = [p['precio'] for p in result['propiedades']]
    assert precios == sorted(precios)
    data['orden_precio'] = 'desc'
    result = service.search_properties(data)
    precios = [p['precio'] for p in result['propiedades']]
    assert precios == sorted(precios, reverse=True)