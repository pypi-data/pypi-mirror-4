# Copyright (C) 2009, 2010  Red Hat, Inc.
#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.  The
# ASF licenses this file to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the
# License.  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations
# under the License.

import urllib
try:  # Python 2
    from urlparse import urljoin
except ImportError:  # Python 3
    from urllib.parse import urljoin

import requests


class Deltacloud(object):
    """Simple Deltacloud client"""

    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password
        self.entrypoints = self.discover_entrypoints()

    def request(self, path='', params=None, method='get'):
        url = urljoin(self.url, path)
        resp = requests.request(method, url,
                auth=(self.username, self.password),
                params=params,
                headers={
                    'accept': 'application/json',
                })
        resp.raise_for_status()
        json = None
        if hasattr(resp.json, '__call__'):  # Current `requests` releases
            if resp.text:
                json = resp.json()
        else:  # Legacy `requests` versions
            json = resp.json
        return resp, json

    def valid_credentials(self):
        try:
            self.request('', {'force_auth': 1})
            return True
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                return False
            raise

    def discover_entrypoints(self):
        status, doc = self.request('')
        links = [(link['rel'], link['href']) for link in doc['api']['links']]
        return dict(links)

    def hardware_profiles(self):
        status, doc = self.request(self.entrypoints['hardware_profiles'])
        return [HardwareProfile(self, profile) for profile in
                doc.get('hardware_profiles', [])]

    def realms(self):
        status, doc = self.request(self.entrypoints['realms'])
        return [Realm(self, realm) for realm in doc.get('realms', [])]

    def images(self):
        status, doc = self.request(self.entrypoints['images'])
        return [Image(self, image) for image in doc.get('images', [])]

    def keys(self):
        status, doc = self.request(self.entrypoints['keys'])
        return [Key(self, key) for key in doc.get('keys', [])]

    def instances(self, id=None):
        instances_url = self.entrypoints['instances']
        if id:
            single_instance_url = instances_url + '/' + urllib.quote_plus(id)
            response, body = self.request(single_instance_url)
            return Instance(self, body['instance'])
        else:
            response, doc = self.request(instances_url)
            return [Instance(self, instance) for instance in
                    doc.get('instances', [])]

    def create_instance(self, image_id, opts=None):
        if opts is None:
            opts = {}
        opts['image_id'] = image_id
        response, doc = self.request(self.entrypoints['instances'], opts, 'post')
        instance = get_in_dict(doc, ['instance'])
        return Instance(self, instance)

def get_in_dict(dictionary, path, default=None):
    '''
    Return the value at the path in the nested dictionary.

    If the path isn't available, return the default value instead.
    '''
    if not path:
        return default
    if not dictionary:
        return default
    if len(path) == 1:
        return dictionary.get(path[0], default)
    return get_in_dict(dictionary.get(path[0], {}), path[1:], default)


class Instance(Deltacloud):

    def __init__(self, deltacloud, instance):
        self.instance, self.deltacloud = instance, deltacloud

    @property
    def id(self):
        return self.instance['id']

    @property
    def name(self):
        return self.instance['name']

    @property
    def state(self):
        return self.instance['state']

    @property
    def owner_id(self):
        return self.instance['owner_id']

    @property
    def public_addresses(self):
        return self.instance['public_addresses']

    @property
    def private_addresses(self):
        return self.instance['private_addresses']

    @property
    def login(self):
        return get_in_dict(instance, ['authentication', 'login'], {})

    @property
    def authentication_type(self):
        return get_in_dict(instance, ['authentication', 'type'])

    @property
    def key_name(self):
        return self.instance['keyname']

    @property
    def username(self):
        return self.instance['username']

    @property
    def password(self):
        return self.instance['password']


    def start(self):
        return self.do_action('start')

    def stop(self):
        return self.do_action('stop')

    def reboot(self):
        return self.do_action('reboot')

    def destroy(self):
        return self.do_action('destroy')

    def actions(self):
        '''Return all the actions allowed on the instance.'''
        return [link['rel'] for link in self.instance.get('actions', [])]

    def do_action(self, action):
        '''Run the specified action.'''
        if not action in self.actions():
            return False
        action_links = [link for link in self.instance['actions']
                        if link['rel'] == action]
        action = action_links[0]
        url = action['href']
        method = action['method']
        response, body = self.deltacloud.request(url, method=method)
        if response.status_code >= 400:
            return False
        if body and 'id' in body:
            self.instance = body
        return True

    def refresh(self):
        response, body = self.deltacloud.request(self.instance['href'])
        if response.status_code >= 400:
            return
        if body and 'instance' in body:
            self.instance = body['instance']


class Image(Deltacloud):

    def __init__(self, client, image):
        self.id = image["id"]
        self.name = image["name"]
        self.state = image["state"]
        self.owner = image["owner"]
        self.architecture = image["architecture"]
        self.description = image["description"]

class Key(Deltacloud):

    def __init__(self, client, key):
        self.id = key["id"]
        # TODO: JSON doesn't return the key name. We need to fix that
        # self.name = key["name"]
        self.name = key["id"]
        self.fingerprint = key["fingerprint"]
        self.pem = key["pem_rsa_key"]

class Realm(Deltacloud):

    def __init__(self, client, realm):
        self.id = realm['id']
        self.name = realm['name']
        self.state = realm['state']


class HardwareProfile(Deltacloud):

    def __init__(self, client, profile):
        self.id = profile['id']
        self.name = profile['name']
        self.properties = [HardwareProfileProperty(profile, prop) for prop in
                           profile.get('property', [])]


class HardwareProfileProperty(HardwareProfile):

    def __init__(self, profile, prop):
        self.name  = prop['name']
        self.kind  = prop['kind']
        self.unit  = prop['unit']
        self.value = prop['value']
        if 'enum' in prop:
            self.enums = [enum['value'] for enum in prop['enum']['entry']]
        if 'range' in prop:
            self.range_min = prop['range']['first']
            self.range_max = prop['range']['last']
