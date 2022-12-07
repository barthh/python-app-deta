from flask import Flask, render_template, request, redirect, url_for
import logging 
import sys

app = Flask(__name__)

@app.route('/', methods=["GET"])
def hello_world():
    prefix_google = """
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-5W5P1Y2GKG"></script> <script>
    window.dataLayer = window.dataLayer || []; function gtag(){dataLayer.push(arguments);} gtag('js', new Date());
    gtag('config', ' G-5W5P1Y2GKG'); </script>
    """
    return prefix_google + render_template("index.html",)

@app.route('/', methods = ['POST'])
def hellow_world_input():
    if request.form["submit"] == "Logger":
        return redirect(url_for("logger"))
    return "Oui"

@app.route('/logger')
@app.route('/logger', methods=["GET"])
def logger():
    print('Back-end logs :', file=sys.stderr) # deta logs
    logging.info("Logging test") # 
    script = """
    <script> console.log("Hellow world log") </script>
    """
    return render_template("logger.html") + script

if __name__ == '__main__':
    app.run(debug = True)