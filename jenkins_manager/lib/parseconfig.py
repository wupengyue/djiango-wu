import yaml
import logging

log = logging.getLogger(__name__)


def yaml_loader(file_path):
    config = dict()
    with open(file_path, 'r') as stream:
        try:
            config = yaml.load(stream)
            log.debug("get config :" + str(config))
        except yaml.YAMLError as exc:
            print(exc)
            log.error(exc)

    return config
