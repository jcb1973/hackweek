import urllib2
import re
import lxml.html

def find_albums(str_html):

  t = "<i>.*?<a href=\"/wiki/.*?\" title=\".*?\">(.*?)</a>.*?</i>"
  albums = re.findall(t, str_html, re.S)
  r = []
  for item in albums:
    t = lxml.html.fromstring(item)
    name = t.text_content()
    r.append (re.sub("\n", " ", name))
  return r  

def do_scrape(param):
  name = ''.join(param)
  foo = name.replace(" ", "_")
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

  return find_albums(table)


def application(environment, start_response):
  from webob import Request, Response

  request = Request(environment)
  params = request.params
  post = request.POST

  stuff= do_scrape(params.getall('name'))
  page = '\n'.join(stuff)

  response = Response(body = page,
                      content_type = "text/html",
                      charset = "utf8",
                      status = "200 OK")

  return response(environment, start_response)
