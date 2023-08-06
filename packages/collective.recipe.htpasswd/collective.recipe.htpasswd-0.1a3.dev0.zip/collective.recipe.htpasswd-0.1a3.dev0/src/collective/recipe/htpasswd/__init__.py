# -*- coding: utf-8 -*-
""" collective.recipe.htpasswd
"""

import crypt
import logging
import os
import random
import string

from base64 import b64encode
from hashlib import sha1

import zc.buildout

try:
    import aprmd5
except ImportError:
    HAVE_APRMD5 = False
else:
    HAVE_APRMD5 = True


class Recipe(object):
    """ This recipe should not be used to update an existing htpasswd file
        because it overwritte the htpasswd file in every update.
    """

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        self.logger = logging.getLogger(self.name)

        supported_algorithms = ('crypt', 'plain', 'md5', 'sha1')
        if 'algorithm' in options:
            if options['algorithm'].lower() not in supported_algorithms:
                raise zc.buildout.UserError("Unknow algorithm. see "
                                            "documentation for a list of "
                                            "supported algorithms.")
            elif options['algorithm'].lower() == 'md5' and not HAVE_APRMD5:
                raise zc.buildout.UserError('You need the python-aprmd5 module '
                                            'installed in order to use the MD5 '
                                            'algorithm')
            else:
                self.algorithm = options['algorithm'].lower()
        else:
            self.algorithm = 'crypt'

        if 'output' not in options:
            raise zc.buildout.UserError('No output file specified.')
        elif os.path.isdir(options['output']):
            raise zc.buildout.UserError('The output file specified is an '
                                        'existing directory.')
        elif os.path.isfile(options['output']):
            self.logger.warning('The output file specified exist and is going '
                                'to be overwritten.')

        self.output = options['output']

        if 'credentials' not in options:
            raise zc.buildout.UserError('You must specified at lest one pair '
                                        'of credentials.')
        else:
            self.credentials = []
            for credentials in options['credentials'].split('\n'):
                if not credentials:
                    continue
                try:
                    (username, password) = credentials.split(':', 1)
                except ValueError:
                    raise zc.buildout.UserError('Every pair credentials must '
                                                'be separated be a colon.')
                else:
                    self.credentials.append((username, password))

            if not self.credentials:
                raise zc.buildout.UserError('You must specified at lest one '
                                            'pair of credentials.')

        if 'mode' in options:
            self.mode = int(options['mode'], 8)
        else:
            self.mode = None

    def install(self):
        """ Create the htpasswd file.
        """
        self.mkdir(os.path.dirname(self.output))
        with open(self.output, 'w+') as pwfile:
            for (username, password) in self.credentials:
                pwfile.write("%s:%s\n" % (username, self.mkhash(password)))

        if self.mode is not None:
            os.chmod(self.output, self.mode)

        self.options.created(self.output)
        return self.options.created()

    def update(self):
        """ Every time that the update method is called the htpasswd file is
            overrided.
        """
        return self.install()

    def mkdir(self, path):
        """ Create the path of directories recursively.
        """
        parent = os.path.dirname(path)
        if not os.path.exists(path) and parent != path:
            self.mkdir(parent)
            os.mkdir(path)
            self.options.created(path)

    def salt(self):
        """ Returns a two-character string chosen from the set [a–zA–Z0–9./].
        """
        characters = string.ascii_letters + string.digits + './'
        if self.algorithm == 'crypt':
            slen = 2
        elif self.algorithm == 'md5':
            slen = 8
        elif self.algorithm in ('pain', 'sha1'):
            raise RuntimeError("The '%s' algorithm don't must be call to the "
                               "salt method" % self.algorithm)
        else:
            raise RuntimeError("Unknow algorithm '%s' in the salt method" %
                               self.algorithm)

        sres = ''
        while len(sres) < slen:
                sres += random.choice(characters)

        return sres

    def mkhash(self, password):
        """ Returns a the hashed password as a string.
        """
        if self.algorithm == 'crypt':
            if len(password) > 8:
                self.logger.warning((
                    'Only the first 8 characters of the password are '
                    'used to form the password. The extra characters '
                    'will be discarded.'))
            return crypt.crypt(password, self.salt())
        elif self.algorithm == 'md5':
            return aprmd5.md5_encode(password, self.salt())
        elif self.algorithm == 'plain':
            return password
        elif self.algorithm == 'sha1':
            return b64encode(sha1(password).digest())
        else:
            raise ValueError(
                "The algorithm '%s' is not supported." % self.algorithm)
