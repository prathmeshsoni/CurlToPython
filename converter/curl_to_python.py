import json

import requests
import uncurl
import os

class CurlToPython:
    def __init__(self, curlstr):
        self.curlstr = f'{curlstr}'.strip().replace('\\', '')
        self.converted = uncurl.parse_context(self.curlstr)
        # self.main_request()

    def get_cookies(self, check=None):
        if check:
            cookies = check.cookies
            return cookies

        cookies = self.converted.cookies
        return cookies

    def get_header(self, check=None):
        if check:
            header = check.headers
            return header

        header = self.converted.headers
        return header

    def get_data(self):
        data = self.converted.data
        return data

    def get_url(self, check=None):
        if check:
            url = check.url
            return url

        url = self.converted.url
        return url

    def get_method(self, check=None):
        method = self.converted.method
        return method

    def main_request(self):
        method = self.get_method()
        url = self.get_url()
        headers = self.get_header()
        cookies = self.get_cookies()
        data = self.get_data()

        print('Method =', method)
        print('URL =', url)
        print('Headers =', headers)
        print('Cookies =', cookies)
        print('Data =', data)

        response = requests.request(
            method, url,
            headers=headers,
            cookies=cookies,
            data=data
        )

        path = self.download_response(response.text)
        print('Status Code =', response.status_code)
        print('Cookies =', self.get_cookies(response))
        print('Header =', self.get_header(response))
        print('url =', self.get_url(response))
        # print(self.get_converted_str())
        return path

    def get_converted_str(self):
        return self.get_str()

    def download_response(self, text):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        final_path = os.path.join(base_dir, 'converter')
        
        f_name = f'{self.get_url()}'.replace('https://', '').replace('http://', '').replace('/', '_')
        if f_name.endswith('_'):
            f_name = f_name[:-1]

        if not os.path.exists(f'{final_path}/response'):
            os.makedirs(f'{final_path}/response')
        
        file_name = f'response-{f_name}.html'
        with open(f'{final_path}/response/{file_name}', 'w', encoding='utf-8') as f:
            f.write(text)

        domain_url = 'http://127.0.0.1:5000'
        return f'{domain_url}/converter/response/{file_name}'

    def get_str(self, **kargs):
        BASE_INDENT = " " * 4
        parsed_context = uncurl.parse_context(self.curlstr)

        data_token = ''
        if parsed_context.data:
            data_token = '{}data=\'{}\',\n'.format(BASE_INDENT, parsed_context.data)

        verify_token = ''
        if parsed_context.verify:
            verify_token = '\n{}verify=False'.format(BASE_INDENT)

        requests_kargs = ''
        for k, v in sorted(kargs.items()):
            requests_kargs += "{}{}={},\n".format(BASE_INDENT, k, str(v))

        auth_data = "{}auth={}".format(BASE_INDENT, parsed_context.auth)

        formatter = {
            'method': parsed_context.method,
            'url': parsed_context.url,
            'data_token': data_token,
            'headers_token': "{}headers = {}".format("", self.dict_to_pretty_string(parsed_context.headers)),
            'cookies_token': "{}cookies = {}".format("", self.dict_to_pretty_string(parsed_context.cookies)),
            'security_token': verify_token,
            'requests_kargs': requests_kargs,
            'auth': auth_data,
        }
        if parsed_context.data:
            formatter['json_data_token'] = "{}json_data = {}".format("",
                                                                     self.dict_to_pretty_strings(parsed_context.data))
            formatter['json_data_token'] = formatter['json_data_token'].replace('    }', '}').replace('        ',
                                                                                                      '    ')
        formatter['headers_token'] = formatter['headers_token'].replace('    }', '}').replace('        ', '    ')
        formatter['cookies_token'] = formatter['cookies_token'].replace('    }', '}').replace('        ', '    ')

        if parsed_context.data:
            return """
{cookies_token}

{headers_token}

{json_data_token}

response = requests.{method}("{url}", cookies=cookies, headers=headers, json=json_data)
print(response.text)
""".format(**formatter)
        else:
            return """
{cookies_token}

{headers_token}

response = requests.{method}("{url}", cookies=cookies, headers=headers)
print(response.text)
""".format(**formatter)

    def dict_to_pretty_string(self, the_dict, indent=4):
        if not the_dict:
            return "{}"

        return ("\n" + " " * indent).join(
            json.dumps(the_dict, sort_keys=True, indent=indent, separators=(',', ': ')).splitlines())

    def dict_to_pretty_strings(self, the_dict, indent=4):
        return ("\n" + " " * indent).join(
            json.dumps(json.loads(the_dict), sort_keys=True, indent=indent, separators=(',', ': ')).splitlines())


if __name__ == '__main__':
    curl_command = """
        curl 'https://prathmeshsoni.works/' \
            -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \
            -H 'accept-language: en-US,en;q=0.9' \
            -H 'sec-ch-ua: "Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"' \
            -H 'sec-ch-ua-mobile: ?0' \
            -H 'sec-ch-ua-platform: "Windows"' \
            -H 'sec-fetch-dest: document' \
            -H 'sec-fetch-mode: navigate' \
            -H 'sec-fetch-site: none' \
            -H 'sec-fetch-user: ?1' \
            -H 'upgrade-insecure-requests: 1' \
            -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    """

    converted = CurlToPython(curl_command).get_converted_str()
    response = CurlToPython(curl_command).main_request()
    print(converted)
    print(response)
