#!/usr/bin/env python
# -*- coding: utf-8 -*-

from optparse import OptionParser
import glob
import importlib
import itertools
import logging
import os
import sys

import fanstatic

def main():
  logging.getLogger().setLevel(logging.INFO)
  parser = OptionParser()
  parser.add_option("--dry-run", action="store_true", dest="dry_run", help="dry run")
  parser.add_option("--versioning", action="store_true", dest="versioning", help="""\
If ``True``, Fanstatic will automatically include
a version identifier in all URLs pointing to resources.
Since the version identifier will change when you update a resource,
the URLs can both be infinitely cached and the resources will always
be up to date. See also the ``recompute_hashes`` parameter.""")
  parser.add_option("--versioning_use_md5", action="store_true", dest="versioning_use_md5", help="""\
If ``True``, Fanstatic will use and md5
algorithm instead of an algorithm based on the last modification time of
the Resource files to compute versions. Use md5 if you don't trust your
filesystem.""")
  parser.add_option("--base_url", dest="base_url", metavar="URL", help="""\
This URL will be prefixed in front of all resource
URLs. This can be useful if your web framework wants the resources
to be published on a sub-URL. By default, there is no ``base_url``,
and resources are served in the script root. Note that this can
also be set with the set_base_url method on a ``NeededResources``
instance.""")
  parser.add_option("--publisher_signature", dest="publisher_signature", default=fanstatic.DEFAULT_SIGNATURE, metavar="PATH", help="""\
The name under which resource libraries
should be served in the URL. By default this is ``fanstatic``, so
URLs to resources will start with ``/fanstatic/``.""")
  (options, _args) = parser.parse_args()
  fanstatic_options = dict(options.__dict__)
  fanstatic_options.pop("dry_run")
  needed = fanstatic.NeededResources(**fanstatic_options)
  fanstatic_package_names = set(os.path.basename(module_path).split("-", 1)[0]
                                for module_path in itertools.chain.from_iterable(glob.iglob("%s/js[\.]*" % path) for path in sys.path))
  for fanstatic_package_name in fanstatic_package_names:
    try:
      library = importlib.import_module(fanstatic_package_name).library
    except ImportError, e:
      logging.error("%s: %s" % (e.__class__.__name__, e))
      continue
    else:
      library_url = needed.library_url(library.known_resources.values()[0].library)
      source_file = os.path.join("../../..", library.path)
      target_file = library_url.lstrip("/")
      logging.info("make symlink %s to %s" % (target_file, source_file))
      if options.dry_run:
        continue
      base_directory = os.path.dirname(target_file)
      if not os.path.exists(base_directory):
        os.mkdir(base_directory)
      if not os.path.exists(target_file):
        os.symlink(source_file, target_file)

if __name__== "__main__":
  main()
