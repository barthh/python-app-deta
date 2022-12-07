from flask import Flask, render_template

app = Flask(__name__)

@app.route('/', methods=["GET"])
def hello_world():
    prefix_google = """
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-5W5P1Y2GKG"></script> <script>
    window.dataLayer = window.dataLayer || []; function gtag(){dataLayer.push(arguments);} gtag('js', new Date());
    gtag('config', ' G-5W5P1Y2GKG'); </script>
    """
    return prefix_google + "HelloW World"