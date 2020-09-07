"""This module contains a class for providing access to Dinero API."""

from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session
import json
import logging

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
    """A connection object for accessing Dinero API."""

    API_URL_V1 = 'https://api.dinero.dk/v1'
    API_URL_V1_2 = 'https://api.dinero.dk/v1.2'

    def __init__(self, client_id, client_secret, api_key, name=None):
        """
        Create a new instance.

        :param client_id: Dinero client ID.
        :param client_secret: Dinero client secret.
        :param api_key: Dinero API key.
        :param name: Name of organization to work/on.
        """
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
        """Set the Dinero organization to work with/on.

        :param name: Name of organization.

        """
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
        """Get all contacts of current organization."""
        url = f'{self.API_URL_V1}/{self.organization}/contacts'
        return self.session.get(url)

    def get_contact(self, contact):
        """Get named contact of current organization."""
        url = f'{self.API_URL_V1}/{self.organization}/contacts/{contact}'
        return self.session.get(url)

    def update_contact(self, contact, data):
        """
        Update contact information in current organization.

        :param contact: Contact id to change.
        :param data: Update contact data to upload.
        """
        url = f'{self.API_URL_V1}/{self.organization}/contacts/{contact}'
        self.session.put(url, json=data)

    def _get_matching_contact(self, fields, match_fn):
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
        """Get contact ID of named contact."""
        def name_match(c):
            if c['name'] == name:
                return c['contactGuid']
            else:
                return None
        return self._get_matching_contact('name,contactGuid', name_match)

    def contact_with_external_reference(self, key, value):
        """
        Get contact ID of contact with matching ExternalReference.

        The ExternalReference field is assumed to be a JSON object, and a
        contact matches if the ExternalReference JSON object has a key/value
        match.

        :param key: Key to match.
        :param value: Value to match.
        """
        def extref_match(c):
            extref = c.get('ExternalReference')
            try:
                extref = json.loads(extref)
            except Exception as e:
                logging.warn(f'Bad ExternalReference value: {e}: {extref}')
                return None
            if extref.get(key) == value:
                return c['contactGuid']
            return None
        return self._get_matching_contact(
            'name,contactGuid,ExternalReference', extref_match)

    def create_invoice(self, contact, product_lines=[],
                       language=None, currency=None, comment=None, date=None):
        """
        Create draft invoice.

        :param contact: Contact ID.
        :param product_lines: Product lines for the invoices API.
        :param language: Language of the invoice.
        :param currency: Currency to use for the invoice.
        :param comment: Comment to add to invoice.
        :param date: Invoice date.
        """
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

    def get_draft_invoice(self, contact):
        """
        Get existing draft invoice.

        Exactly one draft invoice is expected to exist for the contact.  If no
        or more than one draft voice exists for the customer, this function
        returns None.

        :param contact: Contact ID to get draft invoice for.
        :return: Invoice data or None.

        """
        url = f'{self.API_URL_V1}/{self.organization}/invoices'
        params = {'fields': "Guid,Date,Description",
                  'statusFilter': 'Draft',
                  'queryFilter': f"ContactGuid eq '{contact}'"}
        resp = self.session.get(url, params=params)
        if not resp.ok:
            print('Error: Getting invoice list failed: ' +
                  f'{resp.status_code} {resp.reason}')
            print(resp.text)
            return None
        invoices = resp.json()['Collection']
        if len(invoices) == 0:
            print('Error: No draft invoice found')
            return None
        if len(invoices) > 1:
            print('Error: Multiple draft invoices found')
            return None
        guid = invoices[0]['Guid']
        url = f'{self.API_URL_V1}/{self.organization}/invoices/{guid}'
        resp = self.session.get(url, headers={'Accept': 'application/json'})
        if not resp.ok:
            print('Error: Getting invoice failed: ' +
                  f'{resp.status_code} {resp.reason}')
            print(resp.text)
            return None
        invoice = resp.json()
        return invoice

    def update_invoice(self, invoice):
        """
        Update existing draft invoice.

        :param guid: Invoice data.
        """
        guid = invoice['Guid']
        # API v1 does not support Text lines, so we need to use at least v1.2
        url = f'{self.API_URL_V1_2}/{self.organization}/invoices/{guid}'
        resp = self.session.put(url, json=invoice)
        if not resp.ok:
            print('Error: Updating invoice failed: ' +
                  f'{resp.status_code} {resp.reason}')
            print(resp.text)
