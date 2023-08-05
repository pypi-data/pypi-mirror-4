#!/usr/bin/python
import optparse
import os
import pprint
import resource 
import json
import sys
import webbrowser

import requests
from requests.auth import HTTPBasicAuth
import yaml
import time

VERSION = '0.5.2'

backliftURL = {}
default_backliftURL = 'https://www.backlift.com/'
backlift_appid_file = 'appid'
backlift_cfg_folder = '.backlift'
backlift_email = 'support@backlift.com'
backlift_dir = '.backlift_env'


# maxfiles is set to a few less than the system limit. 
maxfiles = resource.getrlimit(resource.RLIMIT_NOFILE)[0] - 6

## ERROR MESSAGES -------------------------------------------------------------

ERR_ID =       "Ooops! Something's wrong. I couldn't obtain an app id. To\n"+\
               "use the push or watch commands, you need an existing\n"+\
               "backlift app created with either the create or init commands.\n"+\
               "If you've just upgraded backlift, run 'backlift init [name]'"

ERR_BADID =    "Ooops! Something's wrong. I couldn't obtain an app id from\n"+\
               "the server. Please send an angry email to %s." % backlift_email

ERR_MAXFILE =  "Too many files. Total: %d,  max: %d"

ERR_SERVER =   "Ooops! Our server is not responding. Hopefully this is\n"+\
               "temporary. If this problem persists, please send an angry\n"+\
               "email to %s." % backlift_email

ERR_WRITE =    "Ooops! We couldn't create a file. Please check to ensure\n"+\
               "you have permission to write to %s."

ERR_INIT =     "This app has already been initialized. Use -f to force."

ERR_500 =      "Ooops! Our server is having trouble. We're looking into\n"+\
               "it! While we're at it, please check to make sure you're\n"+\
               "running the latest version of the backlift command line\n"+\
               "interface at www.backlift.com. You're currently running\n"+\
               "backlift cli %s." % VERSION

ERR_400 =      "Ooops! There seems to be a problem. \nError message: %s"

ERR_404 =      "Ooops! We couldn't find the app on the backlift server."

ERR_403 =      "Ooops! This action is forbidden. Either you haven't\n" +\
               "set up your api key, or you used an invalid key. Please\n"+\
               "use the backlift setup command. See backlift --help."

ERR_RESPONSE = "Oops! Something is wrong with the server. Please let us\n"+\
               "know by emailing %s." % backlift_email + "\nError code: %s"

ERR_NOURL =    "Oops! This app doesn't have a valid URL. Have you pushed\n"+\
               "your app to backlift yet? (See backlift --help) If you\n"+\
               "have pushed your app and you're still getting this error,\n"+\
               "please let us know by sending an email to %s." % backlift_email

ERR_NOUSER =   "Oops! User couldn't be created."

## UTILITIES ------------------------------------------------------------------

def fail(msg):
    print >> sys.stderr, msg
    sys.exit(1)


def check_response(r):
    # import pdb; pdb.set_trace()
    if not (r.status_code / 100 == 2):
        mtype = r.headers['Content-Type'].split(';')[0]
        if r.status_code == 500:
            fail(ERR_500)
        elif r.status_code == 400:
            try:
                err = json.loads(r.content)
                errstrs = []
                for key, val in err['form_errors'].items():
                    if key:
                        errstrs.append(key + ': ' + ', '.join(val))
                    else:
                        errstrs.append(', '.join(val))
                fail(ERR_400 % '\n'.join(errstrs))
            except (ValueError, KeyError):
                fail(ERR_400 % r.content)
        elif r.status_code == 404:
            fail(ERR_404)
        elif r.status_code == 403:
            fail(ERR_403)
        else:
            fail(ERR_RESPONSE % r.status_code)


def listFiles(path, skip_hidden):
    files = []        

    for (dirpath, dirnames, filenames) in os.walk(path):
        # import pdb; pdb.set_trace()
        path_hidden = reduce(lambda x, y: x or (y[0] == '.'), 
            dirpath.split('/')[1:], False)

        if not path_hidden or not skip_hidden:

            for name in filenames:

                filepath = os.path.normpath(os.path.join(dirpath, name))

                if dirpath == os.path.join(path, backlift_cfg_folder):
                    continue

                elif skip_hidden and name[0] == '.':
                    continue

                files.append(filepath)

    filecount = len(files)
    if filecount > maxfiles:
        fail(ERR_MAXFILE % (filecount, maxfiles))

    return files


