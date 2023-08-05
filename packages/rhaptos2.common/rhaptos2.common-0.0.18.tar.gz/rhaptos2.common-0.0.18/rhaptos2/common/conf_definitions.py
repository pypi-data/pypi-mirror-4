
"""
We expect to see 

"""

definitions = {

'bamboo_global':{
            'logserverfqdn': 'log.frozone.mikadosoftware.com',
            'logserverport': '5147',
            'cdn_server_name': 'localhost:5000',
            'statsd_host': 'log.frozone.mikadosoftware.com',
            'statsd_port': '8125',
            'use_logging': 'Y',
            'loglevel': 'DEBUG',
            'www_server_name': 'localhost:5000',
            'userserver': 'http://localhost:8001/user',
},

'bamboo_deploy': {'appnamespace': 'rhaptos2repo',
            'archive_root': '/opt/cnx/archive',
            'code_root': '/home/pbrian/src/rhaptos2.repo',
            'confdir': '/tmp/confdir',
            'deployagent': 'deployagent',
            'deployagent_keypath': '/home/pbrian/.ssh/deployagent',
            'install_to': 'www.frozone.mikadosoftware.com::www.frozone.mikadosoftware.com',
            'modusdir': '/home/pbrian/src/bamboo.recipies/recipies/',
            'remote_build_root': '/home/deployagent/',
            'stage_root': '/opt/cnx/stage/rhaptos2.repo',
            'venvpath': '/opt/cnx/venv/t1',
            'www_server_root': '/usr/share/www/nginx/www',
            'xunitfilepath': '/opt/cnx/nosetests.xml'},

 'rhaptos2repo': {'aloha_staging_dir': '/opt/cnx/stage/rhaptos2.repo/aloha/',
                  'css_staging_dir': '/opt/cnx/stage/rhaptos2.repo/css/',
                  'js_staging_dir': '/opt/cnx/stage/rhaptos2.repo/js/',
                  'openid_secretkey': 'usekeyczar',
                  'pgdbname': 'repouser',
                  'pghost': 'devlog.office.mikadosoftware.com',
                  'pgpassword': 'pass1',
                  'pgpoolsize': '5',
                  'pgusername': 'repouser',
                  'repodir': '/usr/local/var/cnx/repo',}}


