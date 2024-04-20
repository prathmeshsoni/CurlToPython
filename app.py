from flask import Flask, request, jsonify, render_template, send_from_directory, redirect, session
import os
from converter.curl_to_python import CurlToPython
import uuid

database = {}

app = Flask(__name__)
app.secret_key = '9202c558s9c7a4ds42vf96f4f9bf464240acfbb9'


# Redirect to a specific URL for 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return redirect('/')


# Home Page
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        check = request.get_json().get('check', '')
        curl = request.get_json().get('curl_code', '')
        s = 1 if curl else 0

        if s == 0:
            return jsonify({'code': f'Error: command should begin with "curl" but instead begins with "{curl}"'})

        try:
            main_data = ''
            if check:
                try:
                    main_data = CurlToPython(curl).main_request()
                except Exception as e:
                    print('Error:', e)

            datas = CurlToPython(curl).get_converted_str()
        except:
            datas = f'Error: command should begin with "curl" but instead begins with "{curl}"'

        items = {'code': datas}
        if check:
            items['url'] = main_data

        return jsonify(items)

    else:
        return render_template('home.html')


@app.route('/html-viewer/', methods=['GET', 'POST'])
def html_viewer():
    if request.method == 'POST':
        html_code = request.get_json().get('html_code', '')
        data_id = str(uuid.uuid4())
        
        database[data_id] = html_code
        
        session['data_id'] = data_id
        
        items = {'link': '/html-viewer/'}
        return jsonify(items)

    else:
        data_id = session.get('data_id')
        
        html_code = database.get(data_id, '')
        
        if html_code:
            data = html_code
        else:
            data = '<h1>Hello World!!</h1>'
            
        items = {'data': data}
        return render_template('html_viewer.html', items=items)


# Response Page
@app.route('/converter/response/<path:filename>')
def protected_serve(filename):
    directory = os.path.join(app.root_path, 'converter/response/')
    return send_from_directory(directory, filename)


if __name__ == '__main__':
    app.run(debug=True)
