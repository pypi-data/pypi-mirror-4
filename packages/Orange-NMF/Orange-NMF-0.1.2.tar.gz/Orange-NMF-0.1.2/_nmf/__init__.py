
import pkg_resources

def datasets():
    yield ('nmf', pkg_resources.resource_filename(__name__, 'datasets'))