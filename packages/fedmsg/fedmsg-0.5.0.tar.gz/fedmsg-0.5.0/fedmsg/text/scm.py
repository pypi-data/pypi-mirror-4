# This file is part of fedmsg.
# Copyright (C) 2012 Red Hat, Inc.
#
# fedmsg is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# fedmsg is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with fedmsg; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#
# Authors:  Ralph Bean <rbean@redhat.com>
#
from fedmsg.text.base import BaseProcessor


class SCMProcessor(BaseProcessor):
    def handle_subtitle(self, msg, **config):
        return '.git.receive.' in msg['topic']

    def subtitle(self, msg, **config):
        if '.git.receive.' in msg['topic']:
            repo = '.'.join(msg['topic'].split('.')[5:-1])
            user = msg['msg']['commit']['name']
            summ = msg['msg']['commit']['summary']
            branch = msg['msg']['commit']['branch']
            tmpl = self._('{user} pushed to {repo} ({branch}).  "{summary}"')
            return tmpl.format(user=user, repo=repo,
                               branch=branch, summary=summ)
        else:
            raise NotImplementedError

    def handle_link(self, msg, **config):
        return '.git.receive.' in msg['topic']

    def link(self, msg, **config):
        if '.git.receive.' in msg['topic']:
            repo = '.'.join(msg['topic'].split('.')[5:-1])
            rev = msg['msg']['commit']['rev']
            branch = msg['msg']['commit']['branch']
            prefix = "http://pkgs.fedoraproject.org/cgit"
            tmpl = "{prefix}/{repo}.git/commit/?h={branch}&id={rev}"
            return tmpl.format(prefix=prefix, repo=repo,
                               branch=branch, rev=rev)
        else:
            raise NotImplementedError
