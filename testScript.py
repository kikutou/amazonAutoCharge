# coding=utf-8
import urllib
import urllib2

response ={}
url = "http://13.112.14.13:4000/amazon-login"
headers ={
  "pragma":"no-cache",
}
try :
  params = urllib.urlencode(
      {
          'email':"juteng2005@gmail.com",
          'password':"Juteng378084190"
      }
  )
  req = urllib2.Request(url, params ,headers )
  res = urllib2.urlopen(req)
  response["body"] = res.read()
  response["headers"] =  res.info().dict
except urllib2.HTTPError, e:
  print e
  exit()

print response["body"]

url = "http://13.112.14.13:4000/buy-checklist"
headers ={
  "pragma":"no-cache",
}
try :
  params = urllib.urlencode(
      {
          'email':"juteng2005@gmail.com",
          'trade_id':"1",
          'code1':"DDDDDDDDDDDDDDDDDD",
          'trade_code1':"11111",
          'code2':"AAAAAAAAAAAAAAAAAA",
          "trade_code2":"skfhskdhfskd"
      }
  )
  req = urllib2.Request(url, params ,headers )
  res = urllib2.urlopen(req)
  response["body"] = res.read()
  response["headers"] =  res.info().dict
except urllib2.HTTPError, e:
  print e
  exit()

print response["body"]
