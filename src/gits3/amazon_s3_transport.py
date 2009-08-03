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

from boto.s3.connection import S3Connection
from boto.s3.key import Key

from git_config import GitConfig

import re

class S3Transport(object):
    
    URL_PATTERN = re.compile(
                             r'(?P<protocol>[^:]+)://'
                             r'(?P<config>[^@]+)@'
                             r'(?P<bucket>[^/]+)/'
                             r'(?P<prefix>.*)'
                             )
    
    def __init__(self, url):
        self.s3Conn = S3Connection('AKIAITETCENIS3TKNVXQ','/taQuiG5b9AVDKbPA6AJo/w0F2Z3Oe/JAN+V1TJP')
        self.url = url
        o = self.URL_PATTERN.match(self.url)
        if o:
            bucket_name = o.group('bucket')
            self.prefix = o.group('prefix')
            self.bucket = self.s3Conn.get_bucket(bucket_name, False)
            print self.bucket
    
    
    def upload_pack(self, file_name):
        pack_full_path = self.prefix + '/objects/pack/'
        self.upload_file(pack_full_path, file_name)
          
    def upload_file(self, prefix, file_name):
        new_key = self.bucket.new_key(prefix + file_name)
        new_key.set_contents_from_file(open(file_name))
        pass
            
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