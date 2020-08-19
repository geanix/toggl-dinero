"""This module contains a class for providing access to Toggl API."""

from toggl import TogglPy
import logging


class TogglAPI:
    """A connection object for accessing Toggl API."""

    def __init__(self, api_token):
        """Create a new instance."""
        self.api = TogglPy.Toggl()
        self.api.setAPIKey(api_token)

    def client_id(self, name):
        """Resolve client ID from name."""
        client = self.api.getClient(name)
        if client is None:
            return None
        return client.get('id')

    def workspace_id(self, name=None):
        """Get workspace ID."""
        if name is None:
            workspaces = self.api.getWorkspaces()
            if len(workspaces) != 1:
                logging.warning('Unable to determine workspace ID, '
                                'Please specify workspace name')
                return None
            return workspaces[0]['id']
        workspace = self.api.getWorkspace(name)
        if workspace is None:
            logging.warning(f'Unknown workspace: {name}')
            return None
        return workspace['id']

    def get_summary_report(self, data, pdf=None):
        """
        Fetch summary report.

        :param data: Request parameters for the summary report API.
        :param pdf: Filename to write PDF report to.
        :return: Summary report data as dictionary
        """
        report = self.api.getSummaryReport(data)
        if pdf is not None:
            self.api.getSummaryReportPDF(data, pdf)
        return report
