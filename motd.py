#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#https://home.openweathermap.org/users


#import requests
import json 
import pystache
import time
import http.client
import os.path
from datetime import datetime
from datetime import date

API_KEY = "878de2eb13352fabdc825fc0438dcac6"
BASE_URL = "api.openweathermap.org"

#Bash formatting styles
BASH_STYLES = {
  'HEADER': '\033[95m',
  'OKBLUE': '\033[94m',
  'OKGREEN': '\033[92m',
  'WARNING': '\033[93m',
  'FAIL': '\033[91m',
  'ENDC': '\033[0m',
  'BOLD': '\033[1m',
  'UNDERLINE': '\033[4m'
}

class OpenWeatherAPI(object): 

  def request_weather( self, city ):
    with CachedHttpRequest( city ) as response:
      output = ''

      if response.get('status') == 200:
        output = self._format_output( response.get('data') )
      else:
        output = self._format_not_found( response )
          
      print( output )

  def read_template(self):
    with open('motd.mustache','r') as template_file:
      return template_file.read()

  def _format_not_found( self, response):
    return response.get('msg')

  def _format_output( self, response ):
    template = self.read_template()

    now = datetime.now()
    currenttime = now.strftime("%-d.%-m.%Y %H:%M")

    date_format = '%H:%M'
    ts = response.get('sys').get('sunrise') + response.get('timezone')
    sunrise = datetime.utcfromtimestamp(ts).strftime(date_format)
    ts = response.get('sys').get('sunset') + response.get('timezone')
    sunset = datetime.utcfromtimestamp(ts).strftime(date_format)

    output = pystache.render(template, {
      'currenttime': currenttime,
      'response': response,
      'sunset': sunset,
      'sunrise': sunrise,
      'BASH': BASH_STYLES,
      'c': u'\N{DEGREE SIGN}C'
    })

    return output

  def _debug(self, data):
    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(data)
      

class CachedHttpRequest(object):

  def __init__(self, city="Tampere", force=False, cache_time = 60):
    self._city = city
    self._force = force
    self._temp_file_path = '/var/tmp/motd-py-temp-response.json'
    self._cache_age = cache_time#s

  def make_http_request(self, city):
    url ="/data/2.5/weather?appid={API_KEY}&q={city}&units=metric".format( BASE_URL=BASE_URL, API_KEY=API_KEY, city=city )    
    conn = http.client.HTTPConnection(BASE_URL)
    conn.request("GET", url)
    response = conn.getresponse()    
    data = response.read()
    conn.close()    
    return { 'status': response.status, 'data': json.loads(data), 'time': time.time() }

  def cached_file_exist(self):
    return os.path.isfile(self._temp_file_path)

  def load_cached_response(self):
    with open(self._temp_file_path, 'r') as rawfile:
      cached_reponse = json.loads( rawfile.read() )
      cached_reponse['cached'] = True
      return cached_reponse

  def is_cache_expired(self):    
    response = self.load_cached_response()
    is_expired = response.get('time') + self._cache_age < time.time()
    return is_expired

  def _store_response(self, response):
    with open(self._temp_file_path, 'w') as rawfile:
      rawfile.write( json.dumps( response) )
    return response    

  def __enter__(self):
    if self._force or (not self.cached_file_exist()) or (self.cached_file_exist() and self.is_cache_expired()):
      response = self.make_http_request(self._city)      
      
      if response.get('status') == 200:
        return self._store_response( response )
      else:
        return response
    
    return self.cached_file_exist() and self.load_cached_response()

  def __exit__(self, type, value, traceback):
    return None

if __name__ == "__main__":
    
  api = OpenWeatherAPI()
  api.request_weather('Tampere')