# coding=utf-8
import json
import httplib, urllib
from bomberman.error import BadRequest
from bomberman.error import Unauthorized
from bomberman.error import InternalServerError
from bomberman.error import LanguageNotSupported
from bomberman.connection import Connection

class Client(object):
  def __init__(self):
    self.conn = Connection()

  def is_profane(self, corpus, language="en"):
    params = urllib.urlencode({'corpus': corpus})
    self.conn.request("GET", "%s/profanity/check?%s" % (self.__lang_version(language), params), headers=self.conn.headers)
    resp = self.conn.getresponse()
    if resp.status == 200:
      profane = resp.read()
      self.conn.close()
      return (profane == "1")
    else:
      self.conn.close()
      self.__raise_exception(resp.status)

  def censor(self, corpus, replacement_text="***", language="en"):
    params = urllib.urlencode({'corpus': corpus, 'replacement_text': replacement_text})
    self.conn.request("GET", "%s/profanity/censor?%s" % (self.__lang_version(language), params), headers=self.conn.headers)
    resp = self.conn.getresponse()
    if resp.status == 200:
      data = json.loads(resp.read())
      self.conn.close()
      return data['censored_text']
    else:
      self.conn.close()
      self.__raise_exception(resp.status)

  def highlight(self, corpus, start_tag="<strong>", end_tag="</strong>", language="en"):
    params = urllib.urlencode({'corpus': corpus, 'start_tag': start_tag, 'end_tag': end_tag})
    self.conn.request("GET", "%s/profanity/highlight?%s" % (self.__lang_version(language), params), headers=self.conn.headers)
    resp = self.conn.getresponse()
    if resp.status == 200:
      data = json.loads(resp.read())
      self.conn.close()
      return data['highlighted_text']
    else:
      self.conn.close()
      self.__raise_exception(resp.status)

  def __lang_version(self, language="en"):
    if language == "en":
      return "/v" + self.conn.api_version
    elif language == "ja":
      return "/ja/v" + self.conn.api_version
    else:
      raise LanguageNotSupported
    
  def __raise_exception(self, code):
    if code == 400:
      raise BadRequest
    elif code == 401:
      raise Unauthorized
    elif code == 500:
      raise InternalServerError
    else:
      raise Exception("Bomberman returned error code %s" % code)
