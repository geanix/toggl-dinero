from toggl import TogglPy


class TogglAPI:

    def __init__(self, api_token):
        self.api = TogglPy.Toggl()
        self.api.setAPIKey(api_token)

    def client_id(self, name):
        client = self.api.getClient(name)
        if client is None:
            return None
        return client.get('id')

    def workspace_id(self, name):
        workspace = self.api.getWorkspace(name)
        return workspace['id']

    def get_summary_report(self, data, pdf=None):
        report = self.api.getSummaryReport(data)
        if pdf is not None:
            self.api.getSummaryReportPDF(data, pdf)
        return report
