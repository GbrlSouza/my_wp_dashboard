import os
import json
import base64
import requests
import xml.etree.ElementTree as ET

from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash

load_dotenv()

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

WP_URL = 'http://seusite.com/wp-json/wp/v2'
WP_USERNAME = "seu_usuario_api"
WP_APP_PASSWORD = "sua_senha_de_aplicacao"

XML_FILE_PATH = 'data/posts_cache.xml'

if not os.path.exists('data'):
    os.makedirs('data')
    
def get_auth_headers():
    credentials = f"{WP_USERNAME}:{WP_APP_PASSWORD}"
    token = base64.b64encode(credentials.encode()).decode('utf-8')
    
    return {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json"
    }

def create_xml_from_posts(posts_data):
    root = ET.Element('posts')
    root.set('source', 'WordPress API')

    for post in posts_data:
        post_element = ET.SubElement(root, 'post')
        post_element.set('id', str(post.get('id', '')))
        post_element.set('status', post.get('status', ''))
        
        title_text_raw = post.get('title', {}).get('raw', post.get('title', {}).get('rendered', ''))
        content_text_raw = post.get('content', {}).get('raw', post.get('content', {}).get('rendered', ''))
        
        ET.SubElement(post_element, 'title_rendered').text = post.get('title', {}).get('rendered', '')
        ET.SubElement(post_element, 'title_raw').text = title_text_raw
        ET.SubElement(post_element, 'content_raw').text = content_text_raw
        ET.SubElement(post_element, 'date').text = post.get('date', '')[:10]
        ET.SubElement(post_element, 'link').text = post.get('link', '')
        
    tree = ET.ElementTree(root)
    tree.write(XML_FILE_PATH, encoding='utf-8', xml_declaration=True)

def read_posts_from_xml():
    posts_list = []
    
    if not os.path.exists(XML_FILE_PATH):
        return None 
        
    try:
        tree = ET.parse(XML_FILE_PATH)
        root = tree.getroot()
        
        for post_element in root.findall('post'):
            posts_list.append({
                'id': int(post_element.get('id', 0)),
                'status': post_element.get('status', ''),
                'title': {'rendered': post_element.find('title_rendered').text, 'raw': post_element.find('title_raw').text}, 
                'content': {'rendered': '', 'raw': post_element.find('content_raw').text}, 
                'date': post_element.find('date').text,
                'link': post_element.find('link').text
            })
            
        return posts_list
        
    except (ET.ParseError, AttributeError) as e:
        return None

@app.route('/')
def dashboard():
    headers = get_auth_headers()
    posts_data = []
    
    try:
        response = requests.get(f"{WP_URL}/posts?_fields=id,title,status,date,link,content&per_page=20", headers=headers)
        response.raise_for_status()
        
        posts_data = response.json()
        
        if posts_data:
            create_xml_from_posts(posts_data)
        
        flash("Posts carregados com sucesso da API do WordPress.", 'info')

    except requests.exceptions.RequestException as e:
        xml_cache = read_posts_from_xml()
        
        if xml_cache is not None:
            posts_data = xml_cache
            flash("Erro ao conectar à API WP. Dados carregados do cache XML.", 'warning')
            
        else:
            flash(f"Falha total: Não foi possível conectar à API e o cache XML está indisponível.", 'danger')

    return render_template('dashboard.html', posts=posts_data)

@app.route('/new_post', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        status = request.form.get('status', 'draft')
        
        post_data = {
            "title": title,
            "content": content,
            "status": status,
        }
        
        headers = get_auth_headers()
        
        try:
            response = requests.post(f"{WP_URL}/posts", headers=headers, json=post_data)
            response.raise_for_status()
            
            flash(f"Post '{title}' criado com sucesso!", 'success')
            
            return redirect(url_for('dashboard'))
            
        except requests.exceptions.RequestException as e:
            error_message = response.json().get('message', str(e))
            
            flash(f"Erro ao criar o post na API: {error_message}", 'danger')
            
            return render_template('post_form.html', action='Criar Novo Post', post=post_data, post_id=None)

    return render_template('post_form.html', action='Criar Novo Post', post=None, post_id=None)

@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    headers = get_auth_headers()
    
    if request.method == 'GET':
        try:
            response = requests.get(f"{WP_URL}/posts/{post_id}", headers=headers)
            response.raise_for_status()
            post = response.json()
            
            return render_template('post_form.html', action='Editar Post', post=post, post_id=post_id)
            
        except requests.exceptions.RequestException as e:
            flash(f"Erro ao buscar post {post_id}: {e}", 'danger')
            
            return redirect(url_for('dashboard'))

    elif request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        status = request.form.get('status')
        
        update_data = {
            "title": title,
            "content": content,
            "status": status,
        }
        
        try:
            response = requests.post(f"{WP_URL}/posts/{post_id}", headers=headers, json=update_data)
            response.raise_for_status()
            
            flash(f"Post '{title}' atualizado com sucesso!", 'success')
            
            return redirect(url_for('dashboard'))
            
        except requests.exceptions.RequestException as e:
            error_message = response.json().get('message', str(e))
            
            flash(f"Erro ao atualizar o post {post_id}: {error_message}", 'danger')
            
            submitted_post_data = {'title': {'rendered': title}, 'content': {'raw': content}, 'status': status}
            
            return render_template('post_form.html', action='Editar Post', post_id=post_id, post=submitted_post_data)

@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    headers = get_auth_headers()
    
    try:
        response = requests.delete(f"{WP_URL}/posts/{post_id}?force=true", headers=headers)
        response.raise_for_status()
        
        flash(f"Post ID {post_id} excluído permanentemente.", 'success')
        
    except requests.exceptions.RequestException as e:
        error_message = response.json().get('message', str(e))
        
        flash(f"Erro ao excluir post {post_id}: {error_message}", 'danger')

    return redirect(url_for('dashboard'))
    
if __name__ == '__main__':
    app.run(debug=True)
