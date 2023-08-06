__author__ = 'erik'
from sce import PluginSetup,utils
from datetime import datetime
import os
from starcluster.logger import log

opj = os.path.join
timenow = lambda: datetime.now().strftime('%a %b %d %H:%M:%S %Y')

class Setup(PluginSetup):
    def __init__(self,output_dir):
        self.output_dir = output_dir

    def __postconfig__(self):
        self.cluster_outdir = opj(self.output_dir,utils.cluster_name(self.master))
        self.outfile_path = opj(self.cluster_outdir,'stats.csv')
        os.system('mkdir -p {0}'.format(self.cluster_outdir))

    def run2(self):
        log.info("Writing billing stats to {0}".format(self.outfile_path))
        for n in self.nodes:
            self.on_add_node2(n)

    def on_add_node2(self, node):
        self.write([timenow(),node.alias,node.instance_type,str(node.instance),'add_node'])

    def on_remove_node2(self, node):
        self.write([timenow(),node.alias,node.instance_type,str(node.instance),'rm_node'])

    def on_shutdown2(self):
        for n in self.nodes:
            self.on_remove_node2(n)

    def write(self,columns):
        with open(self.outfile_path,'a') as outf:
            print >> outf, "\t".join(columns)