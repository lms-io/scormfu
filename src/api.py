from bottle import route,request 
from organization import Organization
from registration import Registration 
from user import User 
from course import Course
import redis, configparser, thread, requests, sys, jsonpickle, random, os, zipfile, shutil 

config = configparser.ConfigParser()
config.read('config.ini')
rhost = config.get('redis','host')
rport = config.getint('redis','port')
rdb = config.getint('redis','db')
rdis = redis.StrictRedis(host=rhost, port=rport, db=rdb)

syskey = config.get('application','syskey')
debug = config.getboolean('application','debug')


tempdir = config.get('upload','tempdir')
finaldir = config.get('upload','finaldir')
webdir = config.get('upload','webdir')
contenthost = config.get('content','host')

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

def callback(r, v):
    print(r.query.get('callback'))
    if r.query.get('callback') is not None:
        return '%s(%s)' % (r.query.get('callback'),v)
    else:
        return v

@route('/sys/<key>')
def sys_is_working(key=""):
    if not is_sys(key): return ""
    rdis.set('version','1.3')
    return callback(request,rdis.get('version')) 

@route('/sys/<key>/organization/new/<name>')
@route('/sys/<key>/organization/new/<name>/<id>')
def sys_new_organization(key="",id="",name=""):
    if not is_sys(key): return callback(request,"") 
    if id =="":
        id=new_id()
    organization = Organization(id,name)
    rdis.set(organization.key,to_json(organization))
    rdis.sadd('organization:list',organization.key)
    return callback(request,rdis.get(organization.key)) 

@route('/sys/<key>/organization/all')
def sys_new_organization(key="",id="",name=""):
    if not is_sys(key): return callback(request,"") 

    orgs = rdis.smembers('organization:list')
    orgResp = []
    for org in orgs:
        orgResp.append(from_json(rdis.get(org)))
    return callback(request,to_json(orgResp))

@route('/sys/<key>/<org>/user/new/<name>')
@route('/sys/<key>/<org>/user/new/<name>/<id>')
def api_new_user(key="",org="",name="",id=""):
    if not is_sys(key,org): return callback(request,"") 
    if id =="":
        id=new_id()

    organization = from_json(rdis.get(Organization().to_key(org)))
    user = User(id,name,organization)
    rdis.set(user.key,to_json(user))
    rdis.sadd('%s:user:list' % organization.key,user.key)
    return callback(request,rdis.get(user.key)) 

@route('/sys/<key>/<org>/user/all')
def api_all_users(key="",org=""):
    if not is_sys(key): return callback(request,"") 
    organization = from_json(rdis.get(Organization().to_key(org)))
    users = rdis.smembers('%s:user:list' % organization.key)
    userResp = []
    for user in users:
        userResp.append(from_json(rdis.get(user)))
    return callback(request,to_json(userResp))

@route('/sys/<key>/<org>/course/new/<name>')
@route('/sys/<key>/<org>/course/new/<name>/<id>')
def api_new_course(key="",org="",name="",id=""):
    if not is_sys(key): return callback(request,"") 
    if id =="":
        id=new_id()

    organization = from_json(rdis.get(Organization().to_key(org)))
    course = Course(id,name,organization)
    if not valid_for(organization,(course,)): return ""

    rdis.set(course.key,to_json(course))
    rdis.sadd('%s:course:list' % organization.key,course.key)
    return callback(request,rdis.get(course.key)) 

@route('/sys/<key>/<org>/course/all')
def api_all_courses(key="",org=""):
    if not is_sys(key): return callback(request,"") 
    organization = from_json(rdis.get(Organization().to_key(org)))
    courses = rdis.smembers('%s:course:list' % organization.key)
    courseResp = []
    for course in courses:
        courseResp.append(from_json(rdis.get(course)))
    return callback(request,to_json(courseResp))


