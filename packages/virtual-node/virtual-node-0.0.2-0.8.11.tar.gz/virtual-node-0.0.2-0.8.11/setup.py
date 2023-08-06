#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("virtual-node")

try:
    import setuptools
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()

from setuptools import setup
from setuptools.command.bdist_egg import bdist_egg as _bdist_egg

# prevent a SandboxViolation error when using the 'bdist_egg' command
# this hack to prevent the violation has be borrowed from the distribute
# package's distribute_setup.py
# https://bitbucket.org/tarek/distribute/src/fa1cb0b8f46af5debe0d44890e497b1c698b3c74/distribute_setup.py#cl-227
from setuptools.sandbox import DirectorySandbox
def violation(*args):
    pass
DirectorySandbox._old = DirectorySandbox._violation
DirectorySandbox._violation = violation

from distutils.command.build import build as _build


class node_bdist_egg(_bdist_egg):

    def run(self):
        self.run_command("build")
        _bdist_egg.run(self)


class node_build(_build):
    env_dir = os.environ.get('VIRTUAL_ENV')
    default_version = '0.8.11'
    verbose = False

    def run(self):
        if not self.env_dir:
            raise KeyError("no virtualenv specified in 'VIRTUAL_ENV' required "
                           "to proceed with install")
        versions = self.distribution.get_version().rsplit('-', 1)
        if len(versions) == 2:
            self.version = versions[1]
        else:
            self.version = self.default_version

        # Only install node if the version we need isn't already installed.
        if self.check_for_node():
            logger.info('Skipping NodeJS installation, v{0} is already installed.'.format(self.version))
        else:
            self.install_node(self.env_dir)
        self.run_npm(self.env_dir)
        self.run_bower(self.env_dir)

    def check_for_node(self):
        """
            Check that the required version of Node is installed in the virtual
            env. If it is, there's no need to re-install.
        """
        node_path = os.path.join(self.env_dir, 'bin', 'node')
        if os.path.exists(node_path):
            version = self.run_cmd([node_path, '--version'])[1][0]
            if 'v{0}'.format(self.version) == version:
                return True
        return False

    def get_node_src_url(self, version, postfix=''):
        node_name = 'node-v%s%s' % (version, postfix)
        tar_name = '%s.tar.gz' % (node_name)
        if version > "0.5.0":
            node_url = 'http://nodejs.org/dist/v%s/%s' % (version, tar_name)
        else:
            node_url = 'http://nodejs.org/dist/%s' % (tar_name)
        return node_url

    def run_cmd(self, cmd, cwd=None, extra_env=None):
        """
        Execute cmd line in sub-shell
        """
        all_output = []
        cmd_parts = []

        for part in cmd:
            if len(part) > 45:
                part = part[:20] + "..." + part[-20:]
            if ' ' in part or '\n' in part or '"' in part or "'" in part:
                part = '"%s"' % part.replace('"', '\\"')
            cmd_parts.append(part)
        cmd_desc = ' '.join(cmd_parts)
        logger.debug(" ** Running command %s" % cmd_desc)

        # output
        stdout = subprocess.PIPE

        # env
        if extra_env:
            env = os.environ.copy()
            if extra_env:
                env.update(extra_env)
        else:
            env = None

        # execute
        try:
            proc = subprocess.Popen(
                [' '.join(cmd)], stderr=subprocess.STDOUT, stdin=None, stdout=stdout,
                cwd=cwd, env=env, shell=True)
        except Exception:
            e = sys.exc_info()[1]
            logger.error("Error %s while executing command %s" % (e, cmd_desc))
            raise

        stdout = proc.stdout
        while stdout:
            line = stdout.readline()
            if not line:
                break
            line = line.rstrip()
            all_output.append(line)
            logger.info(line)
        proc.wait()

        # error handler
        if proc.returncode:
            for s in all_output:
                logger.critical(s)
            raise OSError("Command %s failed with error code %s"
                % (cmd_desc, proc.returncode))

        return proc.returncode, all_output

    def run_npm(self, env_dir):
        if os.path.exists("%s%s" % (env_dir, "package.json")):
            self.run_cmd(['npm', 'install'], env_dir)
        else:
            logger.warning("Could not find 'package.json', ignoring NPM dependencies.")

    def run_bower(self, env_dir):
        bower_bin = "%s/bin/bower" % env_dir
        if not os.path.exists(bower_bin):
            logger.warning("Could not find 'bower' executable, ignoring it")
            return

        if os.path.exists("%s%s" % (env_dir, "components.json")):
            self.run_cmd(['bower', 'install'], env_dir)
        else:
            logger.warning("Could not find 'components.json', ignoring bower dependencies.")

    def install_node(self, env_dir, version=None):
        """
        Download source code for node.js, unpack it
        and install it in virtual environment.
        """
        logger.info(
            ' * Install node.js (%s' % self.version,
            extra={'continued': True}
        )

        node_name = 'node-v%s' % (self.version)
        node_url = self.get_node_src_url(self.version)

        src_dir = os.path.join(env_dir, 'src')
        node_src_dir = os.path.join(src_dir, node_name)
        env_dir = os.path.abspath(env_dir)

        if not os.path.exists(node_src_dir):
            os.makedirs(node_src_dir)

        cmd = [
            'curl', '--silent', '-L', node_url, '|',
            'tar', 'xzf', '-', '-C', src_dir,
        ]
        try:
            self.run_cmd(cmd, env_dir)
            logger.info(') ', extra=dict(continued=True))
        except OSError:
            postfix = '-RC1'
            logger.info('%s) ' % postfix, extra=dict(continued=True))
            new_node_url = self.get_node_src_url(self.version, postfix)
            cmd[cmd.index(node_url)] = new_node_url
            self.run_cmd(cmd, env_dir)

        logger.info('.', extra=dict(continued=True))

        conf_cmd = [
            './configure',
            '--prefix=%s' % (env_dir),
        ]

        self.run_cmd(conf_cmd, node_src_dir)
        logger.info('.', extra=dict(continued=True))
        self.run_cmd(['make'], node_src_dir)
        logger.info('.', extra=dict(continued=True))
        self.run_cmd(['make install'], node_src_dir)
        logger.info('.', extra=dict(continued=True))
        self.run_cmd(['rm -rf "%s"' % node_src_dir])

        logger.info(' done.')


setup(
    name='virtual-node',
    version='0.0.2-0.8.11',
    description='Install node.js into your virtualenv',
    author='Sebastian Vetter',
    author_email='sebastian@roadside-developer.com',
    url='http://github.com/elbaschid/virtual-node',
    long_description="%s\n\n%s" % (open('README.rst').read(),
                                   open('CHANGELOG.rst').read()),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Programming Language :: JavaScript',
        'Topic :: Software Development :: Libraries',
    ],
    license='BSD',
    zip_safe=False,
    cmdclass={
        'build': node_build,
        'bdist_egg': node_bdist_egg,
    }
)
