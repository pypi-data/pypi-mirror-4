import os
from mako.lookup import TemplateLookup


def get_mako_lookup(code_path, output_path):
    cache_dir = os.path.join(
        output_path,
        '.cache',
    )
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)

    lookup = TemplateLookup(
        directories=[code_path],
        module_directory=cache_dir,
    )
    return lookup