def collectFiles(path, skip_hidden):
    # import pdb; pdb.set_trace()
    rootpath = os.path.normpath(os.path.abspath(path))
    print "Scanning %s" % rootpath

    filelist = listFiles(rootpath, skip_hidden)

    files = {}

    for filepath in filelist:
        try:
            filekey = filepath.replace(rootpath, '', 1).strip('/')
            files[filekey] = (filekey, open(filepath, 'rb'))
            print "Adding %s" % filekey
        except OSError:
            continue

    return files


def scanFiles(path, skip_hidden):
    rootpath = os.path.normpath(os.path.abspath(path))
    filelist = listFiles(rootpath, skip_hidden)
    times = {}
    for f in filelist:
        try:
            times[f] = os.stat(f).st_mtime
        except OSError:
            continue
    return times


def get_id(path):
    id_str = ''
    id_file = os.path.join(path, backlift_cfg_folder, backlift_appid_file)
    try:
        handle = open(id_file, 'r')
        id_str = handle.read()
        handle.close()
    except Exception as e:
        pass

    if not id_str: fail(ERR_ID)

    return id_str


def open_create(path, perm):
    try:
        newfile = open(path, perm)
    except IOError:
        newfile = None

    if not newfile:
        try:
            filedir = os.path.split(path)[0]
            os.makedirs(filedir, 0755)
            newfile = open(path, perm)
        except OSError:
            fail(ERR_WRITE % filedir)

    return newfile


def get_api_key_file():
    home = os.getenv('BACKLIFT_HOME') or os.path.expanduser('~')
    path = os.path.join(home, backlift_dir, 'api_key')
    return path


def save_api_key(api_key):
    fh = open_create(get_api_key_file(), 'w')
    fh.write(api_key)
    fh.close()


STATIC_API_KEY = None

def read_api_key():
    global STATIC_API_KEY

    if STATIC_API_KEY:
        return STATIC_API_KEY

    try:
        fh = open(get_api_key_file(), 'r')
        api_key = fh.read()
        fh.close()
    except IOError:
        api_key = ''

    STATIC_API_KEY = api_key
    return api_key


def check_backlift_cfg(path, app_id, force=False):
    filepath = os.path.join(path, backlift_cfg_folder)

    if os.path.exists(filepath) and not force:
        fail(ERR_INIT)

    return filepath


def setup_app(path, app_id, force=False):
    filepath = check_backlift_cfg(path, app_id, force)

    keyfile = open_create(os.path.join(filepath, backlift_appid_file), 'w')
    keyfile.write(app_id)
    keyfile.close()


## REQUESTS -------------------------------------------------------------------

def get_app_meta(api_key, app_id):
    try:
        # import pdb; pdb.set_trace()
        headers = {'x-requested-with': 'BackliftCLI',
                   'x-cli-version': VERSION}
        r = requests.get(backliftURL['getappmeta'] % app_id, headers=headers,
                          auth=HTTPBasicAuth('api', api_key), verify=False)
        check_response(r)

        r = json.loads(r.text)
        return r

    except requests.exceptions.ConnectionError:
        fail(ERR_SERVER)

    return None


def create_app(path, api_key, name, template, force=False):
    try:
        # import pdb; pdb.set_trace()
        headers = {'x-requested-with': 'BackliftCLI',
                   'x-cli-version': VERSION}

        r = requests.get(backliftURL['checkname'] % name, 
                          auth=HTTPBasicAuth('api', api_key), 
                          verify=False, headers=headers)
        check_response(r)

        app_id = json.loads(r.text)['_id']
        check_backlift_cfg(path, app_id, force=force)

        r = requests.post(backliftURL['create'], 
                          data={'appname': name, 'template': template},
                          auth=HTTPBasicAuth('api', api_key), 
                          verify=False, headers=headers)
        check_response(r)

        setup_app(path, app_id, force=force)

        return app_id

    except requests.exceptions.ConnectionError:
        fail(ERR_SERVER)

    return None


def delete_app(api_key, app_id):
    try:
        # import pdb; pdb.set_trace()
        headers = {'x-requested-with': 'BackliftCLI',
                   'x-cli-version': VERSION}
        r = requests.delete(backliftURL['delete'] % app_id, headers=headers,
                            auth=HTTPBasicAuth('api', api_key), verify=False)
        check_response(r)

    except requests.exceptions.ConnectionError:
        fail(ERR_SERVER)

    return None


