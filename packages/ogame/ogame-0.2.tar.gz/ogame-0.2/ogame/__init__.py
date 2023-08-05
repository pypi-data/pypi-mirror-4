from ogame import constants
from ogame.errors import BAD_UNIVERSE_NAME, BAD_DEFENSE_ID
from bs4 import BeautifulSoup

import requests
import json
import time


class OGame(object):
    def __init__(self, universe, username, password, domain='ogame.org'):
        self.session = requests.session()
        self.servers = self.get_servers(domain)
        self.username = username
        self.password = password
        self.server_url = self.get_universe_url(universe)
        self.login()


    def login(self):
        """Get the ogame session token."""
        payload = {'kid': '',
                   'uni': self.server_url,
                   'login': self.username,
                   'pass': self.password}
        res = self.session.post(self.login_url, data=payload).content
        soup = BeautifulSoup(res)
        self.ogame_session = soup.find('meta', {'name': 'ogame-session'}) \
                                 .get('content')


    def logout(self):
        self.session.get(self.logout_url)


    def get_missions(self):
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        res = self.session.get(self.fetchEventbox_url, headers=headers).content
        return json.loads(res)


    def get_resources(self, planet_id):
        url = self.fetchResources_url + '&cp=%s' % planet_id
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        res = self.session.get(url, headers=headers).content
        return json.loads(res)


    def get_planet_ids(self):
        """Get the ids of your planets."""
        res = self.session.get(self.overview_url).content
        soup = BeautifulSoup(res)
        planets = soup.findAll('div', {'class': 'smallplanet'})
        ids = [planet['id'].replace('planet-', '') for planet in planets]
        return ids


    def get_planet_by_name(self, planet_name):
        """Returns the first planet id with the specified name."""
        res = self.session.get(self.overview_url).content
        soup = BeautifulSoup(res)
        planets = soup.findAll('div', {'class': 'smallplanet'})
        for planet in planets:
            name = planet.find('span', {'class': 'planet-name'}).string
            if name == planet_name:
                id = planet['id'].replace('planet-', '')
                return id
        return None


    def build_defense(self, planet_id, defense_id, nbr):
        """Build a defense unit."""
        if defense_id not in constants.Defense.values():
            raise BAD_DEFENSE_ID

        url = self.defense_url + '&cp=%s' % planet_id

        res = self.session.get(url).content
        soup = BeautifulSoup(res)
        form = soup.find('form')
        token = form.find('input', {'name': 'token'}).get('value')

        payload = {'menge': nbr,
                   'modus': 1,
                   'token': token,
                   'type': defense_id}
        self.session.post(url, data=payload)


    def build_ships(self, planet_id, ship_id, nbr):
        """Build a ship unit."""
        if ship_id not in constants.Ships.values():
            raise BAD_SHIP_ID

        url = self.shipyard_url + '&cp=%s' % planet_id

        res = self.session.get(url).content
        soup = BeautifulSoup(res)
        form = soup.find('form')
        token = form.find('input', {'name': 'token'}).get('value')

        payload = {'menge': nbr,
                   'modus': 1,
                   'token': token,
                   'type': ship_id}
        self.session.post(url, data=payload)


    def build_building(self, planet_id, building_id):
        """Build a ship unit."""
        if building_id not in constants.Buildings.values():
            raise BAD_BUILDING_ID

        url = self.resources_url + '&cp=%s' % planet_id

        res = self.session.get(url).content
        soup = BeautifulSoup(res)
        form = soup.find('form')
        token = form.find('input', {'name': 'token'}).get('value')

        payload = {'modus': 1,
                   'token': token,
                   'type': building_id}
        self.session.post(url, data=payload)


    def build_technology(self, planet_id, technology_id):
        if technology_id not in constants.Research.values():
            raise BAD_RESEARCH_ID

        url = self.research_url + '&cp=%s' % planet_id

        payload = {'modus': 1,
                   'type': technology_id}
        self.session.post(url, data=payload)


    def send_fleet(self, planet_id, ships, speed, where, mission, resources):
        pass


    @property
    def research_url(self):
        return constants.url_research % self.server_url


    @property
    def resources_url(self):
        return constants.url_resources % self.server_url


    @property
    def shipyard_url(self):
        return constants.url_shipyard % self.server_url


    @property
    def defense_url(self):
        return constants.url_defense % self.server_url


    @property
    def overview_url(self):
        return constants.url_overview % self.server_url


    @property
    def fetchResources_url(self):
        return constants.url_fetchResources % self.server_url


    @property
    def fetchEventbox_url(self):
        return constants.url_fetchEventbox % self.server_url


    @property
    def logout_url(self):
        return constants.url_logout % self.server_url


    @property
    def login_url(self):
        return constants.url_login % self.server_url


    def get_servers(self, domain):
        res = self.session.get('http://%s' % domain).content
        soup = BeautifulSoup(res)
        select = soup.find('select', {'id': 'serverLogin'})
        servers = {}
        for opt in select.findAll('option'):
            url = opt.get('value')
            name = opt.string.strip().lower()
            servers[name] = url
        return servers


    def get_universe_url(self, universe):
        """Get a universe name and return the server url."""
        universe = universe.lower()
        if universe not in self.servers:
            raise BAD_UNIVERSE_NAME
        return self.servers[universe]
