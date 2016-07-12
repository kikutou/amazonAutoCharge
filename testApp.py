from flask import Flask, request, render_template, session, redirect
import pickle
import demjson
import codecs
import os

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
    # global the_window
    # the_window = [test.test(url)]
    # print the_window
    #
    the_window = test.test(url)
    # json_window = demjson.encode(the_window)
    # session['opened_window'] = json_window
    # print 'input session'
    print the_window
    return render_template('test.html')


@app.route('/test2', methods=['get'])
def test2():
    return render_template('test2.html')


@app.route('/input_session')
def input_data():
    put = request.args.get('session_data')
    result = test.test(put)
    print result
    return render_template('test2.html')
# def input_session():
#     global the_window
#     return test.fill(the_window[0])
    # session['data'] = request.args.get('session_data')
    # msg = 'session inputted'
    # print msg
    # return msg


@app.route('/clear_session')
def clear_session():
    session.clear()
    print 'session cleared'
    print session
    print 'txt removed'
    f = 'captchaFile.txt'
    if os.path.exists(f):
        os.remove(f)

    return render_template('test.html')

@app.route('/input_text')
def input_text():
    text = request.args.get('text_data')
    print text
    captcha_file = codecs.open('captchaFile.txt', 'w')
    captcha_file.write(text)


    return 'new success'




if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=3090)