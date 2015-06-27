from bottle import route 
from boto.s3.key import Key
import redis, configparser, thread, requests, jsonpickle, boto, boto.s3.connection


config = configparser.ConfigParser()
config.read('config.ini')

thost = config.get('bottle','host')
tport = config.getint('bottle','port')
syskey = config.get('application','syskey')

s3key = config.get('s3','aws_access_key_id')
s3secret = config.get('s3','aws_secret_access_key')

#conn = boto.connect_s3(
#        aws_access_key_id = s3key,
#        aws_secret_access_key = s3secret,
#        calling_format = boto.s3.connection.OrdinaryCallingFormat(),
#        )
#bucket = conn.get_bucket('lms-io')
#key = Key(bucket) 
#key.key = "index.html"
#key.set_contents_from_filename('requirements.txt')

#sys.exit(0)
###################################
url = "http://%s:%s/sys/bad" % (thost,tport)
r = requests.get(url)
print(url)
print(r.text)
if r.text:
    raise ValueError("I shouldn't be allowed in")

###################################
url = "http://%s:%s/sys/%s" % (thost,tport, syskey)
r = requests.get(url)
print(url)
json = jsonpickle.decode(r.text)
print(json)
if json != 1.3:
    raise ValueError("I should be allowed in")

###################################
url = "http://%s:%s/sys/%s/organization/new/acme corporation" % (thost,tport, syskey)
r = requests.get(url)
print(url)
json = jsonpickle.decode(r.text)
print(json)
if json.get("name") != "acme corporation":
    raise ValueError("I should be allowed in")
###################################
url = "http://%s:%s/sys/%s/organization/all" % (thost,tport, syskey)
r = requests.get(url)
print(url)
json = jsonpickle.decode(r.text)
print(json)
if len(json) == 0:
    raise ValueError("I should be allowed in")

###################################
url = "http://%s:%s/sys/%s/organization/new/acme corporation 2/TESTID" % (thost,tport, syskey)
r = requests.get(url)
print(url)
json = jsonpickle.decode(r.text)
print(json)
if json.get("id") != "TESTID":
    raise ValueError("I should be allowed in")

###################################
url = "http://%s:%s/sys/%s/organization/new/test" % (thost,tport, syskey)
r = requests.get(url)
print(url)
json = jsonpickle.decode(r.text)
print(json)
if json.get("id") == None:
    raise ValueError("I should be allowed in")

org = json.get("id")
url = "http://%s:%s/sys/%s/%s/user/new/test" % (thost,tport, syskey, org)
r = requests.get(url)
print(url)
json = jsonpickle.decode(r.text)
print(json.get('organization'))
if json.get("name") != "test":
    raise ValueError("I should be allowed in")

if json.get("organization").get("id") != org:
    raise ValueError("I should be allowed in")

url = "http://%s:%s/sys/%s/%s/user/new/test/1234" % (thost,tport, syskey, org)
r = requests.get(url)
print(url)
json = jsonpickle.decode(r.text)
print(json)
if json.get("id") != "1234":
    raise ValueError("I should be allowed in")
if json.get("organization").get("id") != org:
    raise ValueError("I should be allowed in")

url = "http://%s:%s/sys/%s/%s/user/all" % (thost,tport, syskey, org)
r = requests.get(url)
print(url)
json = jsonpickle.decode(r.text)
print(json)
if len(json) != 2: 
    raise ValueError("I should be allowed in")
if json[0].get("organization").get("id") != org:
    raise ValueError("I should be allowed in")

###################################
url = "http://%s:%s/sys/%s/organization/new/test" % (thost,tport, syskey)
r = requests.get(url)
print(url)
json = jsonpickle.decode(r.text)
print(json)
if json.get("id") == None:
    raise ValueError("I should be allowed in")

org = json.get("id")
url = "http://%s:%s/sys/%s/%s/course/new/test" % (thost,tport, syskey, org)
r = requests.get(url)
print(url)
json = jsonpickle.decode(r.text)
print(json)
if json.get("name") != "test":
    raise ValueError("I should be allowed in")
if json.get("organization").get("id") != org:
    raise ValueError("I should be allowed in")

url = "http://%s:%s/sys/%s/%s/course/new/test/1234" % (thost,tport, syskey, org)
r = requests.get(url)
print(url)
json = jsonpickle.decode(r.text)
print(json)
if json.get("id") != "1234":
    raise ValueError("I should be allowed in")
if json.get("organization").get("id") != org:
    raise ValueError("I should be allowed in")

