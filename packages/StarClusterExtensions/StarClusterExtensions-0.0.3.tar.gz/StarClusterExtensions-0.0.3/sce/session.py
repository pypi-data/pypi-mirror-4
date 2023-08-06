from starcluster.static import STARCLUSTER_CFG_FILE
from starcluster.config import StarClusterConfig
from starcluster import logger
import os

logger.configure_sc_logging()
log = logger.log

starclusterConfig = StarClusterConfig(STARCLUSTER_CFG_FILE)
starclusterConfig.load()
clusterManager = starclusterConfig.get_cluster_manager()

settings = {
    'library_path': os.path.dirname(os.path.realpath(__file__))
}