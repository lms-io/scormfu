from bottle import route,request 
from organization import Organization
from registration import Registration 
from user import User 
from course import Course
import redis, configparser, thread, requests, sys, jsonpickle, random

config = configparser.ConfigParser()
config.read('config.ini')
rhost = config.get('redis','host')
rport = config.getint('redis','port')
rdb = config.getint('redis','db')
rdis = redis.StrictRedis(host=rhost, port=rport, db=rdb)

syskey = config.get('application','syskey')
debug = config.getboolean('application','debug')

def valid_for(org,tup):
    for t in tup:
        if t is None or t.organization is None or t.organization.id != org.id:
            return False
    return True

def from_json(arg):
    return jsonpickle.decode(arg)

def to_json(arg):
    if debug:
        return jsonpickle.encode(arg,unpicklable=True) 
    else:
        return jsonpickle.encode(arg,unpicklable=False) 

def is_sys(key,org=None):
    if key == syskey:
        return True 

    userJson = rdis.get(User().to_key(org,key))
    if(userJson == None): return False
    user = from_json(userJson)
    organization = from_json(rdis.get(Organization().to_key(org)))
    return valid_for(organization, (user,))

def new_id():
    return ''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') for i in range(16))

@route('/sys/<key>')
def sys_is_working(key=""):
    if not is_sys(key): return ""
    rdis.set('version','1.3')
    return rdis.get('version') 

@route('/sys/<key>/organization/new/<name>')
@route('/sys/<key>/organization/new/<name>/<id>')
def sys_new_organization(key="",id="",name=""):
    if not is_sys(key): return ""
    if id =="":
        id=new_id()
    organization = Organization(id,name)
    rdis.set(organization.key,to_json(organization))
    return rdis.get(organization.key) 

@route('/sys/<key>/<org>/user/new/<name>')
@route('/sys/<key>/<org>/user/new/<name>/<id>')
def api_new_user(key="",org="",name="",id=""):
    if not is_sys(key,org): return ""
    if id =="":
        id=new_id()

    organization = from_json(rdis.get(Organization().to_key(org)))
    user = User(id,name,organization)
    rdis.set(user.key,to_json(user))
    rdis.sadd('%s:user:list' % organization.key,user.key)
    return rdis.get(user.key) 

@route('/sys/<key>/<org>/user/all')
def api_all_users(key="",org=""):
    if not is_sys(key): return ""
    organization = from_json(rdis.get(Organization().to_key(org)))
    users = rdis.smembers('%s:user:list' % organization.key)
    userResp = []
    for user in users:
        userResp.append(from_json(rdis.get(user)))
    return to_json(userResp)

@route('/sys/<key>/<org>/course/new/<name>')
@route('/sys/<key>/<org>/course/new/<name>/<id>')
def api_new_course(key="",org="",name="",id=""):
    if not is_sys(key): return ""
    if id =="":
        id=new_id()

    organization = from_json(rdis.get(Organization().to_key(org)))
    course = Course(id,name,organization)
    if not valid_for(organization,(course,)): return ""

    rdis.set(course.key,to_json(course))
    rdis.sadd('%s:course:list' % organization.key,course.key)
    return rdis.get(course.key) 

@route('/sys/<key>/<org>/course/all')
def api_all_courses(key="",org=""):
    if not is_sys(key): return ""
    organization = from_json(rdis.get(Organization().to_key(org)))
    courses = rdis.smembers('%s:course:list' % organization.key)
    courseResp = []
    for course in courses:
        courseResp.append(from_json(rdis.get(course)))
    return to_json(courseResp)


@route('/sys/<key>/<org>/registration/new')
@route('/sys/<key>/<org>/registration/new/<name>')
@route('/sys/<key>/<org>/registration/new/<name>/<id>')
def api_new_registration(key="",org="", name="",id=""):
    if not is_sys(key): return ""
    if id =="":
        id=new_id()
    organization = from_json(rdis.get(Organization().to_key(org)))
    registration = Registration(id,name,organization)
    if not valid_for(organization,(registration,)): return ""

    rdis.set(registration.key,to_json(registration))
    rdis.sadd('%s:registration:list' % organization.key,registration.key)
    return rdis.get(registration.key) 


@route('/sys/<org>/track/<reg>/<course>')
def api_track_registration(org="", reg="", course=""):
    organization = from_json(rdis.get(Organization().to_key(org)))
    course = from_json(rdis.get(Course().to_key(org,course)))
    registration = from_json(rdis.get(Registration().to_key(org,reg)))
    if not valid_for(organization,(course,registration)): return ""

    key = request.query.get('key')
    value = request.query.get('value')
    if key and value:
        rdis.hset('%s:track:%s:%s' % (organization.key,registration.id,course.id), key, value)
        return '{"action":"update"}' 
    if key and not value:
        return to_json(rdis.hmget('%s:track:%s:%s' % (organization.key,registration.id,course.id), key))
    else:
        return to_json(rdis.hgetall('%s:track:%s:%s' % (organization.key,registration.id,course.id)))
