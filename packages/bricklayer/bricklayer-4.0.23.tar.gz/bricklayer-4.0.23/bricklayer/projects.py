import shutil
import redis
from model_base import ModelBase, transaction
from groups import Groups
from git import Git

class Projects(ModelBase):
    
    namespace = 'project'

    def __init__(self, name='', git_url='', install_cmd='', build_cmd='', version='', release='', group_name='', experimental=1):
        self.name = name
        self.git_url = git_url
        self.install_cmd = install_cmd
        self.build_cmd = build_cmd
        self.group_name = group_name
        if version:
            self.version(version=version)
        self.release = release
        self.experimental = experimental
        self.email = 'bricklayer@locaweb.com.br'
        self.username = 'Bricklayer Builder'
        self.install_prefix = ''
        self.populate(self.name)

    def __dir__(self):
        return ['name', 'git_url', 'install_cmd', 'build_cmd', 'email', 'username', 'release', 'group_name', 'experimental']
   
    @transaction
    def start_building(self):
        self.redis_cli.incr('build_lock:%s' % self.name)

    @transaction
    def is_building(self):
        build_lock = self.redis_cli.get('build_lock:%s' % self.name)
        if build_lock and int(build_lock) > 0:
            return True
        return False

    @transaction
    def stop_building(self):
        self.redis_cli.decr('build_lock:%s' % self.name)

    @transaction
    def add_branch(self, branch):
        self.redis_cli.rpush('branches:%s' % self.name, branch)
     
    @transaction
    def remove_branch(self, branch):
        index = self.redis_cli.lindex('branches:%s' % self.name, branch)
        self.redis_cli.lrem('branches:%s' % self.name, index)
    
    @transaction
    def repository(self):
        group = Groups(self.group_name)
        res = []
        for attr in ('repo_addr', 'repo_user', 'repo_passwd'):
            res.append(getattr(group, attr))
        return res

    @transaction
    def branches(self):
        res = self.redis_cli.lrange('branches:%s' % self.name, 0, self.redis_cli.llen('branches:%s' % self.name) - 1)
        if len(res) == 0:
            res.append('master')
        return res

    @transaction
    def last_commit(self, branch='master', commit=''):
        if commit == '':
            res = self.redis_cli.get('branches:%s:%s:last_commit' % (self.name, branch))
        else:
            res = self.redis_cli.set('branches:%s:%s:last_commit' % (self.name, branch), commit)
        return res

    @transaction
    def last_tag(self, tag_type='', tag=''):
        if tag:
            res = self.redis_cli.set('tags:%s:%s:last_tag' % (self.name, tag_type), tag)
        else:
            res = self.redis_cli.get('tags:%s:%s:last_tag' % (self.name, tag_type))
        return res

    @transaction
    def version(self, branch='master', version=''):
        if version == '':
            res = self.redis_cli.get('branch:%s:%s:version' % (self.name, branch))
        else:
            res = self.redis_cli.set('branch:%s:%s:version' % (self.name, branch), version)
        return res

    @classmethod
    def get_all(self):
        connection_obj = Projects()
        redis_cli = connection_obj.connect()
        keys = redis_cli.keys('%s:*' % self.namespace)
        projects = []
        for key in keys:
            key = key.replace('%s:' % self.namespace, '')
            projects.append(Projects(key)) 
        return projects
    
    def clear_branches(self):
        git = Git(self)
        for b in self.branches():
            try:
                shutil.rmtree("%s-%s" % (git.workdir, b))
            except Exception, e:
                pass # ignore if files does not exist
