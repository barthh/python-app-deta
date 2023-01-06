from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_LOCATION = 'client_secrets.json'

# Comme le fichier .env ne peut pas être envoyé sur Deta (Request entity too large), 
# On utilise un fichier Python pour stocker les clés d'API sensibles.
from hidden_keys import get_VIEW_ID
VIEW_ID = get_VIEW_ID()

def initialize_analyticsreporting():
    """Initializes an Analytics Reporting API V4 service object.
    Returns:
      An authorized Analytics Reporting API V4 service object.
    """
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        KEY_FILE_LOCATION, SCOPES)

    # Build the service object.
    return build('analyticsreporting', 'v4', credentials=credentials)


def get_report(analytics):
    """Queries the Analytics Reporting API V4.
    Args:
      analytics: An authorized Analytics Reporting API V4 service object.
    Returns:
      The Analytics Reporting API V4 response.
    """
    return analytics.reports().batchGet(
        body={
            'reportRequests': [
                {
                    'viewId': VIEW_ID,
                    'dateRanges': [{'startDate': '7daysAgo', 'endDate': 'today'}],
                    'metrics': [{'expression': 'ga:pageviews'}],
                    'dimensions': []
                    # 'dimensions': [{'name': 'ga:country'}]
                }]
        }
    ).execute()


def print_response(response):
    """Parses and prints the Analytics Reporting API V4 response.
    Args:
      response: An Analytics Reporting API V4 response.
    """
    for report in response.get('reports', []):
        columnHeader = report.get('columnHeader', {})
        dimensionHeaders = columnHeader.get('dimensions', [])
        metricHeaders = columnHeader.get(
            'metricHeader', {}).get('metricHeaderEntries', [])

        for row in report.get('data', {}).get('rows', []):
            dimensions = row.get('dimensions', [])
            dateRangeValues = row.get('metrics', [])

            for header, dimension in zip(dimensionHeaders, dimensions):
                print(header + ': ', dimension)

            for i, values in enumerate(dateRangeValues):
                print('Date range:', str(i))
                for metricHeader, value in zip(metricHeaders, values.get('values')):
                    visitors = value
    return str(visitors)
