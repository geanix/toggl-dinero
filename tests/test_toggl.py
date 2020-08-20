"""Tests for toggl_dinero.toggl module."""


import pytest
import requests
from toggl_dinero.toggl import TogglAPI


def test_init():
    TogglAPI('foobar')


CLIENTS = [
    {'id': 1234, 'wid': 5657, 'name': 'Foo', 'at': '2019-12-23T12:23:07+00:00'},
    {'id': 8901, 'wid': 2345, 'name': 'Bar', 'at': '2019-12-23T12:23:12+00:00'},
]

WORKSPACES = [
    {
        'id': 1234, 'name': 'Foo',
        'profile': 101, 'premium': True, 'admin': True,
        'default_hourly_rate': 42, 'default_currency': 'DKK',
        'only_admins_may_create_projects': False,
        'only_admins_see_billable_rates': False,
        'only_admins_see_team_dashboard': False,
        'projects_billable_by_default': True,
        'rounding': 0, 'rounding_minutes': 6,
        'api_token': '58b5eb5988f029d9e1fab66018a73cac',
        'at': '2020-08-07T15:22:00+00:00',
        'logo_url': 'https://assets.toggl.com/logos/1234567890.png',
        'ical_enabled': True, 'ical_url': '/ical/workspace_user/1234567890',
    },
    {
        'id': 5678, 'name': 'Bar',
        'profile': 102, 'premium': True, 'admin': False,
        'default_hourly_rate': 43, 'default_currency': 'DKK',
        'only_admins_may_create_projects': False,
        'only_admins_see_billable_rates': False,
        'only_admins_see_team_dashboard': False,
        'projects_billable_by_default': True,
        'rounding': 0, 'rounding_minutes': 6,
        'api_token': '58b5eb5988f029d9e1fab66018a73cac',
        'at': '2020-08-07T15:23:00+00:00',
        'logo_url': 'https://assets.toggl.com/logos/1234567891.png',
        'ical_enabled': True, 'ical_url': '/ical/workspace_user/1234567891',
     },
]

SUMMARY_REPORT_JSON = {
    'data': [
        {'id': 1234,
         'items': [{'cur': 'DKK',
                    'rate': 1000.0,
                    'sum': 200.0,
                    'time': 720000,
                    'title': {'time_entry': 'Some stuff'}},
                   {'cur': 'DKK',
                    'rate': 1000.0,
                    'sum': 5400.0,
                    'time': 19440000,
                    'title': {'time_entry': 'Other stuff'}}],
         'time': 20160000,
         'title': {'client': 'Client',
                   'color': '0',
                   'hex_color': '#0b83d9',
                   'project': 'Things'},
         'total_currencies': [{'amount': 5600.0, 'currency': 'DKK'}]},
        {'id': 5678,
         'items': [{'cur': 'DKK',
                    'rate': 2000.0,
                    'sum': 200.0,
                    'time': 360000,
                    'title': {'time_entry': 'Wasting time'}}],
         'time': 360000,
         'title': {'client': 'DEIF',
                   'color': '0',
                   'hex_color': '#525266',
                   'project': 'Nothing'},
         'total_currencies': [{'amount': 200.0, 'currency': 'DKK'}]}],
    'total_billable': 20520000,
    'total_currencies': [{'amount': 5800.0, 'currency': 'DKK'}],
    'total_grand': 20520000}

SUMMARY_REPORT_PDF = b'foobar'


@pytest.fixture(scope='function')
def api(requests_mock):
    requests_mock.get('https://www.toggl.com/api/v8/clients',
                      json=CLIENTS)
    requests_mock.get('https://www.toggl.com/api/v8/workspaces',
                      json=WORKSPACES)
    api = TogglAPI('__DUMMY_API_KEY__')
    api.mock = requests_mock
    return api


@pytest.mark.parametrize('i', range(len(CLIENTS)))
def test_client_id(api, i):
    assert api.client_id(CLIENTS[i]['name']) == CLIENTS[i]['id']


def test_client_id_unknown(api):
    assert api.client_id('unknown') is None


@pytest.mark.parametrize('i', range(len(CLIENTS)))
def test_workspace_id(api, i):
    assert api.workspace_id(WORKSPACES[i]['name']) == WORKSPACES[i]['id']


def test_workspace_id_unknown(api):
    assert api.workspace_id('unknown') is None


@pytest.mark.parametrize('i', range(len(CLIENTS)))
def test_workspace_id_none(api, i):
    api.mock.get('https://www.toggl.com/api/v8/workspaces',
                 json=WORKSPACES[i:i+1])
    assert api.workspace_id() == WORKSPACES[i]['id']


def test_workspace_id_none_all(api):
    assert api.workspace_id() == None


def test_summary_report(api):
    api.mock.get('https://toggl.com/reports/api/v2/summary?'
                 'user_agent=toggl-dinero&workspace_id=42',
                 json=SUMMARY_REPORT_JSON)
    assert api.summary_report({'workspace_id': 42}) == SUMMARY_REPORT_JSON


def test_summary_report_pdf(api):
    api.mock.get('https://toggl.com/reports/api/v2/summary.pdf?'
                 'user_agent=toggl-dinero&workspace_id=42',
                 content=b'pdf file')
    assert api.summary_report_pdf({'workspace_id': 42}) == b'pdf file'
