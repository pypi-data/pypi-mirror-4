import os
from fabric.api import env, local, lcd

class VersionControlCommon(object):
    def __init__(self, dest_dir, repos_path):
        self.dest_dir = dest_dir
        self.repos_path = repos_path

    @property
    def stick_filename(self):
        dst_up, dst_name = os.path.split(env.local_project_root + self.dest_dir)
        return dst_up + "/."+ dst_name +'.version'

    def checkout(self):
        local('{cmd} checkout {repos_path} {to}'.format(
            cmd=self.cmd,
            repos_path=self.repos_path,
            to=self.dest_dir))

    def get_sticky_version(self):
        if os.path.exists(self.stick_filename):
            version = open(self.stick_filename).read()
        else:
            version = self.tip_version

        return version

    def update(self,  to_tip):
        if to_tip and os.path.exists(self.stick_filename):
            os.unlink(self.stick_filename)
        to_version = self.get_sticky_version()

        with lcd(self.dest_dir):
            local('{cmd} update -r {to_version}'.format(
                cmd=self.cmd,
                to_version=to_version))

    def checkout_and_update(self, to_tip):
        if not os.path.exists(env.local_project_root + self.dest_dir):
            self.checkout()
        self.update(to_tip)


class Mercurial(VersionControlCommon):
    cmd = 'hg'
    tip_version = 'tip'

    def update(self, to_tip):
        with lcd(self.dest_dir):
            local('{cmd} pull'.format(cmd=self.cmd))
        VersionControlCommon.update(self, to_tip)

    def checkout(self):
        local('{cmd} clone {repos_path} {to}'.format(
            cmd=self.cmd,
            repos_path=self.repos_path,
            to=self.dest_dir))

    def stick_current_version(self):
        with lcd(self.dest_dir):
            open(self.stick_filename, "w").write(
                local(
                    'hg tip|grep changeset',
                    capture=True
                    ).strip().split(':')[-1])


class Subversion(VersionControlCommon):
    cmd = 'svn'
    tip_version = 'HEAD'

    def stick_current_version(self):
        with lcd(self.dest_dir):
            open(self.stick_filename, "w").write(
                local(
                    'svn info|grep Revision:',
                    capture=True
                    ).split(':')[-1].strip())
