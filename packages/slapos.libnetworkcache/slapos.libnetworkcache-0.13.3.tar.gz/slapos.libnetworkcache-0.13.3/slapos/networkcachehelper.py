##############################################################################
#
# Copyright (c) 2012 ViFiB SARL and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import json
import logging
import os
import shutil
import tarfile
import urllib2
from slapos.libnetworkcache import NetworkcacheClient, UploadError, \
    DirectoryNotFound

logging.basicConfig()
logger = logging.getLogger('networkcachehelper')
logger.setLevel(logging.INFO)

def _split_last_directory(path):
  """
  If basename(path) is a file (i.e /path/to/directory), do a simple split.
  If basename(path) is a directory (i.e /path/to/directory/), split again to
  have pair like ('/path/to', 'directory').
  """
  path_dirname, path_basename = os.path.split(path)
  if not path_basename:
    # We were given a path like "/path/to/directory/": Split again.
    path_dirname, path_basename = os.path.split(path_dirname)
  return path_dirname, path_basename

def helper_upload_network_cached(dir_url, cache_url,
    file_descriptor, directory_key,
    signature_private_key_file, shacache_cert_file, shacache_key_file,
    shadir_cert_file, shadir_key_file, metadata_dict={}):
  """
  Upload content of a file descriptor to a network cache server using
  shacache/shadir API.
  It will upload file_descriptor content to server using directory_key as
  shacache key, and metadata_dict as shadir metadata if specified.

  Return True if successfull, False otherwise.
  """
  if not (dir_url and cache_url):
    return False

  # backward compatibility
  if not metadata_dict.get('file'):
    metadata_dict['file'] = 'notused'
  if not metadata_dict.get('urlmd5'):
    metadata_dict['urlmd5'] = 'notused'

  # convert '' into None in order to call nc nicely
  if not signature_private_key_file:
    signature_private_key_file = None
  if not shacache_cert_file:
    shacache_cert_file = None
  if not shacache_key_file:
    shacache_key_file = None
  if not shadir_cert_file:
    shadir_cert_file = None
  if not shadir_key_file:
    shadir_key_file = None
  try:
    nc = NetworkcacheClient(cache_url, dir_url,
      signature_private_key_file=signature_private_key_file,
      shacache_cert_file=shacache_cert_file,
      shacache_key_file=shacache_key_file,
      shadir_cert_file=shadir_cert_file,
      shadir_key_file=shadir_key_file)
  except TypeError:
    logger.warning('Incompatible version of networkcache, not using it.')
    return False

  try:
    return nc.upload_generic(file_descriptor, directory_key, **metadata_dict)
  except (IOError, UploadError), e:
    logger.info('Failed to upload file. %s' % str(e))
    return False
  return True

def helper_upload_network_cached_from_file(dir_url, cache_url,
    path, directory_key, metadata_dict,
    signature_private_key_file, shacache_cert_file, shacache_key_file,
    shadir_cert_file, shadir_key_file):
  """
  Upload an existing file, using a file_descriptor.
  """
  file_descriptor = open(path, 'r')
  return helper_upload_network_cached(
      dir_url=dir_url,
      cache_url=cache_url,
      file_descriptor=file_descriptor,
      directory_key=directory_key,
      signature_private_key_file=signature_private_key_file,
      shacache_cert_file=shacache_cert_file,
      shacache_key_file=shacache_key_file,
      shadir_cert_file=shadir_cert_file,
      shadir_key_file=shadir_key_file,
      metadata_dict=metadata_dict,
  )

def helper_upload_network_cached_from_directory(dir_url, cache_url,
    path, directory_key, metadata_dict,
    signature_private_key_file, shacache_cert_file, shacache_key_file,
    shadir_cert_file, shadir_key_file):
  """
  Create a tar from a given directory (path) then upload it to networkcache.
  """
  # Create tar file. Don't create it to /tmp dir as it can be too small.
  path_dirname, path_basename = _split_last_directory(path)
  tarpath = os.path.join(path_dirname, '%s.tar' % path_basename)
  tar = tarfile.open(tarpath, "w:gz")
  try:
    try:
      tar.add(path, arcname=path_basename)
    finally:
      tar.close()
    # Upload it
    result = helper_upload_network_cached_from_file(dir_url, cache_url,
      tarpath, directory_key, metadata_dict,
      signature_private_key_file, shacache_cert_file, shacache_key_file,
      shadir_cert_file, shadir_key_file)
  finally:
    # Always clean it
    if os.path.exists(tarpath):
      os.remove(tarpath)
  return result


