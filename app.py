from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

def search_dnsdumpster(target):
    headers = {
        'Pragma': 'no-cache', 
        'Origin': 'https://dnsdumpster.com',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,it;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Cache-Control': 'no-cache',
        'Referer': 'https://dnsdumpster.com/',
        'Connection': 'keep-alive', 'DNT': '1',
    }

    session = requests.Session()
    get_csrf_res = session.get('https://dnsdumpster.com', headers=headers)
    csrf_token = get_csrf_res.cookies['csrftoken']

    data = {
        'csrfmiddlewaretoken': csrf_token, 
        'targetip': target, 
        'user': 'free'
    }

    res = session.post('https://dnsdumpster.com/', headers=headers, data=data, cookies={'csrftoken': csrf_token})
    subdomain_finder = re.compile(r'">(.*\.' + re.escape(target) + ')<br>')
    links = subdomain_finder.findall(res.text)

    domains = list(set([domain.strip() for domain in links if domain.endswith("." + target)]))

    return domains

@app.route('/search_dns', methods=['POST'])
def api_search_dns():
    data = request.json
    if not data or 'target' not in data:
        return jsonify({'error': 'Please provide a target domain'}), 400

    target = data['target']
    domains = search_dnsdumpster(target)
    return jsonify({'domains': domains})

if __name__ == '__main__':
    app.run(debug=True)

