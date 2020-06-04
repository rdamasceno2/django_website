from website import app
from flask import request
from flask import render_template
from flask import Flask, make_response
from flask import Markup
from flask import url_for
from flask import abort
from ConfigParser import SafeConfigParser
from ConfigParser import NoSectionError
from ConfigParser import NoOptionError
import os
import oauth2 as oauth
import simplejson
from github3 import GitHub
import facebook as facebook
import urllib
import urllib2
import requests
import re
import sys
import logging

logging.basicConfig(stream = sys.stderr)
#app = Flask(__name__)
#app.debug = True
app.jinja_env.add_extension('jinja2.ext.do')
config_file = os.path.dirname(os.path.abspath(__file__)) + '/config.cfg'

parser = SafeConfigParser()
if os.environ.get('CONFIG_PARSER_PATH'):
  parser.read(os.environ['CONFIG_PARSER_PATH'])
else:
  variables = [v for v in os.environ if 'CONFIG_PARSER' in v]
  if len(variables) == 0:
    parser.read(config_file)
  else:
    for v in variables:
      configs = map(lambda x: x.lower(),str.split(v,"___"))[1:]
      if not parser.has_section(configs[0]):
        parser.add_section(configs[0])
      parser.set(configs[0],configs[1],os.environ[v])
  
def sort_by_date(values):
  for v in values:
    if v["startDate"] < 10:
      offset = "0"
    else:
      offset = ""
    v['sortbydate'] = str(v["startDate"]["year"]) + offset + str(v["startDate"]["month"])
  sorted(values,key=lambda x: x["sortbydate"])
  map(lambda x: x.pop("sortbydate"),values)
  return values

def get_github_data():
  try:
    oauth_user=parser.get('github','user')
    oauth_user_token=parser.get('github','oauth')
  except NoSectionError,NoOptionError:
    return None
  gh = GitHub(oauth_user,token=oauth_user_token)
  repos = list(gh.iter_repos())
  repo_data = {}
  for r in repos:
    repo_name = getattr(r,'name')
    current_repo = r.__dict__
    new_repo = {}
    new_repo['full_name'] = current_repo['full_name']
    new_repo['url'] = current_repo['html_url']
    repo_data[repo_name] = new_repo

  return repo_data

def old_get_github_data():

  oauth_user_token=parser.get('github','oauth_key')
  oauth_user_secret=parser.get('github','oauth_secret')
  
  url = "https://api.github.com/user/repos"
  consumer = oauth.Consumer(
     key=oauth_user_token, 
     secret=oauth_user_secret)
  client = oauth.Client(consumer)
  client.disable_ssl_certificate_validation=True
  resp, content = client.request(url)
  return simplejson.loads(content)


def get_user_data():
  try:
    api_key=parser.get('linkedin','api_key')
    secret_key=parser.get('linkedin','secret_key')
    oauth_user_token=parser.get('linkedin','oauth_user_token')
    oauth_user_secret=parser.get('linkedin','oauth_user_secret')
    url = "http://api.linkedin.com/v1/people/~"
    url = "http://api.linkedin.com/v1/people/~:(id,first-name,last-name,industry)?format=json"
    url='http://api.linkedin.com/v1/people/~:(%(all_fields)s)?format=json' % {"all_fields":parser.get('linkedin','field_list')}
  except NoSectionError,NoOptionError:
    return None

  consumer = oauth.Consumer(
     key=api_key,
     secret=secret_key)
     
  token = oauth.Token(
     key=oauth_user_token, 
     secret=oauth_user_secret)


  client = oauth.Client(consumer, token)

  resp, content = client.request(url)
  content = simplejson.loads(content)
  content["positions"]["values"] = sort_by_date(content["positions"]["values"])
  return content

def process_facebook_likes(fb_data):
  output_data = {}
  try:
    blacklisted_categories = parser.get('facebook','likes_category_blacklist').rstrip().split(',')
    blacklisted_ids = parser.get('facebook','likes_individual_blacklist').rstrip().split(',')
  except NoSectionError,NoOptionError:
    return None
  for item in fb_data['data']:
    if item['category'] in blacklisted_categories:
      continue
    if item['category'] not in output_data:
      output_data[item['category']] = {}
    if item['id'] not in blacklisted_ids:
      output_data[item['category']][item['id']] = item['name']
  for category in output_data.keys():
    if len(output_data[category]) == 0:
      del output_data[category]
  return output_data

def get_facebook_data():
  try:
    oauth_args = {"client_id":parser.get('facebook','app_id'),"client_secret":parser.get('facebook','secret'),"grant_type":"client_credentials"}
  except NoSectionError,NoOptionError:
    return None

  auth_url = "https://graph.facebook.com/oauth/access_token?%(args)s" % {"args":urllib.urlencode(oauth_args)}
  r = requests.get(auth_url)
  oauth_token = r.text.split("=")[1]
  graph = facebook.GraphAPI(oauth_token)
  profile = graph.get_object(parser.get("facebook","user"))
  facebook_data = {}
  facebook_data["likes"] = process_facebook_likes(graph.get_object(parser.get("facebook","user") + "/likes"))

  return facebook_data

@app.route("/css")
def css():
  abort(404)

@app.route("/bootstrap")
def bootstrap():
  abort(404)

@app.route("/facebook",methods=['GET','POST'])
def fb():
  redirect_url = "http://subbakrishna.com/facebook"
  redirect_url = "https://www.facebook.com/connect/login_success.html"
  redirect_url = "http://subbakrishna.com/facebook_redirect"
  user_code_url = "https://graph.facebook.com/oauth/authorize?client_id=%(app_id)s&redirect_uri=%(redirect_url)s" % {"app_id":parser.get('facebook','app_id'),"redirect_url":redirect_url}
  req = urllib2.Request(user_code_url)
  response = urllib2.urlopen(req)

  return get_facebook_data()

@app.route("/facebook_redirect",methods=['GET','POST'])
def redir():
  print request.args.items()
  print request.form.itmes()
  return "HELLO"

@app.route("/", methods=['GET', 'POST'])
def combined_all():

  mobile = False
  browser = request.user_agent.browser
  version = request.user_agent.version and int(request.user_agent.version.split('.')[0])
  platform = request.user_agent.platform
  uas = request.user_agent.string

  if platform:
    if platform in ['iphone','android'] \
    or (platform == 'windows' and re.search('Windows Phone OS', uas)) \
    or (re.search('BlackBerry', uas)):
       mobile = True
     

  return render_template('combined_pages.html', data=get_user_data(),github_data=get_github_data(),user_data=dict(parser.items('user')),facebook_data=get_facebook_data(),mobile=mobile,gvoice_widget = parser.get('user','gvoice_widget_id'))

if __name__ == '__main__':
  app.run(debug=True,host='0.0.0.0')