def helper_download_network_cached(dir_url, cache_url,
    signature_certificate_list, 
    directory_key, wanted_metadata_dict={}, required_key_list=[],
    strategy=None):
  """
  Downloads from a network cache provider.
  Select from shadir directory_key entry matching (at least)
  wanted_metadata_dict and with all metadata keys in required_key_list defined
  and not null.

  if a "strategy" function is given as parameter, use it to choose the best
  entry between list of matching entries. Otherwise, choose the first.
  This strategy function takes a list of entries as parameter, and should
  return the best entry.

  If something fails (providor be offline, or hash_string fail), we ignore
  network cached index.

  return (file_descriptor, metadata) if succeeded, False otherwise.
  """
  if not(dir_url and cache_url):
    return False

  if len(signature_certificate_list) == 0:
    # convert [] into None in order to call nc nicely
    signature_certificate_list = None

  try:
    nc = NetworkcacheClient(cache_url, dir_url,
        signature_certificate_list=signature_certificate_list)
  except TypeError:
    logger.warning('Incompatible version of networkcache, not using it.')
    return False

  logger.info('Trying to download %s from network cache...' % directory_key)
  try:
    file_descriptor = None
    json_entry_list = nc.select_generic(directory_key)
    # For each entry shadir sent, chooses only the entry matching all
    # wanted metadata, and having all wanted keys
    matching_entry_list = []
    for entry, _ in json_entry_list:
      try:
        tags = json.loads(entry)
        match = True
        for metadata_key, metadata_value in wanted_metadata_dict.items():
          if tags.get(metadata_key) != metadata_value:
            # Something doesn't match: not a good entry
            match = False
            break
          # Now checks if all required keys are present
          # i.e we want that entry contains a list key with not null
          # corresponding value
          for required_key in required_key_list:
            if not tags.get(required_key):
              match = False
              break
        if not match:
          continue
        # Everything match. Add it to list of matching entries
        matching_entry_list.append(tags)
      except Exception:
        pass
    if matching_entry_list:
    # If a strategy is defined, call it to determine best entry
      if strategy:
        best_entry = strategy(matching_entry_list)
        if not best_entry:
          logger.info("Can't find best entry matching strategy, selecting "
              "random one between acceptable ones.")
          best_entry = matching_entry_list[0]
      else:
        best_entry = matching_entry_list[0]

      # download best entry
      file_descriptor = nc.download(best_entry.get('sha512'))
      return file_descriptor, tags
    else:
      logger.info('No matching entry to download from network cache: %s'\
          % directory_key)
      return False

  except (IOError, DirectoryNotFound), e:
    if isinstance(e, urllib2.HTTPError) and e.code == 404:
      logger.info('%s does not exist in network cache.' % directory_key)
    else:
      logger.warning('Failed to download from network cache %s: %s' % (
          directory_key, str(e)))
  return False


def helper_download_network_cached_to_file(dir_url, cache_url,
    signature_certificate_list,
    directory_key, path, wanted_metadata_dict={}, required_key_list=[],
    strategy=None):
  """
  Download a file from network cache. It is the responsibility of caller method
  to check md5.
  """
  result = helper_download_network_cached(dir_url, cache_url,
      signature_certificate_list,
      directory_key, wanted_metadata_dict, required_key_list, strategy)
  if result:
    # XXX check if nc filters signature_certificate_list!
    # Creates a file with content to desired path.
    file_descriptor, metadata_dict = result
    f = open(path, 'w+b')
    try:
      shutil.copyfileobj(file_descriptor, f)
      # XXX method should check MD5.
      return metadata_dict
    finally:
      f.close()
      file_descriptor.close()
  return False

def helper_download_network_cached_to_directory(dir_url, cache_url,
    signature_certificate_list,
    directory_key, path, wanted_metadata_dict={}, required_key_list=[],
    strategy=None):
  """
  Download a tar file from network cache and untar it to specified path.
  """
  # Download tar file. Don't download to /tmp dir as it can be too small.
  path_dirname, path_basename = _split_last_directory(path)
  tarpath = os.path.join(path_dirname, '%s.tar' % path_basename)
  try:
    metadata_dict = helper_download_network_cached_to_file(
      dir_url, cache_url,
      signature_certificate_list,
      directory_key, tarpath, wanted_metadata_dict, required_key_list,
      strategy)
    if metadata_dict:
      # Untar it to path
      tar = tarfile.open(tarpath)
      try:
        logger.info("Extracting downloaded archive from cache...")
        tar.extractall(path=os.path.dirname(path))
      finally:
        tar.close()

  finally:
    # Always clean it
    if os.path.exists(tarpath):
      os.remove(tarpath)
  return metadata_dict
