#!/usr/bin/env python

# This file is part of StorageAPI, by Luke Granger-Brown
# and is licensed under the MIT license, under the terms listed within
# LICENSE which is included with the source of this package

import requests


class ApiV1Object(object):
    def __init__(self, api, id):
        self.api = api
        self.object_id = id

        self.info_dict = None

    def info(self):
        if self.info_dict is None:
            self.info_dict = self.api.object_info(self.object_id)
        return self.info_dict

    def delete(self):
        return self.api.object_delete(self.object_id)

    @property
    def url(self):
        return "http://stor.ag/e/" + self.object_id


class ApiV1(object):
    base_url = 'http://api.stor.ag/v1'

    def __init__(self, auth):
        self.client = requests.session()
        self.client.auth = auth

    def build_url(self, url_path):
        return self.base_url + url_path

    def do_request(self, method, url_path, **kwargs):
        url = self.build_url(url_path)
        method_func = getattr(self.client, method.lower())
        return method_func(url, **kwargs)

    def get(self, url_path, **kwargs):
        return self.do_request('GET', url_path, **kwargs)

    def post(self, url_path, **kwargs):
        return self.do_request('POST', url_path, **kwargs)

    def delete(self, url_path, **kwargs):
        return self.do_request('DELETE', url_path, **kwargs)

    def patch(self, url_path, **kwargs):
        return self.do_request('PATCH', url_path, **kwargs)

    def head(self, url_path, **kwargs):
        return self.do_request('HEAD', url_path, **kwargs)

    def put(self, url_path, **kwargs):
        return self.do_request('PUT', url_path, **kwargs)

    def api_status(self):
        return self.get('/status').json()

    def object_delete(self, object_id):
        url_path = '/object/' + object_id
        resp = self.delete(url_path)
        resp.raise_for_status()
        resp_json = resp.json()
        if resp_json['message'] != 'Object deleted.':
            raise Exception("Failed to delete object: " + resp_json['message'])
        return self

    def object_info(self, object_id):
        url_path = '/object/' + object_id
        resp = self.get(url_path)
        resp.raise_for_status()
        resp_json = resp.json()
        return resp_json

    def object_upload(self, file_handle, file_name=None):
        fp = (file_name, file_handle) if file_name is not None else file_handle
        resp = self.post('/object', files={'file': fp})
        resp.raise_for_status()
        resp_json = resp.json()

        if 'id' not in resp_json:
            if 'message' not in resp_json:
                exmsg = "Unknown error"
            else:
                exmsg = resp_json['message']

            raise("Failed to upload file: " + exmsg)

        print(resp_json['id'])
        return ApiV1Object(self, resp_json['id'])

    def object(self, object_id):
        return ApiV1Object(self, object_id)
