# Copyright (C) 2009 Abdelhalim Ragab <abdelhalim@gmail.com>
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; version 3
# of the License or (at your option) any later version of 
# the License.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


'''

@author: abdelhalim
'''

import boto

from git_config import GitConfig

import re
import os


class S3Transport(object):
    URL_PATTERN = re.compile(
                             r'(?P<protocol>[^:]+)://'
                             r'(?P<config>[^@]+)@'
                             r'(?P<bucket>[^/]+)/'
                             r'(?P<prefix>.*)'
                             )

    def __init__(self, url):
        self.url = url
        o = self.URL_PATTERN.match(self.url)
        if o:
            bucket_name = o.group('bucket')
            self.prefix = o.group('prefix')
            if self.prefix.endswith('/'):
                self.prefix = self.prefix[:-1]

            self.s3Conn = boto.connect_s3()
            self.bucket = self.s3Conn.get_bucket(bucket_name, False)

    def open_properties(self, properties_file):
        propFile = file(properties_file, "rU")
        propDict = dict()
        for propLine in propFile:
            propDef = propLine.strip()
            if len(propDef) == 0:
                continue
            if propDef[0] in ('!', '#'):
                continue
            punctuation = [propDef.find(c) for c in ':= '] + [len(propDef)]
            found = min([pos for pos in punctuation if pos != -1])
            name = propDef[:found].rstrip()
            value = propDef[found:].lstrip(":= ").rstrip()
            propDict[name] = value
        propFile.close()
        return propDict

    def upload_pack(self, file_name):
        pack_full_path = self.prefix + '/objects/pack/'
        self.upload_file(pack_full_path, file_name)

    def upload_file(self, prefix, file_name):
        new_key = self.bucket.new_key(prefix + file_name)
        new_key.set_contents_from_file(open(file_name))
        new_key.set_acl('public-read')
        pass

    def upload_string(self, path, contents):
        key_path = self.prefix + '/' + path
        key = self.bucket.get_key(key_path)
        if not key:
            key = self.bucket.new_key(key_path)
        key.set_contents_from_string(contents)
        key.set_acl('public-read')

    def get_pack_names(self):

        if self.bucket:

            path = self.prefix + '/objects/pack'
            keys = self.bucket.list(path)

            packs = []

            for key in keys:

                if key.name.endswith('.pack'):
                    if key.name.startswith(path):
                        packs.append(key.name[len(path)+1:len(key.name)])

            return packs

    def get_advertised_refs(self):
        refs = {}

        if self.bucket:
            # get loose refs
            path = self.prefix + '/refs'
            keys = self.bucket.list(path)

            for key in keys:
                name = key.name[len(self.prefix + '/'):]
                s = key.get_contents_as_string()
                ref = self.get_ref(s, refs)
                refs[name] = {name: ref}

            # read HEAD
            path = self.prefix + '/HEAD'
            key = self.bucket.get_key(path)
            if key:
                s = key.get_contents_as_string()
                ref = self.get_ref(s, refs)
                refs['HEAD'] = {'HEAD': ref}

        return refs

    def get_ref(self, s, refs):
        if s.startswith('ref: '):
            target = s[len('ref: '):]
            target = target.strip()
            try:
                target_ref = refs[target]
            except KeyError:
                target_ref = None

            if target_ref:
                return target_ref[target]

        return s

    def create_new_repo(self, refs):
        if self.bucket:

            # .git/config file
            config_str = '[core]\n' + '\trepositoryformatversion = 0\n'
            key = self.bucket.new_key(self.prefix + '/config')
            key.set_contents_from_string(config_str)
            key.set_acl('public-read')

            # .git/HEAD
            if refs.startswith('refs/heads'):
                head_str = 'ref: ' + refs + '\n'
            else:
                head_str = 'refs: refs/heads/' + refs + '\n'

            key = self.bucket.new_key(self.prefix + '/HEAD')
            key.set_contents_from_string(head_str)
            key.set_acl('public-read')