url = "http://%s:%s/sys/%s/%s/course/all" % (thost,tport, syskey, org)
r = requests.get(url)
print(url)
json = jsonpickle.decode(r.text)
print(json)
if len(json) != 2: 
    raise ValueError("I should be allowed in")
if json[0].get("organization").get("id") != org:
    raise ValueError("I should be allowed in")


###################################
url = "http://%s:%s/sys/%s/organization/new/test" % (thost,tport, syskey)
r = requests.get(url)
print(url)
json = jsonpickle.decode(r.text)
print(json)
if json.get("id") == None:
    raise ValueError("I should be allowed in")

org = json.get("id")
url = "http://%s:%s/sys/%s/%s/course/new/test" % (thost,tport, syskey, org)
r = requests.get(url)
print(url)
json = jsonpickle.decode(r.text)
print(json)
if json.get("name") != "test":
    raise ValueError("I should be allowed in")

course = json.get('id')
url = "http://%s:%s/sys/%s/%s/registration/new/test" % (thost,tport, syskey, org)
r = requests.get(url)
print(url)
json = jsonpickle.decode(r.text)
print(json)
if json.get("name") != "test":
    raise ValueError("I should be allowed in")

url = "http://%s:%s/sys/%s/%s/registration/new/test/123" % (thost,tport, syskey, org)
r = requests.get(url)
print(url)
json = jsonpickle.decode(r.text)
if json.get("id") != "123":
    raise ValueError("I should be allowed in")

###################################
url = "http://%s:%s/sys/%s/organization/new/test" % (thost,tport, syskey)
r = requests.get(url)
print(url)
json = jsonpickle.decode(r.text)
print(json)
if json.get("id") == None:
    raise ValueError("I should be allowed in")

org = json.get("id")
url = "http://%s:%s/sys/%s/%s/course/new/test" % (thost,tport, syskey, org)
r = requests.get(url)
print(url)
json = jsonpickle.decode(r.text)
print(json)
if json.get("name") != "test":
    raise ValueError("I should be allowed in")

course = json.get('id')
url = "http://%s:%s/sys/%s/%s/registration/new/test" % (thost,tport, syskey, org)
r = requests.get(url)
print(url)
json = jsonpickle.decode(r.text)
print(json)
if json.get("name") != "test":
    raise ValueError("I should be allowed in")

url = "http://%s:%s/sys/%s/%s/registration/new/test/123" % (thost,tport, syskey, org)
r = requests.get(url)
print(url)
json = jsonpickle.decode(r.text)
if json.get("id") != "123":
    raise ValueError("I should be allowed in")

registration = json.get("id")

url = "http://%s:%s/sys/%s/track/%s/%s" % (thost,tport, org, registration,course)
print(url)
r = requests.get(url)
json = jsonpickle.decode(r.text)
print(json)
if json is None:
    raise ValueError("I should be allowed in")

url = "http://%s:%s/sys/%s/track/%s/%s/?key=key1&value=val1" % (thost,tport, org, registration,course)
print(url)
r = requests.get(url)
json = jsonpickle.decode(r.text)
print(json)
if json is None:
    raise ValueError("I should be allowed in")

url = "http://%s:%s/sys/%s/track/%s/%s/?key=key2&value=val2" % (thost,tport, org, registration,course)
print(url)
r = requests.get(url)
json = jsonpickle.decode(r.text)
print(json)
if json is None:
    raise ValueError("I should be allowed in")

url = "http://%s:%s/sys/%s/track/%s/%s/?key=key3&value=val3" % (thost,tport, org, registration,course)
print(url)
r = requests.get(url)
json = jsonpickle.decode(r.text)
print(json)
if json is None:
    raise ValueError("I should be allowed in")
url = "http://%s:%s/sys/%s/track/%s/%s/?key=key3&value=val4" % (thost,tport, org, registration,course)
print(url)
r = requests.get(url)
json = jsonpickle.decode(r.text)
print(json)
if json is None:
    raise ValueError("I should be allowed in")
url = "http://%s:%s/sys/%s/track/%s/%s/?key=key3&value=valfin" % (thost,tport, org, registration,course)
print(url)
r = requests.get(url)
json = jsonpickle.decode(r.text)
print(json)
if json is None:
    raise ValueError("I should be allowed in")

url = "http://%s:%s/sys/%s/track/%s/%s/?key=key3" % (thost,tport, org, registration,course)
print(url)
r = requests.get(url)
json = jsonpickle.decode(r.text)
print(json)
if json[0] != "valfin" :
    raise ValueError("I should be allowed in")

