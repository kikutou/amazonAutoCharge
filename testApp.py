from flask import Flask, request, render_template, session, redirect, make_response, send_file
import urllib2

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('test.html')

@app.route('/download')
def download():
    url = './trade/201608300609022682/574d0366d1458_3016/after.html'
    response = make_response(send_file(url))
    response.headers["Content-Disposition"] = "attachment; filename=after.html;"
    return response


if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=3090)

