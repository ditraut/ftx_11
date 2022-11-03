import time
import urllib.parse
from typing import Optional, Dict, Any, List
from requests import Request, Session, Response
import hmac
from requests_toolbelt.adapters import source


class FtxClient:
    _ENDPOINT = 'https://ftx.com/api/'

    def __init__(self, api_key='my_key', api_secret='my_secret', subaccount_name=None) -> None:
        self.source_adapt = source.SourceAddressAdapter('192.168.100.40')
        self._session = Session().mount('https://', self.source_adapt)
        #self._session = Session() 
        self._api_key = api_key
        self._api_secret = api_secret
        self._subaccount_name = subaccount_name

    def _post(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('POST', path, json=params)

    def _request(self, method: str, path: str, **kwargs) -> Any:
        request = Request(method, self._ENDPOINT + path, **kwargs)
        self._sign_request(request)
        response = self._session.send(request.prepare())
        return self._process_response(response)

    def _sign_request(self, request: Request) -> None:
        ts = int(time.time() * 1000)
        prepared = request.prepare()
        signature_payload = f'{ts}{prepared.method}{prepared.path_url}'.encode()
        if prepared.body:
            signature_payload += prepared.body
        signature = hmac.new(self._api_secret.encode(), signature_payload, 'sha256').hexdigest()
        request.headers['FTX-KEY'] = self._api_key
        request.headers['FTX-SIGN'] = signature
        request.headers['FTX-TS'] = str(ts)
        if self._subaccount_name:
            request.headers['FTX-SUBACCOUNT'] = urllib.parse.quote(self._subaccount_name)

    def _process_response(self, response: Response) -> Any:
        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            raise
        else:
            if not data['success']:
                raise Exception(data['error'])
            return data['result']

    def add_ip(self) -> dict:
        return self._post('direct_access_settings/add_ip', {
            'name': "'test_15.29.277.230'",
            'ip': "15.29.277.230"
        })


def main():
    client = FtxClient()
    add_ip = client.add_ip()
    print(add_ip)


if __name__ == '__main__':
    main()