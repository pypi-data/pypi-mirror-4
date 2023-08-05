Xost
================================

Xost is a small embedded server which simplifies hosting of django applications.

Requirements
------------
twisted

Usage
-----
Installing the application:
    pip install xost

add xost to your INSTALLED_APPS: ::  

    INSTALLED_APPS = (
        ....,
        ‘xost’
    )

Xost is configured via the XOST key in settings.py: ::

    XOST= {
        ‘key’: ‘value’
    }


possible configuration keys are listed below (default values are provided after = sign): ::

    address: None - string configuration listen addresses
    port = 8080 - a port number on which to listen
    min_threads = 5 - minimum number of threads in the pool
    max_threads = 20 - maximum number of threads in the pool
    root = ‘launch_folder’ - path to working (root) folder
    static_root = ‘launch_folder/static/’ - path to static file folder
    media_root = ‘launch_folder/media/ - path to media file folder
    log_path = ‘launch_folder/log/’ -path to log folder
    collect_static = True - do not collect static files to  static root folder before launch
    debug = False - if set to true, prints debug information


startup: ::

    python manage.py serve

by default server starts on port 8080


in order to get full list of configuration keys, run ::

    python manage.py serve --help
