from flask import Flask, request, render_template, session, redirect
import pickle
import json

import test

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)

app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KT'


@app.route('/')


def index():
    return render_template('test.html')


@app.route('/run_test')


def run_test():
    url = request.args.get('url')
    print url
    result = test.test(url)
    session['opened_window'] = pickle.dumps(result)
    print 'input session'

    return render_template('test.html')


@app.route('/clear_session')

def clear_session():
    session.clear()
    print 'session cleared'
    return render_template('test.html')



if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=3000)