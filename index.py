from apis.cve import CVE
from apis.qrcode import QRCode
from apis.github import GitHub
from apis.sci_hub import SciHub
from apis.pdf_thumb import PDFThumb
from apis.wikipedia import Wikipedia
from apis.pdf_info import PDFInfo

from flask import Flask, request, render_template

app = Flask(__name__)

def list_apis():
    endpoints = []
    
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'index' and rule.endpoint != 'static':
            endpoints.append('/' + rule.endpoint)
        
    return sorted(endpoints)

@app.route('/')
def index():
    return render_template(
        'index.html',
        list_apis=list_apis(),
        
        github_user='Kremilly',
        crates_user='Kremilly',
        pypi_user='thesilvaemily',
        packagist_user='Kremilly',
        website_domain='kremilly.com',
        email_user='contact@kremilly.com',
        
        wiki_docs='https://github.com/kremilly/MyApis/wiki',
    )

@app.route('/github', methods=['GET'])
def github():
    return GitHub({
        'user': request.args.get('user')
    }).get()

@app.route('/qrcode', methods=['GET'])
def qrcode():
    return QRCode({
        'url': request.args.get('url')
    }).get()

@app.route('/pdfthumb', methods=['GET'])
def pdfthumb():
    return PDFThumb({
        'pdf': request.args.get('pdf'),
        'page': request.args.get('page'),
        'width': request.args.get('width'),
        'height': request.args.get('height'),
    }).get()

@app.route('/wikipedia', methods=['GET'])
def wikipedia():
    return Wikipedia({
        'term': request.args.get('term'),
        'location': request.args.get('location'),
        'thumb_size': request.args.get('thumb_size'),
        'short_summary': request.args.get('short_summary'),
    }).get()   

@app.route('/cve', methods=['GET'])
def cve():
    return CVE({
        'id': request.args.get('id')
    }).get()

@app.route('/scihub', methods=['GET'])
def scihub():
    return SciHub({
        'paper': request.args.get('paper')
    }).get()

if __name__ == '__main__':
    app.run()
