from flask import Flask, render_template
import requests

app = Flask(__name__)

WP_URL = 'http://seusite.com/wp-json/wp/v2/posts'

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
