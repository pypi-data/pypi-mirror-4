"""
Configures SGE to work with h_vmem and other complex values.

This means you can submit jobs, specify how much memory you require, and Grid Engine will
be able to schedule properly.

To schedule jobs, use -l like this: qsub -l h_vmem=10G,num_proc=3

..note:: You currently must run qconf -mc and set h_vmem and num_proc to consumable for this to work.

Example config:
[plugin sge_plus]
setup_class = sge_plus.Setup

author: Erik Gafni
"""
from sce import PluginSetup,utils
from starcluster.logger import log
import os
opj = os.path.join

class Setup(PluginSetup):

    def __init__(self, data_path='/home/erik/projects/SCE/sce/sge_plus/data',master_slots=1):
        self.data_path = data_path
        self.master_slots = master_slots

    def run2(self):
        log.info('Running SGE Plus')
        master = self.master

        #update qconf complex list to make h_vmem and num_proc consumable
        master.ssh.put(opj(self.data_path,'qconf_c'),'/tmp/qconf_c')
        master.ssh.execute('qconf -Mc /tmp/qconf_c')

        for node in self.nodes:
            self.on_add_node2(node)

    def update_complex_list(self,node):
        """
        Sets a node's h_vmem and num_proc complex values

        :param node: The node to update
        """
        log.info('Updating complex values for {0}'.format(node))
        h_vmem = node.ssh.execute('free -g|grep Mem:|grep -oE "[0-9]+"|head -1')[0]
        num_proc = self.master_slots if node.is_master() else node.ssh.execute('nproc')[0]
        node.ssh.execute(
            "qconf -rattr exechost complex_values slots={num_proc},num_proc={num_proc},h_vmem={h_vmem}g {node}".format(
                h_vmem=h_vmem,num_proc=num_proc,node=node.alias)
        )

    def on_add_node2(self,node):
        self.update_complex_list(node)
