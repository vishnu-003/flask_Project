from flask import Flask, render_template, request,jsonify,redirect
import os
import requests
import bs4 as bs
import urllib.request
from instascrape import Reel 
import time

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'downloads'  # Folder where downloaded files will be stored

@app.route('/')
def index():

    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    print(url)
    print(type(url))

    print("dsfdsfsdfdsdsaasfsdfsdfds")

    headers = {
        'authority': 'fastdl.app',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://fastdl.app',
        'pragma': 'no-cache',
        'referer': 'https://fastdl.app/',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }
    data = {
        'url': f"{url}",
        'lang_code': 'en',
        'token': '',
    }
    response = requests.post('https://fastdl.app/c/', headers=headers, data=data)
    anc=response.text
    # source = urllib.request.urlopen('https://www.instagram.com/reel/CxGEYRBJtFj/?igshid=MzRlODBiNWFlZA==').read()
    print(f"inside---->{url}")
    soup = bs.BeautifulSoup(anc,'lxml')
    for url in soup.find_all('a'):
        href_link=url.get('href')
        print(soup.get_text())
        # download= "<a href={href_link} download>Download Video</ahref_link"
    return (f"<a href={href_link} download>Download Video</ahref_link")


if __name__ == '__main__':
    app.run(debug=True)



            

  

