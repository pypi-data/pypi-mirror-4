import os
import json
import logging
import urllib2
import urlparse
from collections import namedtuple

import m3u8

Server = namedtuple('Server', 'server port')

def get_servers(playlists):
    return dict([(playlist_name, playlist_data['servers']) for
        playlist_name, playlist_data in playlists['streams'].items()])

def discover_playlists(config):
    '''
    Returns a dictionary of streams to be consumed with the following format:
    {
        'stream1': {
            'input-path': '/h100.m3u8',
            'servers': [Server('http://server1'), Server('http://server3')]
        },
        'stream2': {
            'input-path': '/h200.m3u8',
            'servers': [Server('http://server1')],
        }
    }
    '''
    api_url = config.get('discover', 'api_url')
    playlists = _get_streams_from_url(api_url)
    for playlist, data in playlists['streams'].items():
        data['servers'] = map(_url_to_server, data['servers'])
    return playlists

def _get_streams_from_url(url):
    # FIXME: implement error checking
    return json.load(urllib2.urlopen(url, timeout=30))

def _url_to_server(server):
    parsed_url = urlparse.urlparse(server)
    server_url = '{scheme}://{hostname}'.format(scheme=parsed_url.scheme, hostname=parsed_url.hostname)
    port = parsed_url.port or 80
    return Server(server=server_url, port=port)
