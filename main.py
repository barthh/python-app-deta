from flask import Flask, render_template, request
import logging
import sys
import requests
from pytrends.request import TrendReq
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def hellow_world():
    # Permet d'ajouter une vue sur Google Analytics
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

from analytics_functions import initialize_analyticsreporting, get_report, print_response

@app.route('/visitors')
def visitors():
    analytics = initialize_analyticsreporting()
    response = get_report(analytics)
    nb_visitor = print_response(response)
    logging.info("Test gdx")
    return render_template('visitors.html', visitors=str(nb_visitor))



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
