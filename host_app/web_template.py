
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, \
    flash, jsonify

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template('template.html', poweerMode = 1, heatRunning = 0)

if __name__ == "__main__":
    app.run(debug=True)