def create_superuser(api_key, app_id, username, password):
    try:
        # import pdb; pdb.set_trace()
        data={'username': username, 'password': password}
        headers = {'x-requested-with': 'BackliftCLI',
                   'x-cli-version': VERSION}
        res = requests.post(backliftURL['createsuperuser'] % app_id, 
                          auth=HTTPBasicAuth('api', api_key), verify=False,
                          headers=headers, data=data)
        check_response(res)

        res = json.loads(res.text)
        return res['_id']

    except requests.exceptions.ConnectionError:
        fail(ERR_SERVER)

    return None


def download_template_files(path, template, api_key, params=None):
    files = []
    try:
        # import pdb; pdb.set_trace()

        headers = {'x-requested-with': 'BackliftCLI',
                   'x-cli-version': VERSION}
        manifest_url = os.path.join(backliftURL['templatefiles'], template)
        r = requests.get(manifest_url, 
                         auth=HTTPBasicAuth('api', api_key), verify=False,
                         headers=headers)
        check_response(r)

        r = json.loads(r.text)
        files = r['files']

        if len(files) > 0:
            for f in files:

                file_url = os.path.join(backliftURL['templatefiles'], template, f)
                r = requests.get(file_url, params=params, 
                                 auth=HTTPBasicAuth('api', api_key), verify=False,
                                 headers=headers)
                check_response(r)

                filepath = os.path.abspath(os.path.join(path, f))

                if os.path.exists(filepath):
                    print "Skipping %s (file exists)" % f
                    continue

                newfile = open_create(filepath, 'wb')
                newfile.write(r.content)
                newfile.close()
                print "Creating %s" % f

    except requests.exceptions.ConnectionError:
        fail(ERR_SERVER)

    return None


def upload_files(id, files, api_key):
    try:
        headers = {'x-requested-with': 'BackliftCLI',
                   'x-cli-version': VERSION}
        r = requests.post(backliftURL['upload'] % id, files=files,
                          auth=HTTPBasicAuth('api', api_key), verify=False,
                          headers=headers)

        for filekey, filedata in files.items():
            filedata[1].close()

        check_response(r)

        r = json.loads(r.text)

        print "%d files uploaded to the backlift sandbox\n" % r['count']
        print "Admin url -->> \n%s\n" % r['admin_url']
        print "Your app is hosted at -->> \n%s\n" % r['app_url']

    except requests.exceptions.ConnectionError:
        fail(ERR_SERVER)


## COMMANDS -------------------------------------------------------------------


def setup(api_key):
    save_api_key(api_key)


def create(path, name, template='init', mkpath=True, force=False):

    # import pdb; pdb.set_trace()

    api_key = read_api_key()

    app_root = os.path.normpath(os.path.abspath(path))
    if mkpath:
        app_root = os.path.normpath(os.path.join(app_root, name))

    id = create_app(app_root, api_key, name, template, force=force)
    if id:
        if mkpath:
            print "Downloading template into %s" % app_root
        download_template_files(app_root, template, api_key)
        print "This app will be called %s." % id

    else:
        fail(ERR_BADID)


def delete(path, name, force=False):

    if not force:
        print "Are you sure? Use -f or --force to complete this action.\n"+\
              "Note: delete will only remove the project from the backlift\n"+\
              "server. The local project folder will not be effected."
        return

    # import pdb; pdb.set_trace()

    api_key = read_api_key()

    app_root = os.path.normpath(
                    os.path.abspath(
                        os.path.join(path, name)))

    app_id = get_id(app_root)

    if app_id:
        delete_app(api_key, app_id)

        print "App deleted. Note: the local app folder has not been effected."

    else:
        fail(ERR_BADID)


def init(path, name, force=False):
    create(path, name, mkpath=False, force=force)


def push(path, skip_hidden):

    # import pdb; pdb.set_trace()

    api_key = read_api_key()

    id = get_id(path)

    # scan path for files to upload 

    files = collectFiles(path, skip_hidden)

    upload_files(id, files, api_key)

    return id


def watch(path, skip_hidden):

    # import pdb; pdb.set_trace()

    api_key = read_api_key()

    id = push(path, skip_hidden)

    before = scanFiles(path, skip_hidden)

    try:
        while 1:
            time.sleep (0.5)
            after = scanFiles(path, skip_hidden)
            
            added = [f for f in after if not f in before]
            removed = [f for f in before if not f in after]
            modified = [f for f in after if \
                (f in before and f in after and after[f] != before[f])]
            
            if added: print "Added: ", ", ".join (added)
            if removed: print "Removed: ", ", ".join (removed)
            if modified: print "Modified: ", ", ".join (modified)
            
            if added or removed or modified:    
                # import pdb; pdb.set_trace()
                files = collectFiles(path, skip_hidden)        
                upload_files(id, files, api_key)
    
            before = after

    except KeyboardInterrupt:
        pass