@route('/sys/<key>/<org>/registration/new')
@route('/sys/<key>/<org>/registration/new/<name>')
@route('/sys/<key>/<org>/registration/new/<name>/<id>')
def api_new_registration(key="",org="", name="",id=""):
    if not is_sys(key): return callback(request,"") 
    if id =="":
        id=new_id()
    organization = from_json(rdis.get(Organization().to_key(org)))
    registration = Registration(id,name,organization)
    if not valid_for(organization,(registration,)): return ""

    rdis.set(registration.key,to_json(registration))
    rdis.sadd('%s:registration:list' % organization.key,registration.key)
    return callback(request,rdis.get(registration.key)) 

@route('/sys/<key>/<org>/registration/all')
def api_all_courses(key="",org=""):
    if not is_sys(key): return callback(request,"") 
    organization = from_json(rdis.get(Organization().to_key(org)))
    registrations = rdis.smembers('%s:registration:list' % organization.key)
    registrationResp = []
    for registration in registrations:
        registrationResp.append(from_json(rdis.get(registration)))
    return callback(request,to_json(registrationResp))

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
        return callback(request,'{"action":"update"}') 
    if key and not value:
        return callback(request,to_json(rdis.hmget('%s:track:%s:%s' % (organization.key,registration.id,course.id), key)))
    else:
        return callback(request,to_json(rdis.hgetall('%s:track:%s:%s' % (organization.key,registration.id,course.id))))

@route('/sys/<key>/<org>/link/<reg>/<course>')
def api_link_course(key="",org="", reg="", course=""):
    if not is_sys(key): return callback(request,"") 

    organization = from_json(rdis.get(Organization().to_key(org)))
    course = from_json(rdis.get(Course().to_key(org,course)))
    registration = from_json(rdis.get(Registration().to_key(org,reg)))
    if not valid_for(organization,(course,registration)): return ""

    course_path = finaldir + course.id
    course_destination_path = webdir + course.id
    content_path = course_destination_path + "/" + registration.id 

    if not os.path.exists(course_destination_path):
        os.makedirs(course_destination_path)

    os.symlink(course_path, content_path) 
    courseurl = contenthost % (course.id,registration.id, organization.id) 
    return callback(request,'{"url":"%s"}' % courseurl)

@route('/sys/<key>/<org>/upload/<course>', method='POST')
def upload_course(key="",org="",course=""):
    if not is_sys(key): return callback(request,"") 

    id = 'UPLOAD_'+new_id()
    upload     = request.files.get('upload')
    name, ext = os.path.splitext(upload.filename)

    save_path = tempdir + id + "/" 
    save_zip = save_path + upload.filename

    move_path = tempdir + new_id() + "/" 

    content_folder = finaldir + "/" + name
    final_path = finaldir + course + "/" 

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    upload.save(save_path) 

    with zipfile.ZipFile(save_zip, "r") as z:
        z.extractall(save_path)
    os.remove(save_zip)

    # ugh 
    if os.path.exists(save_path + "__MACOSX"):
        shutil.rmtree(save_path + "__MACOSX")
    
    # one subfolder exists, pull it back a directory
    if len(os.listdir(save_path)) == 1 and os.path.exists(save_path + os.listdir(save_path)[0]):
        extract_path = save_path + os.listdir(save_path)[0]
        shutil.move(extract_path, move_path)
        shutil.rmtree(save_path)
        shutil.move(move_path, save_path)

    # more cleanup, what are they calling the file names today?
    # sometimes it comes through as My Course Name.html
    # other times it comes through as index_lms.html
    if os.path.isfile(save_path + "index_lms.html"):
        shutil.move(save_path + "index_lms.html", save_path + "index.html")
    elif os.path.isfile(save_path + name + ".html"):
        shutil.move(save_path + name + ".html", save_path + "index.html")

    # finally check to see if we have a valid index file
    # if we do, move it to the right place

    if os.path.isfile(save_path + "index.html"):
        shutil.move(save_path,final_path) 
    else:
        shutil.rmtree(save_path)
        # I don't know what to do, abort!
        return callback(request,"") 

    return callback(request,'OK')
    

