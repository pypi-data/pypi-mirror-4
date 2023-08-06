"""
SCE command line interface
"""
import argparse, os
from importlib import import_module
import re
from sce.session import clusterManager,starclusterConfig
from sce.session import log

def runplugin(cluster_name,plugin_name,node=None):
    """
    Runs a plugin
    """
    cluster = clusterManager.get_cluster(cluster_name)
    m = re.search('(.+)\.(.+)',starclusterConfig.plugins[plugin_name]['setup_class'])
    setup_mod = m.group(1)
    setup_class = m.group(2)
    plugin_setup = import_module(setup_mod)
    kwargs = starclusterConfig.plugins[plugin_name].copy()
    del kwargs['__name__']
    del kwargs ['setup_class']
    plugin = getattr(plugin_setup,setup_class)(**kwargs)

    if node:
        node_instance = filter(lambda n: n.alias == node,cluster.nodes)[0]
        plugin.on_add_node(node=node_instance,nodes=cluster.nodes, master=cluster.master_node, user='root', user_shell='bash', volumes=cluster.volumes)
    else:
        plugin.run(nodes=cluster.nodes, master=cluster.master_node, user='root', user_shell='bash', volumes=cluster.volumes)

def main():

    parser = argparse.ArgumentParser(description='SCE CLI')
    subparsers = parser.add_subparsers(title="Commands", metavar="<command>")

    rp_sp = subparsers.add_parser('runplugin',help=runplugin.__doc__)
    rp_sp.set_defaults(func=runplugin)
    rp_sp.add_argument('plugin_name',type=str,help='Plugin Name')
    rp_sp.add_argument('cluster_name',type=str,help='Cluster Name')
    rp_sp.add_argument('-n','--node',type=str,help='Run add_on_node(node) only')

    a = parser.parse_args()
    kwargs = dict(a._get_kwargs())
    del kwargs['func']
    a.func(**kwargs)

if __name__ == '__main__':
    main()