url = "http://%s:%s/sys/%s/track/%s/%s" % (thost,tport, org, registration,course)
print(url)
r = requests.get(url)
json = jsonpickle.decode(r.text)
print(json)
if json.get('key3') != "valfin" :
    raise ValueError("I should be allowed in")


###################################
url = "http://%s:%s/sys/%s/organization/new/test" % (thost,tport, syskey)
r = requests.get(url)
print(url)
json = jsonpickle.decode(r.text)
print(json)
if json.get("id") == None:
    raise ValueError("I should be allowed in")

org = json.get("id")
url = "http://%s:%s/sys/%s/%s/user/new/test" % (thost,tport, syskey, org)
r = requests.get(url)
print(url)
json = jsonpickle.decode(r.text)
print(json)
if json.get("name") != "test":
    raise ValueError("I should be allowed in")

if json.get("organization").get("id") != org:
    raise ValueError("I should be allowed in")
user = json.get("id")
url = "http://%s:%s/sys/%s/%s/user/new/test2" % (thost,tport, user, org)
r = requests.get(url)
print(url)
json = jsonpickle.decode(r.text)
print(json)
if json.get("name") != "test2":
    raise ValueError("I should be allowed in")

###################################
url = "http://%s:%s/sys/%s/organization/new/test" % (thost,tport, syskey)
r = requests.get(url)
print(url)
json = jsonpickle.decode(r.text)
print(json)
if json.get("id") == None:
    raise ValueError("I should be allowed in")

org = json.get("id")

url = "http://%s:%s/sys/%s/%s/course/new/test" % (thost,tport, syskey, org)
r = requests.get(url)
print(url)
json = jsonpickle.decode(r.text)
print(json)
course = json.get('id')
url = "http://%s:%s/sys/%s/%s/upload/%s" % (thost,tport, syskey, org, course)
r = requests.post(url, files={'upload': open('test/zips/macfolder.zip', 'rb')})

url = "http://%s:%s/sys/%s/%s/course/new/test" % (thost,tport, syskey, org)
r = requests.get(url)
print(url)
json = jsonpickle.decode(r.text)
print(json)
course = json.get('id')
url = "http://%s:%s/sys/%s/%s/upload/%s" % (thost,tport, syskey, org, course)
r = requests.post(url, files={'upload': open('test/zips/nofolder.zip', 'rb')})

url = "http://%s:%s/sys/%s/%s/course/new/test" % (thost,tport, syskey, org)
r = requests.get(url)
print(url)
json = jsonpickle.decode(r.text)
print(json)
course = json.get('id')
url = "http://%s:%s/sys/%s/%s/upload/%s" % (thost,tport, syskey, org, course)
r = requests.post(url, files={'upload': open('test/zips/zip_with_no_html.zip', 'rb')})

url = "http://%s:%s/sys/%s/%s/course/new/test" % (thost,tport, syskey, org)
r = requests.get(url)
print(url)
json = jsonpickle.decode(r.text)
print(json)
course = json.get('id')
url = "http://%s:%s/sys/%s/%s/upload/%s" % (thost,tport, syskey, org, course)
r = requests.post(url, files={'upload': open('test/zips/zip_with_stuff_bad.zip', 'rb')})

url = "http://%s:%s/sys/%s/%s/course/new/test" % (thost,tport, syskey, org)
r = requests.get(url)
print(url)
json = jsonpickle.decode(r.text)
print(json)
course = json.get('id')
url = "http://%s:%s/sys/%s/%s/upload/%s" % (thost,tport, syskey, org, course)
r = requests.post(url, files={'upload': open('test/zips/zip_with_stuff_good.zip', 'rb')})

url = "http://%s:%s/sys/%s/%s/course/new/test" % (thost,tport, syskey, org)
r = requests.get(url)
print(url)
json = jsonpickle.decode(r.text)
print(json)
course = json.get('id')
url = "http://%s:%s/sys/%s/%s/upload/%s" % (thost,tport, syskey, org, course)
r = requests.post(url, files={'upload': open('test/zips/macfolder.zip', 'rb')})

url = "http://%s:%s/sys/%s/%s/registration/new/test/123" % (thost,tport, syskey, org)
r = requests.get(url)
print(url)
json = jsonpickle.decode(r.text)
if json.get("id") != "123":
    raise ValueError("I should be allowed in")

registration = json.get("id")

url = "http://%s:%s/sys/%s/%s/link/%s/%s" % (thost,tport, syskey,org, registration,course)
print(url)
r = requests.get(url)

