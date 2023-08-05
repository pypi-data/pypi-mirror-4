# -*- coding: utf-8 -*-
#

import shutil
import os
import tarfile
import time
from paramiko import SSHClient
from subprocess import call
from conf.settings import PROJECT_DIR, MEDIA_ROOT
from release.settings import LOCAL_URL
from celery.task import Task
from django.core.management import call_command
from django.core.validators import URLValidator
from release.models import Release, RegisteredUrl, DeploymentHost


class MakeRelease(Task):
    def run(self, release, **kwargs):
        timestamp = str(time.time())
        release.timestamp = timestamp
        release.save()

        try:
            release.status = 1
            release.save()

            # Remove old htdocs folder
            htdocs = os.path.join(PROJECT_DIR, '../..', 'htdocs')
            shutil.rmtree(htdocs, ignore_errors=True,)
            excluded_media = list([u'admin', u'release'])
            release_excluded_media = release.excluded_media.split(',')

            for rem in release_excluded_media:
                excluded_media.append(rem)

            # Run django commands and build out static version
            call(['python',
                  'manage.py',
                  'staticsitegen',
                  '--settings=conf.build'
                  ])
            call_command('collectstatic',
                         interactive=False,
                         ignore_patterns=excluded_media,
                         )

            # Move media to builded htdocs
            try:
                src = os.path.join(PROJECT_DIR, '..', 'static')
                dst = os.path.join(PROJECT_DIR, '../../htdocs', 'static')
                shutil.move(src, dst)
                shutil.rmtree(src, ignore_errors=True,)
            except:
                pass

            # Make tar.gz archive and move to media
            filename = 'htdocs.%s.tar.gz' % (timestamp)

            dirlist = os.listdir(htdocs)
            archive = tarfile.open(filename, 'w:gz')
            for obj in dirlist:
                path = os.path.join(PROJECT_DIR, '../../htdocs/', obj)
                archive.add(path, arcname=obj)
            archive.close()
            archive_src = os.path.join(PROJECT_DIR, '..', filename)
            archive_dst = os.path.join(PROJECT_DIR,
                                       '../media/release/archives',
                                       filename)
            shutil.move(archive_src, archive_dst)
            shutil.rmtree(htdocs, ignore_errors=True,)

            release.archive = 'release/archives/%s' % (filename)
            release.status = 2
            release.done = True
            release.save()
        except:
            release.status = 3
            release.done = False
            release.save()

        return None


class ValidateURLs(Task):
    def run(self, **kwargs):
        registeredurl_list = RegisteredUrl.objects.all()
        validate = URLValidator(verify_exists=True)

        for registeredurl in registeredurl_list:
            url = LOCAL_URL + registeredurl.url
            registeredurl.status = 2
            registeredurl.save()

            try:
                validate(url)
                registeredurl.status = 1
                registeredurl.checked = True
                registeredurl.save()
            except:
                registeredurl.status = 1
                registeredurl.checked = False
                registeredurl.save()


class DeployRelease(Task):
    def run(self, *args, **kwargs):
        release = Release.objects.get(pk=kwargs['release_id'])
        host = DeploymentHost.objects.get(pk=kwargs['host_id'])
        filename = u'htdocs.%s.tar.gz' % (release.timestamp)
        path = os.path.join(MEDIA_ROOT, 'release/archives/', filename)
        hostname = host.host
        hostpath = host.path
        hostuser = host.user
        hostpass = host.password

        # Deployment on local machine
        if host.type is 0:
            call(['mkdir', '-p', '%s/htdocs' % hostpath])
            call(['rm', '-r', '%s/htdocs/*' % hostpath])
            call(['tar', 'xfvz', path, '-C', '%s/htdocs/' % hostpath])

        # Deployment via FTP
        # This is not the best solution but it works.
        elif host.type is 1:
            tmp_path = os.path.join(MEDIA_ROOT, 'release/archives/tmp')
            call(['mkdir', '-p', tmp_path])
            call(['tar', 'xzfv', path, '-C', tmp_path])

            paths = os.listdir(tmp_path)
            for path in paths:
                src_dir = os.path.join(tmp_path, path)

                call(['ncftpput',
                      '-R',
                      '-u', hostuser,
                      '-p', hostpass,
                      hostname,
                      hostpath,
                      src_dir])

            call(['rm', '-r', tmp_path])

        # Deployment via SSH
        elif host.type is 2:
            call(['scp', path, '%s:%s' % (hostname, hostpath)])
            client = SSHClient()
            client.load_system_host_keys()
            client.connect(hostname=hostname, username=hostuser)
            chan = client.get_transport().open_session()
            chan.exec_command('cd %s; tar xfvz ./%s -C ./htdocs/; rm -r ./%s'
                              % (hostpath, filename, filename))
            chan.recv_exit_status()
            chan.close()
            client.close()

        # set release status to done
        release.status = 2
        release.save()
