"""This module contains a class for providing access to Toggl API."""

from togglwrapper import Toggl
import requests
import logging


class TogglAPI:
    """A connection object for accessing Toggl API."""

    def __init__(self, api_token):
        """Create a new instance."""
        self.api = Toggl(api_token)
        self.reports_api = Toggl(api_token,
                                 base_url='https://toggl.com/reports/api',
                                 version='v2')

    def client_id(self, name):
        """Resolve client ID from name."""
        for client in self.api.Clients.get():
            if client['name'] == name:
                return client['id']
        return None

    def workspace_id(self, name=None):
        """Get workspace ID."""
        workspaces = self.api.Workspaces.get()
        if name is None:
            if len(workspaces) != 1:
                logging.warning('Unable to determine workspace ID, '
                                'Please specify workspace name')
                return None
            return workspaces[0]['id']
        for workspace in workspaces:
            if workspace['name'] == name:
                return workspace['id']
        logging.warning(f'Unknown workspace: {name}')
        return None

    def summary_report(self, params):
        """
        Fetch summary report (JSON data).

        :param params: Request parameters for the summary report API.
        :return: Summary report data as dictionary
        """
        params.setdefault('user_agent', 'toggl-dinero')
        return self.reports_api.get('/summary', params=params)

    def summary_report_pdf(self, params):
        """
        Fetch summary report (PDF file).

        :param params: Request parameters for the summary report API.
        :return: Summary report PDF as bytes
        """
        params.setdefault('user_agent', 'toggl-dinero')
        # togglwrapper wraps get() with a return_json fixture, so we need
        # use requests directly
        report = requests.get(f'{self.reports_api.api_url}/summary.pdf',
                              params=params, auth=self.reports_api.auth)
        report.raise_for_status()
        return report.content
