"""
Does stuff I always do at setup.

author: Erik Gafni
"""
from starcluster.logger import log
import os
from sce import PluginSetup
from sce import utils
from sce import session

opj = os.path.join


class Setup(PluginSetup):

    def __init__(self):
        self.data_path = opj(session.settings['library_path'],'erik/data')

    def __postconfig__(self):
        self.cluster_name = self.master.parent_cluster.name[4:]
        self.etc_hosts_line = "{0}\t{1}".format(self.master.ip_address,self.cluster_name)

    def run2(self):
        log.info('Running Erik')
        master = self.master
        utils.apt_update(master)

        #used by Erik for cosmos
        log.info("Installing cosmos libraries.")
        master.apt_install('python-dev libmysqlclient-dev mysql-server graphviz graphviz-dev')
        master.ssh.execute('mkdir -p /home/erik/projects')
        master.ssh.execute('chown erik:erik /home/erik/projects')

        #bash color prompt
        master.ssh.execute('sed -i "1icolor_prompt=yes" /home/erik/.bashrc')

        #add master to local /etc/hosts under the name of the cluster
        utils.add2file('/etc/hosts',self.etc_hosts_line,sudo=True, del_if_exists=True)
        #node.ssh.execute('chown -R erik:erik /gluster')

        for node in self.nodes:
            self.on_add_node2(node)

    def on_add_node2(self, node):
        utils.apt_update(node)
        self._passwdless_sudo(node)
        self._add_to_sudo(node,'erik')
        self._remove_mysql(node)

        node.add_tag('Name','erik__{0.alias}'.format(node))

    def on_shutdown2(self):
        utils.sed_delete('/etc/hosts',regex=self.etc_hosts_line,sudo=True)

    def _passwdless_sudo(self,node):
        node.ssh.put(opj(self.data_path,'sudoers'),'/etc/sudoers')
        node.ssh.execute('chmod 0440 /etc/sudoers')

    def _add_to_sudo(self,node,username):
        node.ssh.execute('usermod -G sudo {0}'.format(username))


    def _install_ssh_hpn(self,node):
        config = ["HPNDisabled no",
                  "TcpRcvBufPoll yes",
                  "HPNBufferSize 8192",
                  "NoneEnabled yes"]

        log.info('Install openssh hpn')
        node.ssh.execute('add-apt-repository ppa:w-rouesnel/openssh-hpn -y')
        utils.apt_update(node)
        node.apt_install('openssh-server')

        for line in config:
            utils.add2file('/etc/ssh/sshd_config',line=line,node=node,del_if_exists=True)

        node.ssh.execute('service ssh restart')

    def _remove_mysql(self,node):
        node.ssh.execute("sudo apt-get remove mysql* -y")
        node.ssh.execute('rm -rf /etc/mysql')
