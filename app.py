from flask import Flask, render_template
import requests
import xml.etree.ElementTree as ET
import os

app = Flask(__name__)

WP_BASE_URL = 'http://seusite.com/wp-json/wp/v2'

XML_FILE_PATH = 'data/posts_cache.xml'

if not os.path.exists('data'):
    os.makedirs('data')

def create_xml_from_posts(posts_data):
    root = ET.Element('posts')
    root.set('source', 'WordPress API')

    for post in posts_data:
        post_element = ET.SubElement(root, 'post')
        post_element.set('id', str(post['id']))
        post_element.set('status', post['status'])
        
        ET.SubElement(post_element, 'title').text = post['title']['rendered']
        ET.SubElement(post_element, 'date').text = post['date'][:10]
        ET.SubElement(post_element, 'link').text = post['link']
        
    tree = ET.ElementTree(root)
    tree.write(XML_FILE_PATH, encoding='utf-8', xml_declaration=True)
    
    print(f"Dados salvos com sucesso em {XML_FILE_PATH}")

def read_posts_from_xml():
    posts_list = []
    
    if not os.path.exists(XML_FILE_PATH):
        return None

    try:
        tree = ET.parse(XML_FILE_PATH)
        root = tree.getroot()

        for post_element in root.findall('post'):
            post = {
                'id': post_element.get('id'),
                'status': post_element.get('status'),
                'title': {'rendered': post_element.find('title').text}, 
                'date': post_element.find('date').text,
                'link': post_element.find('link').text
            }
            
            posts_list.append(post)
        return posts_list

    except ET.ParseError as e:
        print(f"Erro ao analisar o arquivo XML: {e}")
        return None

@app.route('/')

def dashboard():
    posts_data = []
    error_message = None
    
    try:
        endpoint = f'{WP_BASE_URL}/posts'
        
        params = {'per_page': 5, 'status': 'publish', '_fields': 'id,title,status,date,link'}
        
        response = requests.get(endpoint, params=params)
        response.raise_for_status() 
        
        posts_data = response.json()
        
        if posts_data:
            create_xml_from_posts(posts_data)

    except requests.RequestException as e:
        error_message = f"Erro ao conectar à API WP. Tentando ler do cache XML. Detalhe: {e}"
        xml_cache = read_posts_from_xml()
        
        if xml_cache is not None:
            posts_data = xml_cache
            error_message = "Dados carregados com sucesso do cache XML."
            
        else:
            error_message = "Falha total: Não foi possível conectar à API e o cache XML está indisponível."

    return render_template('dashboard.html', posts=posts_data, error=error_message)

if __name__ == '__main__':
    app.run(debug=True)
