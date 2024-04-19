from flask import Flask, request, jsonify, render_template, send_from_directory, redirect
import os
from converter.curl_to_python import CurlToPython

app = Flask(__name__)


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
            if check:
                main_data = CurlToPython(curl).main_request()

            datas = CurlToPython(curl).get_converted_str()
        except:
            datas = f'Error: command should begin with "curl" but instead begins with "{curl}"'

        items = {'code': datas}
        if check:
            items['url'] = main_data

        return jsonify(items)

    else:
        return render_template('home.html')


# Response Page
@app.route('/converter/response/<path:filename>')
def protected_serve(filename):
    directory = os.path.join(app.root_path, 'converter/response/')
    return send_from_directory(directory, filename)


if __name__ == '__main__':
    app.run(debug=True)
