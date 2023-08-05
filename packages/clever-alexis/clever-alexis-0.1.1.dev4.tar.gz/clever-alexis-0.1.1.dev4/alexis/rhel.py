#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
For security reason all actions are performed on behalf of user "buildbot" except __init__

/tmp/
└── <prefix>-<appname>-<version>
    ├── app
    ├── static
    └── venv
        ├── bin
        ├── include
        ├── lib
        └── local -> /vrmd/whois/venv
"""
# TODO: use virtualenv-clone script to move virtualenv from /tmp to working directory after unpacking

import sys
import os.path

from fabric.api import  run, cd, put, get, with_settings, sudo, prompt

from alexis import __version__


class Deployment(object):
    """
    Using:
    >>> from alexis.rhel import Deployment
    >>> deploy = Deployment(prefix, app_name)
    >>> deploy.prepare_app(hg_repository, branch)
    >>> deploy.build_rpm()

    As result - downloading rpm packages in local ./rhel directory
    """

    def __init__(self, prefix, app_name, version=None, release=None, build_deps=None, run_deps=None, update_yum=False):
        self.prefix = prefix
        if update_yum:
            sudo('yum update')
        if build_deps:
            sudo('yum install {}'.format(' '.join(build_deps)))

        # If version is not available
        # automatically find installed package
        # and set same version but release +1
        if not version:
            v = sudo('rpm -q {}-{} --qf "%{{version}}"'.format(self.prefix, app_name))
            r = sudo('rpm -q {}-{} --qf "%{{release}}"'.format(self.prefix, app_name))
            try:
                self.version = v
                self.release = str(int(r) + 1)
            except Exception as e:
                # Set default values of version and release
                print('Revision not found in %s. Error:%s' % (r, e))
                self.version = '1.0.0'
                self.release = '1'
        else:
            self.version = version
            self.release = release

        self.app_name = app_name
        self.run_deps = run_deps or []
        self.pkg_name = ('{0.prefix}-{0.app_name}'.format(self)).lower()
        self.base_path = '/tmp/{0.pkg_name}-{0.version}'.format(self)
        self.app_path = os.path.join(self.base_path, self.prefix, self.app_name)
        self.venv_path = os.path.join(self.app_path, 'venv')
        self.src_path = os.path.join(self.app_path, 'app')
        self.static_path = os.path.join(self.app_path, 'static')

    @with_settings(user='buildbot')
    def prepare_app(self,
                    hg_repository,
                    branch,
                    python_path='/usr/bin/python',
                    static_dir='static',
                    requirements='requirements.txt'
    ):
        """
        Create default directories, create a virtualenv, check out src.

        `hg_repository` - source code hg_repository (URL or path)
        `branch` - hg_repository branch name
        `python_path` - path to python
        `static_dir` - path to static in source code hg_repository (./static by default)
        `requirements` - path to requirements file in source code hg_repository (./requirements.txt by default)
        """
        run('rm -rf {0.base_path}'.format(self))
        self.hg_repository = hg_repository
        self.hg_branch = branch
        self.hg_clone()
        with cd(self.src_path):
            self.hg_commit = run('hg parents --template \"{node|short}\"')
            run('mv {} {}'.format(static_dir, self.static_path))
        self.create_virtualenv(python_path)
        run('{} install -r {}'.format(
            os.path.join(self.venv_path, 'bin/pip'),
            os.path.join(self.src_path, requirements))
        )
        # If app need to be installed into virtualenv lets do it

    #        with cd(self.src_path):
    #            if os.path.exists('setup.py'):
    #                run('{} setup.py install'.format(os.path.join(self.venv_path, 'bin/python')))

    @with_settings(user='buildbot')
    def build_rpm(
            self,
            split_pkg=False,
            before_remove=None,
            after_remove=None,
            before_install=None,
            after_install=None

    ):
        """
        Build RPM package.
        """
        with cd(self.src_path):
            self.hg_branch = run('hg branch')
            self.hg_commit = run('hg parents --template \"{node|short}\"')

        with cd(self.base_path):
            # TODO: del creating empty folder
#            if not os.path.exists(os.path.join(self.src_path, 'rhel')):
#                run('mkdir {}'.format(os.path.join(self.src_path, 'rhel')))

#            run('mv {} .'.format(os.path.join(self.src_path, 'rhel')))
            self.run_deps.append('python-virtualenv')
            deps_str = '-d ' + ' -d '.join(self.run_deps)
            for file_path in [before_remove, after_remove, before_install, after_install]:
                if file_path and os.path.exists(file_path):
                    put(file_path, os.path.join(self.base_path, 'rhel/'))

            main_dir = os.path.join(self.prefix, self.app_name)
            app_dir = os.path.join(main_dir, 'app')
            venv_dir = os.path.join(main_dir, 'venv')
            static_dir = os.path.join(main_dir, 'static')

            hooks_str = ' '.join(
                '{} {}'.format(opt, os.path.join('rhel', os.path.basename(file_path)))
                    for opt, file_path in [
                    ('--before-remove', before_remove),
                    ('--after-remove', after_remove),
                    ('--before-install', before_install),
                    ('--after-install', after_install),
                ]
                    if file_path and os.path.exists(file_path)
            )

            app_deps_str = deps_str + ' -d "{0.pkg_name}-static >= {0.version}" -d "{0.pkg_name}-venv >= {0.version}"'.format(
                self)
            venv_deps_str = deps_str

            if split_pkg:
                pack_app = self.do_pack(app_dir, hooks_str=hooks_str, deps_str=app_deps_str)
                static_app = self.do_pack(static_dir, suffix='static')
                venv_app = self.do_pack(venv_dir, suffix='venv', deps_str=venv_deps_str)

                # Get filename form run result string:
                # ``Created rpm package {"path":"prefix-app_name-1.0.0-1.noarch.rpm"}``
                # and download it to the local machine
                get(pack_app.split('"')[-2], 'packages/rhel/%(basename)s')
                get(static_app.split('"')[-2], 'packages/rhel/%(basename)s')
                get(venv_app.split('"')[-2], 'packages/rhel/%(basename)s')
            else:
                pack_all = self.do_pack(main_dir, hooks_str=hooks_str, deps_str=deps_str)
                get(pack_all.split('"')[-2], 'packages/rhel/%(basename)s')

    def do_pack(self, dir_to_pack, without_dirs=None, suffix=None, hooks_str='', deps_str=''):
        exclude_string = '-x "*.bak" -x "*.orig"'
        if without_dirs:
            exclude_string += ' -x ' + ' -x '.join(without_dirs)
        pkg_name = self.pkg_name + '-' + suffix if suffix else self.pkg_name
        run_fpm = run(
            'fpm -s dir -t rpm -n {1} -v {0.version} --iteration {0.release} '
            '-a native {2} {3} '
            '--description "Build by Alexis ({6}).\n'
            'Branch: {0.hg_branch} Commit: {0.hg_commit}" '
            '{4} {5}'
            .format(self, pkg_name, exclude_string, hooks_str, deps_str, dir_to_pack, __version__)
        )
        return run_fpm

    def hg_clone(self):
        run('hg clone {0.hg_repository} -r {0.hg_branch} {0.src_path}'.format(self))

    def create_virtualenv(self, python_path):
#        with cd('~'):
#            run('rm -f virtualenv.py*')
#        put('{}'.format(os.path.join(os.path.dirname(__file__), 'libs/virtualenv.py')), '~/')
        with cd(self.app_path):
            run('rm -rf venv')
            run('virtualenv venv --python={}'.format(python_path))
#            run('{} ~/virtualenv.py venv'.format(python_path))
