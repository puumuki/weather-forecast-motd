#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#https://home.openweathermap.org/users

import urllib
import json 
import pystache
import time
import http.client
import os.path
from datetime import datetime
from datetime import date
from os.path import expanduser
import configparser
from datetime import timedelta
import logging

#Get logger ready for use.
logger = logging.getLogger('motd')

BASE_PATH = os.path.abspath(os.path.dirname(__file__))

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

  def request_weather( self, city, force ):
    logger.debug("Loading settings")
    with Settings() as settings:    
      logger.debug( dict(settings.items('Default')) )

      city = city if city else settings.get('Default','CITY')
      
      logger.debug( "Instantiating CachedHttpRequest" )
      with CachedHttpRequest( city=city, 
                              cache_time=settings.getint('Default','CACHE_TIME'), 
                              api_key=settings.get('Default','API_KEY'),
                              force=force  ) as response:
        output = ''

        if response.get('status') == 200:
          output = self._format_output( response.get('data') )
        else:
          output = self._format_not_found( response )
            
        print( output )

  def read_template(self):
    
    with open( os.path.join( BASE_PATH, 'data', 'motd.mustache'),'r') as template_file:
      return template_file.read()

  def _format_not_found( self, response):
    return response.get('msg')

  def _format_output( self, response ):
    systeminformation = SystemInformation()

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
      'system': systeminformation.info(),
      'c': u'\N{DEGREE SIGN}C'
    })

    return output

class SystemInformation(object):

  def uptime(self):
    with open('/proc/uptime', 'r') as f:
      s = float(f.readline().split()[0])
      hours, remainder = divmod(s, 3600)
      minutes, seconds = divmod(remainder, 60)
      return '{:02}h {:02}min {:02}s'.format(int(hours), int(minutes), int(seconds))
      

  def info(self):
    return {
      'uptime': self.uptime()
    }

class CachedHttpRequest(object):

  def __init__(self, city="Tampere", api_key="", cache_time=60, force=False):
    self._city = city
    self._force = force
    self._api_key = api_key
    self._temp_file_path = '/var/tmp/motd-py-temp-response.json'
    self._cache_age = cache_time

  def make_http_request(self, city):
    logger.debug( "Making a new http request to weather api" )
    url ="/data/2.5/weather?appid={API_KEY}&q={city}&units=metric".format( 
      BASE_URL=BASE_URL, 
      API_KEY=self._api_key, 
      city=urllib.parse.quote( city )
    )

    conn = http.client.HTTPConnection(BASE_URL)
    conn.request("GET", url)
    response = conn.getresponse()    
    data = response.read().decode("utf-8") 
    conn.close()    
    return { 'status': response.status, 'data': json.loads(data), 'time': time.time() }

  def load_cached_response(self):
    logger.debug( "Returning cached request" )
    with open(self._temp_file_path, 'r') as rawfile:
      cached_reponse = json.loads( rawfile.read() )
      cached_reponse['cached'] = True
      return cached_reponse

  def is_cache_expired(self):    
    response = self.load_cached_response()
    cached_city_differences = response.get('city') != self._city
    is_expired = cached_city_differences or (response.get('time') + self._cache_age < time.time())
    logger.debug( "Is cached request expired - " + str(is_expired))
    logger.debug( "Cache is " + str(int(time.time() - response.get('time'))) + " s old")
    return is_expired

  def _store_response(self, response):
    logger.debug("Caching the HTTP-request")
    with open(self._temp_file_path, 'w') as rawfile:
      rawfile.write( json.dumps( response) )
    return response    

  def __enter__(self):
    cache_file_exist = os.path.isfile(self._temp_file_path)

    if self._force or (not cache_file_exist) or (cache_file_exist and self.is_cache_expired()):
      response = self.make_http_request(self._city)
      response['city'] = self._city      
      response = self._store_response( response ) if response.get('status') == 200 else response
      return response
    
    return cache_file_exist and self.load_cached_response()

  def __exit__(self, type, value, traceback):
    return None

class Settings(object):

  def __init__(self):
    home = expanduser("~")
    self._look_up_list = [ os.path.join( home, '.motdrc'),
                           os.path.join( home,'motdrc' ),
                           os.path.join('etc', '.motdrc'),
                           os.path.join('etc',' motdrc')]
    
  def find_configuration_path(self,paths):
    for path in paths:
      if os.path.exists( path ):
        logger.debug("Found settings from " + path)
        return path

  def __enter__(self):
    path = self.find_configuration_path( self._look_up_list )
    
    if path:
      config = configparser.ConfigParser()
      self._filehandle = open(path,'r')      
      config.read_file(self._filehandle)
      return config
    else:
      raise MotdError("Configuration file .motdrc could not be find from any searched location." + str( self._look_up_list))

  def __exit__(self, type, value, traceback):
    self._filehandle.close()

class MotdError(Exception):
    def __init__(self, message, errors=None):
        super(MotdError, self).__init__(message)
        self.errors = errors

if __name__ == "__main__":      
  api = OpenWeatherAPI()
  api.request_weather('Tampere')