import os
import httplib

class Connection(httplib.HTTPSConnection):
  api_url = "bomberman-prod.herokuapp.com"
  api_key = os.environ['BOMBERMAN_API_KEY']
  api_version = "1"
  headers = {"Authorization": "Token token=" + api_key, "Content-Type": "application/json; charset=utf-8"}
  
  def __init__(self):
    httplib.HTTPSConnection.__init__(self, self.api_url)
