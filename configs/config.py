# config.py

from configs.system_config import SystemConfig
from configs.project_config import ProjectConfig

# a wrapper class or module-level attributes
class Config(object):
    System = SystemConfig
    Project = ProjectConfig