def open_browser(path, admin=False):

    # import pdb; pdb.set_trace()

    api_key = read_api_key()

    app_id = get_id(path)

    meta = get_app_meta(api_key, app_id)

    if admin:
        url = meta.get('_admin_url', '')
    else:
        url = meta.get('_app_url', '')

    if not url:
        fail(ERR_NOURL)

    webbrowser.open_new_tab(url)

def make_su(path, username, password):

    # import pdb; pdb.set_trace()

    api_key = read_api_key()
 
    app_id = get_id(path)

    userid = create_superuser(api_key, app_id, username, password)

    if not userid:
        fail(ERR_NOUSER)

## MAIN -----------------------------------------------------------------------

def execute_command_line():

    usagetxt = '%prog COMMAND [options]\n\n' +\
        'Commands:\n' +\
        '  setup API_KEY\t\tAuthorize this computer with your API_KEY\n' +\
        '  create NAME\t\tCreate a new basic backlift app in the NAME folder\n' +\
        '  create:TYPE NAME\tCreate a new backlift app using the TYPE template\n' +\
        '  init NAME\t\tInitialize a backlift app at the given --path (default: current folder)\n' +\
        '  push\t\t\tPush files up to backlift\n' +\
        '  watch\t\t\tObserve path and push files to backlift whenever they change\n' +\
        '  open\t\t\tOpen an app using the default browser\n' +\
        '  admin\t\t\tOpen an app\'s admin page using the default browser\n' +\
        '  delete [NAME]\t\tDelete a backlift app.\n' +\
        '  makesuperuser NAME PASSWORD\tCreate a super user with the given name / password.'

    parser = optparse.OptionParser(usagetxt, version='%prog cli '+VERSION)

    parser.add_option('-p', '--path', dest='path', default='.', 
        help='The path to the working folder. Defaults to "%default"')
    parser.add_option('-u', '--url', dest='url', default=default_backliftURL, 
        help='The URL to backlift\'s server. Defaults to "%default"')
    parser.add_option('-f', '--force', 
        dest='force', action='store_const', const=True, default=False,
        help='Force action.')
    parser.add_option('-H', '--skip-hidden', 
        dest='skip_hidden', action='store_const', const=False, default=True,
        help='Toggle uploading of hidden files. (Files that start with a '+\
            '".") Defaults to "%default"')

    (options, args) = parser.parse_args()

    backlift_root = options.url
    backliftURL['register'] = os.path.join(backlift_root, 'register-early')
    backliftURL['getappmeta'] = os.path.join(backlift_root, 'app-admin/%s')
    backliftURL['delete'] = os.path.join(backlift_root, 'app-admin/%s')
    backliftURL['create'] = os.path.join(backlift_root, 'app-admin')
    backliftURL['templatefiles'] = os.path.join(backlift_root, 'app-templates')
    backliftURL['upload'] = os.path.join(backlift_root, 'app-admin/%s/files/upload')
    backliftURL['createsuperuser'] = os.path.join(backlift_root, 'createsuperuser/%s')
    backliftURL['checkname'] = os.path.join(backlift_root, 'checkname/%s')

    if len(args) < 1:
        parser.print_help()
    else:
        if   args[0].lower() == 'setup':
            if len(args) != 2:
                parser.print_help()
            else:
                setup(args[1])
        elif args[0].lower() == 'makesuperuser':
            if len(args) != 3:
                parser.print_help()
            else:
                make_su(options.path, args[1], args[2])
        elif args[0].lower().startswith('create'):
            if len(args) != 2:
                parser.print_help()
            else:
                tokens = args[0].lower().split(':')
                if len(tokens) > 1:
                    create(options.path, args[1], tokens[1], force=options.force)
                else:
                    create(options.path, args[1], 'backbone-basic', force=options.force)
        elif args[0].lower().startswith('delete'):
            if len(args) < 2:
                appname = '.'
            else:
                appname = args[1]
            delete(options.path, appname, options.force)
        elif args[0].lower() == 'init':
            if len(args) != 2:
                parser.print_help()
            else:
                init(options.path, args[1], force=options.force)
        elif args[0].lower() == 'open':
            open_browser(options.path)
        elif args[0].lower() == 'admin':
            open_browser(options.path, admin=True)
        elif args[0].lower() == 'push':
            push(options.path, options.skip_hidden)
        elif args[0].lower() == 'watch':
            watch(options.path, options.skip_hidden)
        else:
            parser.print_help()

if __name__ == "__main__":
    execute_command_line()
