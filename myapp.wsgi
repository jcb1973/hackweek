import urllib2, json, sys
import re
import lxml.html
reload(sys)
sys.setdefaultencoding("utf-8")

WIKI_ROOT = 'http://en.wikipedia.org/wiki/'
USER_AGENT = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'

def find_albums(str_html, foo):

  t = "<i>.*?<a href=\"/wiki/.*?\" title=\".*?\">(.*?)</a>.*?</i>"
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
  fo = open('/tmp/'+foo, "wb")
  fo.write( ''.join(r) );
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
  name = ''.join(param)
  artist = name.replace(" ", "_")

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
    html = opener.open(request).read()
    
    if checkForAlbumsPage(html, name):
      request = urllib2.Request(WIKI_ROOT+artist+'_albums_discography')
      opener = urllib2.build_opener()
      request.add_header('User-Agent', USER_AGENT)
      html = opener.open(request).read()
      
    p = re.compile("<span class=\"mw-headline\" id=\"Studio_albums\">Studio albums</span>.*?(Peak.*?positions|Certifications)(.*?)</table>.*?(Soundtrack albums|Live albums)", re.S)

    m = p.search(html)
    if m:
      table = m.group(2)
      return find_albums(table, artist)
    else:
      print 'No match found in: ' +html
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
