from flask import Flask, render_template, request
import logging
import sys
import requests
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from pytrends.request import TrendReq
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_LOCATION = 'client_secrets.json'

# Comme le fichier .env ne peut pas être envoyé sur Deta (Request entity too large), 
# On utilise un fichier Python pour stocker les clés d'API sensibles.
from hidden_keys import get_VIEW_ID
VIEW_ID = get_VIEW_ID()

app = Flask(__name__)

@app.route('/')
def hellow_world():
    prefix_google = """
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=UA-251258993-1"></script> <script>
    window.dataLayer = window.dataLayer || []; function gtag(){dataLayer.push(arguments);} gtag('js', new Date());
    gtag('config', 'UA-251258993-1'); </script>"""

    return prefix_google + render_template("index.html",)


@app.route('/logger')
@app.route('/logger', methods=["POST"])
def logger():
    script = ""
    message = ""

    if request.method == 'POST':
        # Get the input value
        message = request.form.get('log_message')
        if message:
            # Deta log ("deta logs" command)
            print("Log for Deta :", message, file=sys.stderr)
            # Broswer console log
            script = '<script>console.log("Another log : ' + \
                message + '") </script>'

    return render_template("logger.html", log=message) + script


@app.route('/cookies')
def cookies():
    # Request google
    req = requests.get("https://www.google.com/")
    # return req.text
    return render_template("cookies.html", cookie=req.cookies.get_dict())


@app.route('/visitors')
def visitors():
    analytics = initialize_analyticsreporting()
    response = get_report(analytics)
    nb_visitor = print_response(response)
    logging.info("Test gdx")
    return render_template('visitors.html', visitors=str(nb_visitor))

## FOR VISITORS ##########


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


# GRAPHS

@app.route('/timer_log', methods=["GET", "POST"])
def timer_log():
    return render_template("timer_log.html")

@app.route("/trend", methods=['GET', 'POST'])
def trend(element_1 = "vacances", element_2 = "voyage"):

    # Prends les arguments d'entrée
    if request.method == 'POST':
      element_1 = request.form['element_1']
      element_2 = request.form['element_2']
  
    # Connexion à l'API Google Trends
    pytrend = TrendReq()

    # Définition des mots-clés et de la période de temps
    timeframe = 'today 5-y'

    # Chargement des données
    pytrend.build_payload(kw_list=[element_1, element_2], timeframe=timeframe)
    data = pytrend.interest_over_time()

    # Transformation des données en listes pour pouvoir les passer à Chart.js
    labels = data.index.tolist()

    formatted_labels = []
    for date in labels:
        date_str = date.strftime('%a, %d %b %Y %H:%M:%S')
        formatted_date = datetime.strptime(
            date_str, '%a, %d %b %Y %H:%M:%S').strftime('%d/%m/%Y')
        formatted_labels.append(formatted_date)

    values_1 = data[element_1].tolist()
    values_2 = data[element_2].tolist()

    return render_template(
      'chart.html',
      elements = [element_1, element_2],
      labels = formatted_labels, 
      values_1 = values_1, 
      values_2 = values_2
    )

if __name__ == '__main__':
    app.run(debug=True)
