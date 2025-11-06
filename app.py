from flask import Flask, render_template
import requests

app = Flask(__name__)

WP_BASE_URL = 'http://seusite.com/wp-json/wp/v2'

@app.route('/')

def dashboard():
    posts_recentes = []

    try:
        endpoint = f'{WP_BASE_URL}/posts'
        
        params = {
            'per_page': 5,
            'status': 'publish',
            '_fields': 'id,title,status,date,link'
        }
        
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        posts_recentes = response.json()
        
    except requests.RequestException as e:
        print(f"Erro ao obter posts do WordPress: {e}")
        error_message = f"Não foi possível conectar ao WordPress: {e}"
        
        return render_template('dashboard.html', posts=[], error=error_message)

    return render_template('dashboard.html', posts=posts_recentes)

if __name__ == '__main__':
    app.run(debug=True)
