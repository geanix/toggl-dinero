from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session
import json

# Dinero invoice creation procedure
#
# Get an OAuth2 token from https://authz.dinero.dk/dineroapi/oauth/token
# and attach that to all following requests (see https://api.dinero.dk/docs)
#
# Get list of organisations, and use that to resolve/get organisation id
# (Geanix ApS).
#
# Get list of contacts, and use that to resolve contact client name to
# contactGuid number.
#
# Make create invoice request
# - ContactGuid
# - Language (da-DK / en-GB)
# - ProductLines[]
#   - BaseAmountValue
#   - Description (project title)
#   - Quantity (hours)
#   - Unit ("hours")


DINERO_TOKEN_URL = 'https://authz.dinero.dk/dineroapi/oauth/token'


class DineroAPI:

    API_URL_V1 = 'https://api.dinero.dk/v1'

    def __init__(self, client_id, client_secret, api_key, name=None):
        client = LegacyApplicationClient(client_id=client_id)
        oauth = OAuth2Session(client=client)
        token = oauth.fetch_token(token_url=DINERO_TOKEN_URL,
                                  username=api_key, password=api_key,
                                  client_id=client_id,
                                  client_secret=client_secret)
        self.session = oauth
        self.token = token
        if not self.set_organization(name):
            raise Exception('Could not set organization')

    def set_organization(self, name=None):
        url = f'{self.API_URL_V1}/organizations'
        params = {'fields': 'name,id'}
        orgs = self.session.get(url, params=params).json()
        if name is None:
            if len(orgs) == 1:
                self.organization = orgs[0]['id']
                return self.organization
            else:
                return None
        for org in orgs:
            if org['name'] == name:
                self.organization = org['id']
                return self.organization
        return None

    def get_contacts(self):
        url = f'{self.API_URL_V1}/{self.organization}/contacts'
        return self.session.get(url)

    def get_contact(self, contact):
        url = f'{self.API_URL_V1}/{self.organization}/contacts/{contact}'
        return self.session.get(url)

    def update_contact(self, contact, data):
        url = f'{self.API_URL_V1}/{self.organization}/contacts/{contact}'
        self.session.put(url, json=data)

    def get_matching_contact(self, fields, match_fn):
        url = f'{self.API_URL_V1}/{self.organization}/contacts'
        params = {
            'fields': fields,
            'page': 0}
        while True:
            contacts = self.session.get(url, params=params).json()
            for contact in contacts['Collection']:
                match = match_fn(contact)
                if match:
                    return match
            results = contacts['Pagination']['Result']
            pagesize = contacts['Pagination']['PageSize']
            if results < pagesize:
                break
            params['page'] += 1
        return None

    def contact_id(self, name):
        def name_match(c):
            if c['name'] == name:
                return c['contactGuid']
            else:
                return None
        return self.get_matching_contact('name,contactGuid', name_match)

    def contact_with_external_reference(self, key, value):
        def toggl_match(c):
            extref = c.get('ExternalReference')
            try:
                extref = json.loads(extref)
            except:
                return None
            if extref.get(key) == value:
                return c['contactGuid']
            return None
        return self.get_matching_contact(
            'name,contactGuid,ExternalReference', toggl_match)

    def create_invoice(self, contact, product_lines=[],
                       language=None, currency=None, comment=None, date=None):
        url = f'{self.API_URL_V1}/{self.organization}/invoices'
        if language == 'da':
            language = 'da-DK'
        elif language == 'en':
            language = 'en-GB'
        body = {
            'ContactGuid': contact,
            'Currency': currency,
            'Language': language,
            'Comment': comment,
            'Date': date,
            'ProductLines': product_lines,
        }
        body = {k: v for (k, v) in body.items() if v is not None}
        resp = self.session.post(url, json=body)
        if not resp.ok:
            print('Error: Creating invoice failed: ' +
                  f'{resp.status_code} {resp.reason}')
            print(resp.text)