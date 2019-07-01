from typing import Dict, Iterator, NamedTuple, Optional

import requests

BASE_URL = 'https://app.climate.azavea.com/api'


class City(NamedTuple):
    name: str
    admin: str
    id: int


class Client:
    """Client for interacting with the Azavea Climate API."""

    def __init__(self, token: str):
        self.session = requests.Session()
        self.session.headers = {'Authorization': f'Token {token}'}

    def _get(self, endpoint: str, **kwargs) -> Dict:
        response = self.session.get(BASE_URL + endpoint, ** kwargs)
        response.raise_for_status()

        return response.json()

    def get_cities(self, **kwargs) -> Iterator[City]:
        """Return all available cities."""
        params = kwargs.get('params')
        if not params:
            params = {'page': 1}
        elif not params.get('page'):
            params.update({'page': 1})

        while True:
            cities = self._get('/city', params=params, **kwargs)

            if not cities.get('next'):
                break
            else:
                params['page'] += 1

            for city in cities['features']:
                yield City(city['properties']['name'], city['properties']['admin'], city['id'])

    def get_city_id(self, name: str, **kwargs) -> Optional[int]:
        """Get the city given a name and return its ID or None if not found."""
        cities = self._get('/city', params={'name': name}, **kwargs)

        if cities['count'] > 0:
            return cities['features'][0]['id']

    def get_scenarios(self, **kwargs) -> Dict:
        return self._get('/scenario', **kwargs)

    def get_indicators(self, **kwargs) -> Dict:
        """Return the full list of indicators."""
        return self._get('/indicator', **kwargs)

    def get_indicator_data(self, city: int, scenario: str, indicator: str, **kwargs) -> Dict:
        """Return derived climate indicator data for the requested indicator."""
        data = self._get(f'/climate-data/{city}/{scenario}/indicator/{indicator}', **kwargs)

        return data['data']
