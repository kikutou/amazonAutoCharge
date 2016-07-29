# coding=utf-8
from flask import Flask, request, render_template, session, redirect
import BrowserSaver

import amazonBrowserCopy

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


app = Flask(__name__)

#app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KT'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/amazon')
def amazon():

    user_name = request.args.get('user_name')
    password = request.args.get('password')
    codes = [request.args.get('code0'), request.args.get('code1'), request.args.get('code2')]

    captcha = request.args.get('captcha')


    result = amazonBrowserCopy.amazon_main(user_name, password, codes, captcha)


    if len(result) == 2 and result[1]['code'] == 0:

        browser_list = BrowserSaver.Browsers()
        browser_list.set_browser(user_name, result[1]['browser'])

        return render_template('index.html', captcha=result[0]['htmlcode'])
    else:
        return render_template('amazon.html', result=result)


if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=4000)
