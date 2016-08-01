from flask import Flask, request, render_template, session, redirect
import pickle
# import demjson
import time
import codecs
import os
import BrowserSaver

import test

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)

app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KT'


@app.route('/')
def index():
    return render_template('amazontest/test.html')

# @app.route('/one')
# def one():
#     browser_list = Browsers.Browsers()
#     browser_list.set_browser(5,'hahahhaha')
#
#     return render_template('test.html')
#
# @app.route('/two')
# def two():
#     browser_list = Browsers.Browsers()
#     print browser_list.get_browser(5)
#     return render_template('test.html')

@app.route('/ajaxtest', methods=['get'])
def ajaxtest():
    str = 'ajajajajajajajajaj'
    return str


@app.route('/run_test')
def run_test():
    url = request.args.get('url')
    print url
    the_window = test.test(url)
    json = pickle.dumps(the_window)
    session['the_browser'] = json
    print session
    return 'window input'


@app.route('/test2', methods=['get'])
def test2():
    return render_template('test2.html')


@app.route('/input_session')
def input_data():
    put = request.args.get('session_data')

    return test.input_test(put)
    # result = test.test(put)
    # print result
    # return render_template('test2.html')


@app.route('/clear_session')
def clear_session():
    session.clear()
    print 'session cleared'
    print session

    return render_template('test.html')

@app.route('/input_text')
def input_text():
    text = request.args.get('text_data')
    print text
    captcha_file = codecs.open('captchaFile.txt', 'w')
    captcha_file.write(text)

    return 'new success'


@app.route('/thetest')
def thetest():
    render_template('amazontest/index.html')
    time.sleep(5)
    return redirect('/thetest2?msg="aaaa"')


@app.route('/thetest2')
def thetest2():
    msg = request.args.get('msg')
    if msg:
        print msg

    else:
        print 'nononono'
    return render_template('amazontest/test2.html')


if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=3090)

