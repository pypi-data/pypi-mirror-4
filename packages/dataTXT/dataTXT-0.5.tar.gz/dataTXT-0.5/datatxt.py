#!/usr/bin/env python
# encoding=utf8

# datatxt DBpedia it python integration
# test user = hacktivist

from __future__ import print_function

from requests import get

import sparql
import collections

# Global Defaults for the 'hackaton' account to avoid registering a new one
# on http://www.spaziodati.eu/dataTXT
APP_KEY   = '2e57de2ce47dcc1e82613b16017efbf2'
APP_ID    = '1191439d'
LANG      = 'it'
API_URL   = 'http://spaziodati.eu/datatxt/v3/'
RHO       = 0.1
EPSILON   = 0.3
LONG_TEXT = 0
PREFIX    = 'http://it.dbpedia.org'
ENDPOINT  = PREFIX + '/sparql'

# FIXME: ugly hack ahead, needs a virtuoso >= 6.1.6 to remove it
def unpack_row(row):
    """
    Transform row in python objects
    needed because virtuoso < 6.1.6 has a RDF/XML bug on literals
    otherwise similar to sparql.unpack_row()
    """
    pred, obj = sparql.unpack_row(row)
    if isinstance(row[1], sparql.Literal):
        try:
            str(obj)
        except UnicodeEncodeError:
            obj = obj.encode('latin1').decode('utf8')
    return pred, obj

class Datatxt(object):
    """
    Main datatxt text parsers, instantiate a class passing deviation from
    defaults globals listed above
    documentation here: https://spaziodati.3scale.net/getting-started
    """
    def __init__(self, app_key = APP_KEY, app_id = APP_ID, lang = LANG, api_url = API_URL, rho=RHO, epsilon=EPSILON, long_text=LONG_TEXT, prefix=PREFIX, endpoint=ENDPOINT):
        self.api_url = api_url
        self.params = {
            'app_key' : app_key,
            'app_id' : app_id,
            'lang': lang,
            'dbpedia' : 'false',
            'rho' : rho,
            'epsilon' : epsilon,
            'long_text' : long_text,
        }
        self.headers = {
            'Accept' : 'application/json'
        }
        self.default_rho = rho
        self.service = sparql.Service(endpoint)
        self.prefix = prefix

    def annotate(self, text, properties=True, wikilinks=False, rho=None):
        """ return a dictionary out of json
        Example output:
        {u'annotations': [
            {end': 12,
            u'id': 160969,
            u'ref': u'http://it.dbpedia.org/resource/Etimologia',
            u'properties': {all properties in a dictionary of lists}
            u'rho': 0.2531,
            u'spot': u'etimologia',
            u'start': 2,
            u'title': u'Etimologia'},
            {u'end': 25,
            u'id': 102140,
            u'ref': u'http://it.dbpedia.org/resource/Parola',
            u'rho': 0.10507,
            u'spot': u'parola',
            u'start': 19,
            u'title': u'Parola'} #[...]],
        u'error': None,
        u'lang': u'it',
        u'status': 200,
        u'text': u'L\'etimologia della parola che d\xc3\xa0 il nome alla citt\xc3\xa0 di Rovereto  deriva dal latino Roborem e trae dalla stessa radice della parola Robur: forza, robustezza, robusto. In Botanica la parola legno di rovere \xc3\xa8 correlata ad una specie di quercia indigena dell\'Europa, di minore altezza alla quercia ordinaria, ma che fornisce un legno durissimo: Quercus petraea. Nella toponomastica romana "Roboretum" significava selva di querce, albero che abbonda nella valle ed \xc3\xa8 effigie dello stemma comunale.'}
        """
        params = dict(self.params)
        params['text'] = text
        if rho:
            params['rho'] = rho

        r = get(self.api_url, params=self.params, headers=self.headers)
        if r.status_code == 200:
            result = r.json
            for annotation in result['annotations']:
                resource = annotation['ref'][0]['wikipedia'].replace('wikipedia.org/wiki', 'dbpedia.org/resource')
                annotation['ref'] = resource
                if properties:
                    annotation[u'properties'] = self.properties(resource, wikilinks)
            return result

    def sparql(self, query):
        # FIXME: it works only for queries with 2 columns, where the first is an IRI
        result = self.service.query(query)
        statement = query.lower()
        if 'select' in statement:
            d = collections.defaultdict(list)
            for pred, obj in (unpack_row(row) for row in result):
                d[pred].append(obj)
            return dict(d)
        elif 'ask' in statement:
            return result.hasresult()

    def properties(self, resource, wikilinks=False):
        if wikilinks:
            query = "select * where {<%s> ?pred ?obj .}" % resource
        else:
            query = "select * where { graph <%s> {<%s> ?pred ?obj .}}" % (self.prefix, resource)
        return self.sparql(query)

if __name__ == '__main__':
    print("Use datatxt-cli, this is just a python module")


