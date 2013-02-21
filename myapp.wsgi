import urllib2, json, sys
import re
import lxml.html
reload(sys)
sys.setdefaultencoding("utf-8")

WIKI_ROOT = 'http://en.wikipedia.org/wiki/'
USER_AGENT = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'

def find_albums(str_html, artist, simple):

  if simple:
    t = "<i>(.*?)</i>"
  else:
    t = "<i>.*?<a href=\"/wiki/.*?\" title=\".*?\">(.*?)</a>.*?</i>"
  
  print t 
  albums = re.findall(t, str_html, re.S)
  r = []
  for item in albums:
    if len(r) > 0:
      r.append(",")
    t = lxml.html.fromstring(item)
    name = '{\"title\":\"'
    name += re.sub('"', '\\"', t.text_content())
    name += '\"}'
    r.append (re.sub("\n", " ", name))
  fo = open('/tmp/'+artist, "wb")
  fo.write( u''.join(r) );
  fo.close()
  return r

def checkForAlbumsPage(html, name):
  str = name + " albums discography"
  p = re.compile(str, re.S)
  m = p.search(html)
  if m:
    return 1
  else:  
    return 0

def do_scrape(param):

  name = param.strip(' ').title()
  artist = name.replace(" ", "_").strip(' ');
  print artist
  simple_page = 0
  
  try:
    f = open('/tmp/'+artist, "r")
    str = f.read();
    f.close()
    return str
  except IOError as e:
    print 'No existing scraped content'
    request = urllib2.Request(WIKI_ROOT+artist+'_discography')
    opener = urllib2.build_opener()
    request.add_header('User-Agent', USER_AGENT)
    try:
      html = opener.open(request).read().decode('utf-8')
    except urllib2.HTTPError:
      request = urllib2.Request(WIKI_ROOT+artist)
      opener = urllib2.build_opener()
      request.add_header('User-Agent', USER_AGENT)
      simple_page = 1
      html = opener.open(request).read().decode('utf-8')
          
    if checkForAlbumsPage(html, name):
      request = urllib2.Request(WIKI_ROOT+artist+'_albums_discography')
      opener = urllib2.build_opener()
      request.add_header('User-Agent', USER_AGENT)
      html = opener.open(request).read()
    
    if simple_page:
      reg = "<span class=\"mw-headline\" id=\"Discography\">(Discography)</span>(.*?)</ul>"
    else:
      reg = "<span class=\"mw-headline\" id=\"Studio_.*?\">Studio.*?</span>.*?(Peak.*?positions|Certifications)(.*?)(Live albums|Compilation|Soundtrack albums|Soundtracks)"
      
    p = re.compile(reg, re.S)
    m = p.search(html)
    if m:
      table = m.group(2)
      return find_albums(table, artist, simple_page)
    else:
      print 'couldnt get the albums section using ' +reg

def application(environment, start_response):
  from webob import Request, Response

  request = Request(environment)
  params = request.params
  post = request.POST
  page = "["
  stuff= do_scrape(params.getall('name'))
  if type(stuff)==type(list()):
    page += ''.join(stuff)
  else:
    page += stuff 
  page += "]"

  response = Response(body = page,
                      content_type = "application/json",
                      charset = "utf8",
                      status = "200 OK")

  return response(environment, start_response)
