===========
FSGDeploy
===========

Deployment made simple.  Use FSGDeploy to deploy from Linux, Mac, or Windows to Linux or Windows.  FSGDeploy supports MSSQL, IIS, PHP, Google Closure CSS and JS optimization, CSS/JS auto-versioning and a host of other common deployment activities.  In your selected deployment directory, use the following structure::

    sites\site_name\env_name.ini
    Python27\Lib\site-packages\FSGDeploy_util\compiler.jar
    Python27\Lib\site-packages\FSGDeploy_util\stylesheets.jar

Optional (for scripts or scheduled tasks)::

    sites\site_name\db\script.sql
    sites\site_name\scheduled_tasks\task.ini

For example execution, run "**deploy**" in terminal/cmd from within your deployment directory.

If only one site exists, *env ini* files may be located in the root level and site flag should not be used.

Utilities
-------------

* `compiler.jar <http://closure-compiler.googlecode.com/files/compiler-latest.zip>`_

* `Closure-stylesheets.jar <https://code.google.com/p/closure-stylesheets/downloads/detail?name=closure-stylesheets-20111230.jar&can=2&q=>`_ - rename to stylesheets.jar


Example ini
-------------

staging.ini::

    [actions]
    deploy_server
    migrate_config
    apply_database_migrations
    reset_iis
    register_scheduled_tasks
    verify
    # actions may be commented out
    
    [server]
    host = mysite.com
    user = deploy
    # os options: Windows, Centos
    os = Windows
    # remove exclude line if no files should be excluded
    exclude = exampleWildcardFile
    
    [database]
    host = db.mysite.com
    user = dbUser
    password = dbPass
    database = my_db
    
    [path]
    deploy_to = c:\inetpub\wwwroot
    backup_to = c:\bak
    
    [scm]
    repo = ssh://hg@bitbucket.org/my/repo
    branch = default
    build_profile = Release
    auto_version = css,js,htm,html,jpg,jpeg,gif,png
    #solution_filename used for building C# site
    solution_filename = MySite.sln
    site_directory = MySite
    
    [twitter]
    username = twitterbot
    consumer_key = dsf98r298urjkfd
    consumer_secret = HKJLRP8ASf89pfhas789789Rjklf907uosiar
    access_token = LJKjlkO8FRO8A3WO845O8729378598723589ADKLAJljkfjlkl
    access_token_secret = Kckj89U3098UkfjlKC089AUW034ORJkcjlKF098u3jk
    
    [jira]
    username = jiraUser
    password = jiraPass
    server = https://jiraSite.atlassian.net