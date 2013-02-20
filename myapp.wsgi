import urllib2, json, sys
import re
import lxml.html
reload(sys)
sys.setdefaultencoding("utf-8")

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

def do_scrape(param):
  name = ''.join(param)
  foo = name.replace(" ", "_")

  try:
    f = open('/tmp/'+foo, "r") 
    str = f.read();
    f.close() 
    return str
  except IOError as e:
    print 'Oh dear.'
    request = urllib2.Request('http://en.wikipedia.org/wiki/'+foo+'_discography')
    opener = urllib2.build_opener()                                   
    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)')
    html = opener.open(request).read()   
    p = re.compile("<span class=\"mw-headline\" id=\"Studio_albums\">Studio albums</span>.*?(Peak.chart.positions|Certifications)(.*?)<\/table>", re.S)
   
    m = p.search(html)

    if m:
      table = m.group(2)
    else:
      print 'No match - off to to Bing we go'

    return find_albums(table, foo)


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
