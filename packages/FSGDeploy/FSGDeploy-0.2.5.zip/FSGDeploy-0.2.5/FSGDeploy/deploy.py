import sys
import os

import datetime
import ConfigParser
import tempfile
import subprocess
import importlib
import tempfile
import shutil
import glob
import hashlib
import time
import urllib
import urllib2
import base64
import httplib

# Helpers #########################################################################################
def run(args, inOS):
	p = ""
	if inOS != "win32": p = subprocess.Popen(args, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
	else:  p = subprocess.Popen(args, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
	out, err = p.communicate()
	if err: out = err
	return out

def tryimport(module):
	try:
		pkg = importlib.import_module(module)
		return True
	except:
		return False
	return False
	
def escapequote(toescape):
	toescape = toescape.replace("\"", "\\\"")
	toescape = toescape.replace("'", "\\'")
	return toescape

def posttwitter(settings, message):
	if(len(message) > 160):
		return

	auth = tweepy.OAuthHandler(settings.get("twitter", "consumer_key"), settings.get("twitter", "consumer_secret"))
	auth.set_access_token(settings.get("twitter", "access_token"), settings.get("twitter", "access_token_secret"))

	api = tweepy.API(auth)

	api.update_status(message)

def getjiraversion(settings):
        options = {
                'server': settings.get("jira","server")
                }
        jira = JIRA(options,basic_auth=(settings.get("jira","username"),settings.get("jira","password")))
        sprintItems = jira.search_issues('sprint in openSprints()')
        jVersion = ""
        for issue in sprintItems:
                if issue.fields.fixVersions and jVersion == "":
                        jVersion = issue.fields.fixVersions[0].description
        return jVersion

def getrandomword():
	r = urllib2.urlopen("http://randomword.setgetgo.com/get.php")
	return r.read()

def main():
        # Main Script #####################################################################################
        datetimestarted = datetime.datetime.now()
        utilPath = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'FSGDeploy_util'))
        closurePath = os.path.join(utilPath,"compiler.jar")
        cssPath = os.path.join(utilPath,"stylesheets.jar")
        # Read deployment type, assume development by default
        environment = ""
        systemuser = ""
        clientOS = sys.platform
        if clientOS == "win32": systemuser = os.environ['USERNAME']
        else: systemuser = os.environ['USER']
        entrypoint = os.getcwd()
        randomWord = ""
        versionTitle = ""
        site = ""
        tempdir = ""
        actionTweet = False
        actionJira = False
        actionVerbose = False
        osType = ""
        usePassword = False
        actionOptimize = False
        optimizationLevel = "SIMPLE_OPTIMIZATIONS"
        actionCSS = False
        deployStart = datetimestarted
        deployFinish = ""
        uploadStart = ""
        uploadFinish = ""
        buildStart = ""
        buildFinish = ""
        pullStart = ""
        pullFinish = ""
        optimizeStart = ""
        optimizeFinish = ""


        if not sys.argv[1:]:
                print "Allowed flags:"
                print "v\t\t\tVerbose mode"
                print "site:site_name\t\tSite to deploy"
                print "env:env_name\t\tEnvironment to deploy"
                print "o[:OPTIMIZATION_LEVEL]\tUse Closure to optimize Javascript.  Levels: WHITESPACE_ONLY SIMPLE_OPTIMIZATIONS ADVANCED_OPTIMIZATIONS.  Defaults to SIMPLE_OPTIMIZATIONS"
                print "css\t\t\tUse Closure to optimize stylesheets."
                print "tweet[:word]\t\tTweet to Twitter upon start/completion (without word, random word will be used as a hashtag).  tweet:date will make the current date the hashtag"
                print "jira\t\t\tPulls fix version from JIRA to write in tweet (tweet flag must also be used)"
                print "Example: deploy tweet:helloWorld jira v site:projectpeach env:staging o"
                exit(1)
                
        for argvFlag in sys.argv[1:]:
                splitFlag = argvFlag.partition(":")
                if splitFlag[0].lower() == "site":
                        site = splitFlag[2].strip().lower()
                elif splitFlag[0].lower() == "env":
                        environment = splitFlag[2].strip().lower()
                elif splitFlag[0].lower() == "tweet":
                        actionTweet = True
                        if splitFlag[2]:
                                if splitFlag[2].lower() == "date":
                                        randomWord = datetimestarted.strftime("%Y%m%d_%H%M%S")
                                else:
                                        randomWord = splitFlag[2]
                        else:
                                randomWord = getrandomword()
                elif splitFlag[0].lower() == "jira":
                        actionJira = True
                elif splitFlag[0].lower() == "v":
                        actionVerbose = True
                elif splitFlag[0].lower() == "o":
                        actionOptimize = True
                        if splitFlag[2]:
                                if splitFlag[2] == "WHITESPACE_ONLY" or splitFlag[2] == "SIMPLE_OPTIMIZATIONS" or splitFlag[2] == "ADVANCED_OPTIMIZATIONS":
                                        optimizationLevel = splitFlag[2]
                                else:
                                        print "Invalid optimization level.  Please run script with no flags for a list of valid options."
                                        exit(1)
                elif splitFlag[0].lower() == "css":
                        actionCSS = True
                        
        print "##################### START DEPLOYMENT ##########################"
        if environment == "":
                print "Environment flag must be set.  Change this with env flag -- 'deploy site:projectpeach env:staging'"
                exit(1)

        if site == "":
                print "Defaulting to local site.  Change this with site flag -- 'deploy site:projectpeach env:staging'"

        # Load settings file for environment
        settings = ConfigParser.RawConfigParser(allow_no_value=True)

        if site: settings.read(os.path.join(entrypoint, "sites", site, environment + ".ini"))
        else: settings.read(os.path.join(entrypoint, environment + ".ini"))
        if settings.has_option("actions", "verify"):
                verifyOp = raw_input("Deploy " + site + " to " + environment + "? (Y/n): ")
                if verifyOp.lower() != "y":
                        exit(1)
        print "Starting deployment to " + site + " " + environment

        ssh = None
        if settings.has_option("server", "password"):
                usePassword = True

        # Run pre deploy checks ###########################################################################
        print "Running pre-deployment checks"
        failed = False

        osType = settings.get("server", "os").lower()

        if actionOptimize or actionCSS:
                # Java
                print "Java installed?"
                out = run(["java", "-version"],"win32")
                if "Java(TM)" in out:
                        print "[OK]"
                else:
                        print "[FAILED]"
                        print "Download and install Java"
                        print "When running a 64-bit machine, try copying java.exe from System32 to SysWoW64"
                        failed = True
                if actionOptimize:
                        print "compiler.jar located in Python\Lib\site-packages\FSGDeploy_util?"
                        if os.path.isfile(closurePath):
                                print "[OK]"
                        else:
                                print "[FAILED]"
                                print "Download compiler.jar to Python\Lib\site-packages\FSGDeploy_util."
                                print "http://closure-compiler.googlecode.com/files/compiler-latest.zip"
                                failed = True
                if actionCSS:
                        print "stylesheets.jar located in Python\Lib\site-packages\FSGDeploy_util?"
                        if os.path.isfile(cssPath):
                                print "[OK]"
                        else:
                                print "[FAILED]"
                                print "Download closure-stylesheets.jar and rename to stylesheets.jar to Python\Lib\site-packages\FSGDeploy_util."
                                print "https://code.google.com/p/closure-stylesheets/downloads/detail?name=closure-stylesheets-20111230.jar&can=2&q="
                                failed = True

        if settings.has_option("actions", "apply_database_migrations"):
                # pymssql
                print "pymssql installed?"
                if tryimport("pymssql"):
                        print "[OK]"
                else:
                        print "[FAILED]"
                        print "Download and install pymssql"
                        print "http://www.lfd.uci.edu/~gohlke/pythonlibs/#pymssql"
                        failed = True

        if actionTweet:		
                # tweepy
                print "tweepy installed?"
                if tryimport("tweepy"):
                        print "[OK]"
                else:
                        print "[FAILED]"
                        print "Download and install tweepy"
                        print "pip install tweepy or"
                        print "https://github.com/tweepy/tweepy/"
                        failed = True

        if actionJira:		
                # jira
                print "jira-python installed?"
                if tryimport("jira.client"):
                        print "[OK]"
                else:
                        print "[FAILED]"
                        print "Download and install jira-python"
                        print "pip install jira-python or"
                        print "https://bitbucket.org/bspeakmon_atlassian/jira-python"
                        failed = True

        if settings.has_option("actions", "deploy_server"):
                # Mercurial
                print "Hg installed?"
                out = run(["hg", "--version"],"win32")
                if "Mercurial Distributed SCM" in out:
                        print "[OK]"
                else:
                        print "[FAILED]"
                        print "How did you get this script then?  Download and install tortiseHG"
                        failed = True

                if osType == "windows":
                        # MSBuild
                        msbuildlocation = os.path.join(os.environ["WINDIR"], "Microsoft.NET", "Framework", "v4.0.30319", "MSBuild.exe")
                        print "MSBuild installed?"
                        if actionVerbose: print msbuildlocation
                        if os.path.exists(msbuildlocation):
                                print "[OK]"
                        else:
                                print "[FAILED]"
                                failed = True

        if settings.has_option("actions", "deploy_server") or settings.has_option("actions", "register_scheduled_tasks") or  settings.has_option("actions", "reset_iis"): 
                # Paramiko
                print "Paramiko installed?"
                if tryimport("paramiko"):
                        print "[OK]"
                else:
                        print "[FAILED]"
                        print "Download and install pycrypto / paramiko"
                        print "http://www.voidspace.org.uk/python/modules.shtml#pycrypto"
                        print "pip install paramiko"
                        failed = True

                # SSH public key?
                print "Local SSH private key generated?"
                pathtokey = os.path.join(os.path.expanduser("~"), ".ssh","private_key.ssh")
                if os.path.exists(pathtokey):
                        print "[OK]"
                else:
                        print "[FAILED]"
                        print "File not found", pathtokey
                        failed = True

                # Connect to remote server
                import paramiko
                print "Able to connect to remote server?"
                try:
                        ssh = paramiko.SSHClient()
                        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                        if usePassword:
                                ssh.connect(settings.get("server", "host"), username=settings.get("server", "user"), password=settings.get("server","password"))
                        else:
                                ssh.connect(settings.get("server", "host"), username=settings.get("server", "user"), key_filename=pathtokey)
                        stdin, stdout, stderr = ssh.exec_command("hostname")
                        out = stdout.read()
                        print "[OK]"
                except Exception as e:
                        print "[FAILED]"
                        print "Is your key on the server?"
                        print str(e)
                        failed = True
                        
        if osType == "windows" and settings.has_option("actions", "deploy_server"):		
                # 7zip installed on server?
                print "7zip installed on server?"
                zipbinpath = os.path.join(os.environ["SystemDrive"] + "\\", "Program Files", "7-Zip", "7z.exe") # note that this is actually not correct.  I am not sure how to evaluate REMOTE environment vars, so we assume local same (bad assumption)
                stdin, stdout, stderr = ssh.exec_command("attrib " + zipbinpath)
                if "File not found" in stdout.read():
                        print "[FAILED]"
                        print "7zip not installed on server", zipbinpath
                        failed = True
                else:
                        print "[OK]"
                
        # If any failed, exit before starting
        if failed:
                print "One or more pre-checks failed.  Exiting."
                exit(1)

        # Execute Deployment ##############################################################################	
        print "All pre-checks passed, starting deployment"

        # tweet start
        if actionTweet:
                import tweepy
                if actionJira:
                        from jira.client import JIRA
                        versionTitle = getjiraversion(settings)
                        posttwitter(settings, systemuser + " is deploying " + site + " fix version " + versionTitle.encode("utf-8") + " to " + environment + "!  #" + randomWord)
                else:
                        posttwitter(settings, systemuser + " is deploying " + site + " to " + environment + "! #" + randomWord)

        if settings.has_option("actions", "deploy_server"):
                # check for existing deployment
                print "Checking for site deployment lock"
                cmd = ""
                if osType == "windows": cmd = "cmd /c attrib \"" + os.path.join(settings.get("path", "backup_to"), "deploy.lock") + "\""
                elif osType == "centos": cmd = "ls \"" + os.path.join(settings.get("path", "backup_to"), "deploy.lock") + "\""
                if actionVerbose: print cmd
                stdin, stdout, stderr = ssh.exec_command(cmd)
                result = stdout.read()
                if (osType == "windows" and "File not found" not in result) or (osType == "centos" and result):
                        print "Deployment already in process."
                        print "Exiting."
                        exit(1)
                # lock server
                print "Locking server for deployment"
                if osType == "windows": cmd = "cmd /c echo \"lock\" > \"" + os.path.join(settings.get("path", "backup_to"), "deploy.lock") + "\""
                elif osType == "centos": cmd = "touch \"" + os.path.join(settings.get("path", "backup_to"), "deploy.lock") + "\""
                if actionVerbose: print cmd
                stdin, stdout, stderr = ssh.exec_command(cmd)
                result = stdout.read()
                if actionVerbose: print result
                ssh.close()

                # clone branch into temp dir
                print "Cloning repository"
                pullStart = datetime.datetime.now()
                tempdir = tempfile.mkdtemp()
                cmd = "hg clone" + " -r " + settings.get("scm", "branch") + " " + settings.get("scm", "repo") + " \"" + tempdir + "\""
                if actionVerbose: print cmd
                out = run(cmd, clientOS)
                if actionVerbose: print out
                pullFinish = datetime.datetime.now()
                
                if actionOptimize or actionCSS or settings.has_option("scm", "auto_version"):
                        optimizeStart = datetime.datetime.now()
                        multOpt = False
                        optText = ""
                        if actionOptimize:
                                if multOpt:
                                        optText += ", "
                                optText += "Optimizing Javascript with Closure"
                                multOpt = True
                        if actionCSS:
                                if multOpt:
                                        optText += ", "
                                optText += "Optimizing stylesheets with Closure"
                                multOpt = True
                        if settings.has_option("scm", "auto_version"):
                                if multOpt:
                                        optText += ", "
                                optText += "Auto-versioning Javascript and stylesheet files"
                                multOpt = True
                        print optText
                        hash = hashlib.sha1(str(time.time()).encode("UTF-8")).hexdigest()[:6] # generate hash based off of timestamp
                        for root, subFolders, files in os.walk(tempdir):
                                for file in files:
                                        fullpath = os.path.join(root,file)
                                        if actionOptimize:
                                                # use Closure to optimize JS
                                                if fullpath.lower().endswith((".js")):
                                                        cmd = "java -jar " + closurePath + " --jscomp_off=internetExplorerChecks --warning_level QUIET --compilation_level " + optimizationLevel + " --js " + fullpath
                                                        if actionVerbose: print cmd
                                                        out = run(cmd, clientOS)
                                                        f = open(fullpath, 'w')
                                                        f.write(out)
                                                        f.close()
                                        if actionCSS:
                                                # use Closure to optimize CSS
                                                if fullpath.lower().endswith((".css")):
                                                        cmd = "java -jar " + cssPath + " " + fullpath
                                                        if actionVerbose: print cmd
                                                        out = run(cmd, clientOS)
                                                        f = open(fullpath, 'w')
                                                        f.write(out)
                                                        f.close()
                                        if settings.has_option("scm", "auto_version"):
                                                # auto-version Javascript/stylesheets
                                                if fullpath.lower().endswith((".master",".inc",".aspx",".ascx",".php",".htm",".html")):
                                                        f = open(fullpath, 'r')
                                                        filetext = f.read()
                                                        f.close()
                                                        filetext = filetext.replace(".css\"", ".css?" + hash + "\"")
                                                        filetext = filetext.replace(".js\"", ".js?" + hash + "\"")
                                                        f = open(fullpath, 'w')
                                                        f.write(filetext)
                                                        f.close()
                        optimizeFinish = datetime.datetime.now()
                                                
                if osType == "windows":
                        # build project
                        buildStart = datetime.datetime.now()
                        print "Building project"
                        cmd = msbuildlocation + " " + os.path.join(tempdir, "FSG.sln") + " /p:Configuration=" + settings.get("scm", "build_profile")
                        if actionVerbose: print cmd
                        out = run(cmd, clientOS)
                        if "0 Error(s)" not in out:
                                print out
                                print "Build failed.  Somebody owes you lunch."
                                print "Exiting."
                                exit(1)
                        else:
                                if actionVerbose: print out
                        buildFinish = datetime.datetime.now()

                # bundling project
                print "Compressing new client-side site"
                pathtozip = ""
                if osType == "windows": pathtozip = shutil.make_archive(os.path.join(tempdir, "site"), "zip", root_dir=os.path.join(tempdir, "Fsg"))
                elif osType == "centos": pathtozip = shutil.make_archive(os.path.join(tempdir, "site"), "gztar", root_dir=os.path.join(tempdir))
                if actionVerbose: print pathtozip

                # backup current server
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                if usePassword:
                        ssh.connect(settings.get("server", "host"), username=settings.get("server", "user"), password=settings.get("server","password"))
                else:
                        ssh.connect(settings.get("server", "host"), username=settings.get("server", "user"), key_filename=pathtokey)
                        
                print "Backing up old server-side site"
                cmd = ""
                if osType == "windows": cmd = "\"" + zipbinpath + "\"" + " a -tzip -r " + settings.get("path", "backup_to") + datetimestarted.strftime("\\%Y%m%d_%H%M%S") + ".zip " + settings.get("path", "deploy_to") + "\\*.*"
                elif osType == "centos": cmd = "tar -cpzf \"" + settings.get("path", "backup_to") + datetimestarted.strftime("%Y%m%d_%H%M%S") + ".tar.gz\" " + "-C \"" + settings.get("path", "deploy_to") + "\" ."
                if actionVerbose: print cmd
                stdin, stdout, stderr = ssh.exec_command(cmd)
                result = stdout.read()
                if actionVerbose: print result

                # delete existing
                print "Removing old server-side site"
                if settings.has_option("server", "exclude"):
                        excludeWords = settings.get("server", "exclude").split(',')
                        if osType == "windows": cmd = "cmd /c dir /a-d /b /s \"" + settings.get("path", "deploy_to") + "\""
                        elif osType == "centos": cmd = "find \"" + settings.get("path", "deploy_to") + "\" -type f"
                        stdin, stdout, stderr = ssh.exec_command(cmd)
                        result = stdout.read()
                        allFiles = result.split('\n')
                        for aFile in allFiles:
                                for file in files:
                                        canDelete = True
                                        for excludeWord in excludeWords:
                                                if excludeWord.lower() in aFile.lower(): canDelete = False
                                        if canDelete and file:
                                                if osType == "windows": cmd = "cmd /c del /s /q \"" + aFile + "\""
                                                elif osType == "centos": cmd = "rm -f \"" + aFile + "\""
                                                if actionVerbose: print cmd
                                                stdin, stdout, stderr = ssh.exec_command(cmd)
                                                result = stdout.read()
                                                if actionVerbose: print result
                else:
                        if osType == "windows": cmd = "cmd /c del /s /q \"" + settings.get("path", "deploy_to") + "\\*\""
                        elif osType == "centos": cmd = "rm -rf \"" + settings.get("path", "deploy_to") + "\"*"
                        if actionVerbose: print cmd
                        stdin, stdout, stderr = ssh.exec_command(cmd)
                        result = stdout.read()
                        if actionVerbose: print result

                # transferring to server
                print "Transferring new client-side site to server"
                uploadStart = datetime.datetime.now()
                reldeploypath = ""
                if osType == "windows": reldeploypath = settings.get("path", "deploy_to")[2:] # we have to use relative path for scp.  this would blow up if our ftp root was not c:\
                elif osType == "centos": reldeploypath = settings.get("path", "backup_to")
                if actionVerbose: print reldeploypath
                sftp = ssh.open_sftp()
                if osType == "windows": sftp.put(pathtozip, os.path.join(reldeploypath, "fsg.zip"))
                elif osType == "centos": sftp.put(pathtozip, os.path.join(reldeploypath, "site.tar.gz"))
                sftp.close()
                uploadFinish = datetime.datetime.now()

                # decompress on server
                print "Decompressing new server-side site"
                if osType == "windows": cmd = "\"" + zipbinpath + "\" x " + os.path.join(settings.get("path", "deploy_to"), "fsg.zip") + " -o" + settings.get("path", "deploy_to") + " -y"
                elif osType == "centos": cmd = "tar -xpzf \"" + settings.get("path", "backup_to") + "site.tar.gz\" " + "-C \"" + settings.get("path", "deploy_to") + "\" ."
                if actionVerbose: print cmd
                stdin, stdout, stderr = ssh.exec_command(cmd)
                result = stdout.read()
                if actionVerbose: print result

                # remove deploy file
                print "Removing new server-side archive"
                if osType == "windows": cmd = "cmd /c del \"" + os.path.join(settings.get("path", "deploy_to"), "fsg.zip") + "\""
                elif osType == "centos": cmd = "rm \"" + os.path.join(settings.get("path", "backup_to"), "site.tar.gz") + "\""
                if actionVerbose: print cmd
                stdin, stdout, stderr = ssh.exec_command(cmd)
                result = stdout.read()
                if actionVerbose: print result

        if settings.has_option("actions", "apply_database_migrations"):
                # database schema update
                print "Checking for database schema tracking table"
                import pymssql
                dbcon = pymssql.connect(host=settings.get("database", "host"), user=settings.get("database", "user"), password=settings.get("database", "password"), database=settings.get("database", "database"))
                dbcur = dbcon.cursor()

                # check for schema tables
                dbcur.execute("""
                        SELECT COUNT(*)
                        FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE INFORMATION_SCHEMA.COLUMNS.table_name = 'db_schema_version'
                """)
                if dbcur.fetchone()[0] < 1:
                        print "Schema tracking table not found, creating..."
                        dbcur.execute("""
                                        CREATE TABLE [db_schema_version](
                                                [id] INT IDENTITY(1,1) PRIMARY KEY,
                                                [script_name] VARCHAR(255) NOT NULL,
                                                [date_applied] DATETIME NOT NULL
                                        )
                        """)
                        dbcon.commit()

                # Run database migrations
                scriptsPath = ""
                if site: scriptsPath = os.path.join(entrypoint, "sites", site, "db")
                else: scriptsPath = os.path.join(entrypoint, "db")
                scripts = os.listdir(scriptsPath)
                for script in scripts:
                        if not script.endswith(".sql"):
                                continue
                                
                        dbcur.execute("""
                                SELECT COUNT(*)
                                FROM [db_schema_version]
                                WHERE [script_name] = %s
                                """, script
                        )
                        
                        if dbcur.fetchone()[0] < 1:
                                if actionVerbose: print "Executing SQL script ", script
                                scriptPath = ""
                                if site: scriptPath = os.path.join(entrypoint, "sites", site, "db", script)
                                else: scriptPath = os.path.join(entrypoint, "db", script)
                                f = open(scriptPath, "r")
                                sql = f.read()
                                f.close()
                                dbcur.execute(sql)
                                dbcon.commit()
                                
                                dbcur.execute("""
                                        INSERT INTO [db_schema_version] ([script_name], [date_applied])
                                        VALUES(%s, %s)
                                        """, (script, datetime.datetime.now())
                                )
                                dbcon.commit()

                dbcon.close()

        if settings.has_option("actions", "deploy_server") and settings.has_option("actions", "migrate_config"):
                # migrate web config for profile
                print "Copying and renaming Web.config"
                cmd = "cmd /c \"copy /Y \"" + settings.get("path", "deploy_to") + "\\Web." + environment + ".config\" \"" + settings.get("path", "deploy_to") +"\\Web.config\""
                if actionVerbose: print cmd
                stdin, stdout, stderr = ssh.exec_command(cmd)
                result = stdout.read()
                if actionVerbose: print result
                
        if osType == "windows" and settings.has_option("actions", "deploy_server"):
                # run magic command to fix problem with IIS
                print "Migrating Web.config"
                cmd = os.path.join(os.environ["SYSTEMROOT"], "system32", "inetsrv", "appcmd") + " migrate config \"Default Web Site/\""
                if actionVerbose: print cmd
                stdin, stdout, stderr = ssh.exec_command(cmd)
                result = stdout.read()
                if actionVerbose: print result

        if settings.has_option("actions", "reset_iis"):
                # restart IIS
                print "Resetting IIS"
                cmd = "iisreset"
                if actionVerbose: print cmd
                stdin, stdout, stderr = ssh.exec_command(cmd)
                result = stdout.read()
                if actionVerbose: print result

        if settings.has_option("actions", "register_scheduled_tasks"):
                # Re-register scheduled tasks
                tasksPath = ""
                if site: tasksPath = os.path.join(entrypoint, "sites", site, "scheduled_tasks")
                else: tasksPath = os.path.join(entrypoint, "scheduled_tasks")
                tasks = os.listdir(tasksPath)
                for task in tasks:
                        tasksettings = ConfigParser.RawConfigParser()
                        taskPath = ""
                        if site: taskPath = os.path.join(entrypoint, "sites", site, "scheduled_tasks", task)
                        else: taskPath = os.path.join(entrypoint, task)
                        tasksettings.read()
                        
                        # remove task if exists already
                        print "Removing scheduled tasks"
                        cmd = "schtasks /delete /tn \"" + tasksettings.get("scheduled_task", "name") + "\" /f"
                        if actionVerbose: print cmd
                        stdin, stdout, stderr = ssh.exec_command(cmd)
                        result = stdout.read()
                        if actionVerbose: print result
                        
                        # register
                        print "Registering scheduled tasks"
                        cmd = "schtasks /create /tn \"" + tasksettings.get("scheduled_task", "name")  + "\""
                        cmd += " /tr \"" + escapequote(tasksettings.get("scheduled_task", "run")) + "\""
                        cmd += " /sc " + tasksettings.get("scheduled_task", "schedule")
                        if(tasksettings.has_option("scheduled_task", "username")): cmd += " /ru " + tasksettings.get("scheduled_task", "username")
                        if(tasksettings.has_option("scheduled_task", "password")): cmd += " /rp " + tasksettings.get("scheduled_task", "password")
                        if(tasksettings.has_option("scheduled_task", "day")): cmd += " /d " + tasksettings.get("scheduled_task", "day")
                        if(tasksettings.has_option("scheduled_task", "starttime")): cmd += " /st " + tasksettings.get("scheduled_task", "starttime")
                        if actionVerbose: print cmd
                        stdin, stdout, stderr = ssh.exec_command(cmd)
                        result = stdout.read()
                        if actionVerbose: print result

        # unlock server
        if settings.has_option("actions", "deploy_server"):
                print "Removing site deployment lock"
                cmd = ""
                if osType == "windows": cmd = "cmd /c del \"" + os.path.join(settings.get("path", "backup_to"), "deploy.lock") + "\"" 
                elif osType == "centos": cmd = "rm \"" + os.path.join(settings.get("path", "backup_to"), "deploy.lock") + "\""
                if actionVerbose: print cmd
                stdin, stdout, stderr = ssh.exec_command(cmd)
                if actionVerbose: print stdout.read()

        # tweet complete
        if actionTweet:
                if actionJira:
                        posttwitter(settings, "Deployment fix version " + versionTitle.encode("utf-8") + " to " + environment + " DONE! #" + randomWord)
                else:
                        posttwitter(settings, "Deployment to " + environment + " DONE! #" + randomWord)

        # remove cloned repo
        print "Removing client-side cloned repository"
        shutil.rmtree(tempdir)

        print "###################### END DEPLOYMENT ##########################"
        print "Results for deploying " + site + " to " + environment + ":"
        if osType == "windows": print "Build Time: " + str((buildFinish - buildStart).seconds / 60) + " minutes " + str((buildFinish - buildStart).seconds % 60) + " seconds"
        if actionCSS or actionOptimize: print "Optimize Time: " + str((optimizeFinish - optimizeStart).seconds / 60) + " minutes " + str((optimizeFinish - optimizeStart).seconds % 60) + " seconds"
        print "Repo Clone Time: " + str((pullFinish - pullStart).seconds / 60) + " minutes " +str((pullFinish - pullStart).seconds % 60) + " seconds"
        print "Upload Time: " + str((uploadFinish - uploadStart).seconds / 60) + " minutes " + str((uploadFinish - uploadStart).seconds % 60) + " seconds"
        print "Total Deploy Time: " + str((datetime.datetime.now() - deployStart).seconds / 60) + " minutes " +  str((datetime.datetime.now() - deployStart).seconds % 60) + " seconds"

if __name__ == '__main__':
    status = main()
    exit(status)
