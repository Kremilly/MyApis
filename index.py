from apis.cve import CVE
from apis.qrcode import QRCode
from apis.github import GitHub
from apis.pdf_info import PDFInfo
from apis.pdf_thumb import PDFThumb
from apis.wikipedia import Wikipedia
from apis.pdf_scrape import PDFScrape
from apis.readme import ReadmeDevToPosts
from apis.stats_langs import GitHubStatsLangs

from kremilly.kremilly import Kremilly

from flask import Flask, request

app = Flask(__name__)

kremilly = Kremilly(app, {
    'repo': 'MyApis',
    'github': 'Kremilly',
    'domain': 'kremilly.com',
})

@app.route('/')
@app.route('/json')
def index():
    return kremilly.list_json()

@app.route('/rss')
def rss():
    return kremilly.rss()

@app.route('/github', methods=['GET'])
def github():
    return GitHub({
        'user': request.args.get('user')
    }).get()
    
@app.route('/statslangs', methods=['GET'])
def statslangs():
    return GitHubStatsLangs({
        'user': request.args.get('user'),
        'forks': request.args.get('forks'),
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
    
@app.route('/pdfscrape', methods=['GET'])
def pdfscrape():
    return PDFScrape({
        'url': request.args.get('url')
    }).get()

@app.route('/pdfinfo', methods=['GET'])
def pdfinfo():
    return PDFInfo({
        'pdf': request.args.get('pdf')
    }).get()
    
@app.route('/devto', methods=['GET'])
def devto():
    return ReadmeDevToPosts({
        'color': request.args.get('color'),
        'username': request.args.get('username'),
    }).get()

if __name__ == '__main__':
    app.run(debug=True)