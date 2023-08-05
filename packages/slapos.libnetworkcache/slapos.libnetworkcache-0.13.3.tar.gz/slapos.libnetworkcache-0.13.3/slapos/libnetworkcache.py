##############################################################################
#
# Copyright (c) 2010 ViFiB SARL and Contributors.
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


import base64
import hashlib
import httplib
import json
import os
import socket
import subprocess
import tempfile
import traceback
import urllib2
import urlparse

# XXX: code between select/select_generic and upload/upload_generic should be
# factored

# Upload/download timeout is one day
TIMEOUT = 3600 * 24

class NetworkcacheClient(object):
  '''
    NetworkcacheClient is a wrapper for httplib.
    It must implement all the required methods to use:
     - SHADIR
     - SHACACHE
  '''

  openssl = 'openssl'
  def parseUrl(self, url):
    return_dict = {}
    parsed_url = urlparse.urlparse(url)
    return_dict['header_dict'] = {'Content-Type': 'application/json'}
    user = parsed_url.username
    passwd = parsed_url.password
    if user is not None:
      authentication_string = '%s:%s' % (user, passwd)
      base64string = base64.encodestring(authentication_string).strip()
      return_dict['header_dict']['Authorization'] = 'Basic %s' %\
        base64string

    return_dict['path'] = parsed_url.path
    return_dict['host'] = parsed_url.hostname
    return_dict['scheme'] = parsed_url.scheme
    return_dict['port'] = parsed_url.port or \
                           socket.getservbyname(parsed_url.scheme)

    return return_dict

  def __init__(self, shacache, shadir, signature_private_key_file=None,
      signature_certificate_list=None, shacache_key_file=None,
      shacache_cert_file=None, shadir_key_file=None, shadir_cert_file=None):
    """Initializes shacache object.

    Parameters:
      shacache
        URL to shacache.
        Required.

      shadir
        URL to shadir.
        Required.

      signature_private_key_file
        Path to private key file used for signing content.
        Optional.

      signature_certificate_list
        List of strings of certificates to verify content.
        Optional

      shacache_key_file
        Key file used to authenticate to shacache.
        Optional.

      shacache_cert_file
        Certificate file used to authenticate to shacache.
        Optional.

      shadir_key_file
        Key file used to authenticate to shadir.
        Optional.

      shadir_cert_file
        Certificate file used to authenticate to shadir.
        Optional.
      """
    # ShaCache Properties
    for k, v in self.parseUrl(shacache).iteritems():
      setattr(self, 'shacache_%s' % k, v)
    self.shacache_url = shacache
    self.shadir_url = shadir

    # ShaDir Properties
    for k, v in self.parseUrl(shadir).iteritems():
      setattr(self, 'shadir_%s' % k, v)

    self.signature_private_key_file = signature_private_key_file
    if type(signature_certificate_list) is str:
      # If signature_certificate_list is a string, parse it to a list of
      # certificates
      cert_marker = "-----BEGIN CERTIFICATE-----"
      parsed_signature_certificate_list = [cert_marker + '\n' + q.strip() \
        for q in signature_certificate_list.split(cert_marker) \
          if q.strip()]
      self.signature_certificate_list = parsed_signature_certificate_list
    else:
      self.signature_certificate_list = signature_certificate_list

    self.shacache_key_file = shacache_key_file
    self.shacache_cert_file = shacache_cert_file
    self.shadir_key_file = shadir_key_file
    self.shadir_cert_file = shadir_cert_file

  def upload(self, file_descriptor, key=None, urlmd5=None, file_name=None,
    valid_until=None, architecture=None):
    ''' Upload the file to the server.
    If urlmd5 is None it must only upload to SHACACHE.
    Otherwise, it must create a new entry on SHADIR.
    '''
    sha512sum = hashlib.sha512()
    # do not trust, go to beginning of opened file
    file_descriptor.seek(0)
    while True:
      d = file_descriptor.read(sha512sum.block_size)
      if not d:
        break
      sha512sum.update(d)
    sha512sum = sha512sum.hexdigest()

    file_descriptor.seek(0)
    if self.shacache_scheme == 'https':
      shacache_connection = httplib.HTTPSConnection(self.shacache_host,
        self.shacache_port, key_file=self.shacache_key_file,
        cert_file=self.shacache_cert_file, timeout=TIMEOUT)
    else:
      shacache_connection = httplib.HTTPConnection(self.shacache_host,
        self.shacache_port, timeout=TIMEOUT)
    try:
      shacache_connection.request('POST', self.shacache_path, file_descriptor,
                                                 self.shacache_header_dict)
      result = shacache_connection.getresponse()
      data = result.read()
    finally:
      shacache_connection.close()

    if result.status != 201 or data != sha512sum:
      raise UploadError('Failed to upload the file to SHACACHE Server.' \
                        'URL: %s. Response code: %s. Response data: %s' % \
                                   (self.shacache_host, result.status, data))

    if key is not None:
      if file_name is None or urlmd5 is None:
        raise ValueError('In case if key is given file_name and urlmd5 '
          'are required.')
      kw = dict()
      kw['file'] = file_name
      kw['urlmd5'] = urlmd5
      kw['sha512'] = sha512sum

      if valid_until is not None:
        kw['valid-until'] = valid_until
      if architecture is not None:
        kw['architecture'] = architecture

      sha_entry = json.dumps(kw)
      try:
        signature = self._getSignatureString(sha_entry)
      except Exception:
        raise UploadError('Impossible to sign content, error:\n%s' %
          traceback.format_exc())
      data = [sha_entry, signature]

      if self.shadir_scheme == 'https':
        shadir_connection = httplib.HTTPSConnection(self.shadir_host,
          self.shadir_port, key_file=self.shadir_key_file,
          cert_file=self.shadir_cert_file, timeout=TIMEOUT)
      else:
        shadir_connection = httplib.HTTPConnection(self.shadir_host,
          self.shadir_port, timeout=TIMEOUT)
      try:
        shadir_connection.request('PUT', '/'.join([self.shadir_path, key]),
          json.dumps(data), self.shadir_header_dict)
        result = shadir_connection.getresponse()
        data = result.read()
      finally:
        shadir_connection.close()

      if result.status != 201:
        raise UploadError('Failed to upload data to SHADIR Server.' \
                          'URL: %s. Response code: %s. Response data: %s' % \
                                     (self.shacache_host, result.status, data))
    return True

  def upload_generic(self, file_descriptor, key=None, **kw):
    ''' Upload the file to the server.
    If key is None, it must only upload to SHACACHE.
    Otherwise, it must create a new entry on SHADIR.
    '''
    sha512sum = hashlib.sha512()
    file_descriptor.seek(0)
    while True:
      d = file_descriptor.read(sha512sum.block_size)
      if not d:
        break
      sha512sum.update(d)
    sha512sum = sha512sum.hexdigest()
    file_descriptor.seek(0)
    if self.shacache_scheme == 'https':
      shacache_connection = httplib.HTTPSConnection(self.shacache_host,
        self.shacache_port, key_file = self.shacache_key_file,
        cert_file = self.shacache_cert_file, timeout=TIMEOUT)
    else:
      shacache_connection = httplib.HTTPConnection(self.shacache_host,
        self.shacache_port, timeout=TIMEOUT)
    try:
      shacache_connection.request('POST', self.shacache_path, file_descriptor,
                                      self.shacache_header_dict)
      result = shacache_connection.getresponse()
      data = result.read()
    finally:
      shacache_connection.close()
    if result.status != 201 or data != sha512sum:
      raise UploadError('Failed to upload the file to SHACACHE Server.' \
                        'URL: %s. Response code: %s. Response data: %s' % \
                            (self.shacache_host, result.status, data))

    if key is not None:
      kw['sha512'] = data # always update sha512sum
      sha_entry = json.dumps(kw)
      try:
        signature = self._getSignatureString(sha_entry)
      except Exception:
        raise UploadError('Impossible to sign content, error:\n%s' %
          traceback.format_exc())
      data = [sha_entry, signature]
      if self.shadir_scheme == 'https':
        shadir_connection = httplib.HTTPSConnection(self.shadir_host,
          self.shadir_port, key_file = self.shadir_key_file,
          cert_file = self.shadir_cert_file, timeout=TIMEOUT)
      else:
        shadir_connection = httplib.HTTPConnection(self.shadir_host,
          self.shadir_port, timeout=TIMEOUT)
      try:
        shadir_connection.request('PUT', '/'.join([self.shadir_path, key]),
          json.dumps(data), self.shadir_header_dict)
        result = shadir_connection.getresponse()
        data = result.read()
      finally:
        shadir_connection.close()
      if result.status != 201:
        raise UploadError('Failed to upload data to SHADIR Server.' \
                          'URL: %s. Response code: %s. Response data: %s' % \
                              (self.shadir_host, result.status, data))

    return True

  def download(self, sha512sum):
    ''' Download the file.
    It uses http GET request method.
    '''
    sha_cache_url = os.path.join(self.shacache_url, sha512sum)
    request = urllib2.Request(url=sha_cache_url, data=None,
      headers=self.shadir_header_dict)
    return urllib2.urlopen(request)

  def select(self, key):
    ''' Download a file from shacache by selecting the entry in shadir
    Raise DirectoryNotFound if no trustable file is found.
    '''
    url = os.path.join(self.shadir_url, key)
    request = urllib2.Request(url=url, data=None,
      headers=self.shadir_header_dict)
    data = urllib2.urlopen(request).read()
    # Filtering...
    try:
      data_list = json.loads(data)
    except Exception:
      raise DirectoryNotFound('It was impossible to parse json response:\n%s'%
        traceback.format_exc())
    filtered_data_list = []
    if self.signature_certificate_list is not None:
      for data in data_list:
        if len(data[1]):
          if self._verifySignatureInCertificateList(data[0], data[1]):
            filtered_data_list.append(data)
    else:
      filtered_data_list = data_list

    if len(filtered_data_list) == 0:
      raise DirectoryNotFound('Could not find a trustable entry.')

    information_json, signature = filtered_data_list[0]
    try:
      information_dict = json.loads(information_json)
    except Exception:
      raise DirectoryNotFound('It was impossible to parse json-in-json '
        'response:\n%s' % traceback.format_exc())
    try:
      sha512 = information_dict.get('sha512')
    except Exception:
      raise DirectoryNotFound('It was impossible to fetch sha512 from '
        'directory response (%r):\n%s' % (information_dict,
          traceback.format_exc()))
    return self.download(sha512)

  def select_generic(self, key):
    ''' Select trustable entries from shadir.
    '''
    url = os.path.join(self.shadir_url, key)
    request = urllib2.Request(url=url, data=None,
      headers=self.shadir_header_dict)
    data = urllib2.urlopen(request).read()
    try:
      data_list = json.loads(data)
    except Exception:
      raise DirectoryNotFound('It was impossible to parse json response:\n%s' %
        traceback.format_exc())
    filtered_data_list = []
    for data in data_list:
      if len(data[1]):
        if self._verifySignatureInCertificateList(data[0], data[1]):
          filtered_data_list.append(data)
    return filtered_data_list

  def _getSignatureString(self, content):
    """
      Return the signature based on certification file.
    """
    if self.signature_private_key_file is None:
      return ''

    content_file = tempfile.NamedTemporaryFile()
    content_file.write(content)
    content_file.flush()
    content_file.seek(0)
    try:
      signature = subprocess.check_output([self.openssl, "dgst", "-sha1",
            "-sign", self.signature_private_key_file, content_file.name])
      return signature.encode('base64')
    finally:
      content_file.close()

  def _verifySignatureInCertificateList(self, content, signature_string):
    """
      Returns true if it can find any valid certificate or false if it does not
      find any.
    """
    if self.signature_certificate_list is not None:
      for certificate in self.signature_certificate_list:
        if self._verifySignatureCertificate(content, signature_string,
            certificate):
          return True
    return False

  def _verifySignatureCertificate(self, content, signature_string,
      certificate):
    """ verify if the signature is valid for a given certificate. """
    certificate_file = tempfile.NamedTemporaryFile()
    certificate_file.write(certificate)
    certificate_file.flush()
    certificate_file.seek(0)
    signature_file = tempfile.NamedTemporaryFile()
    signature_file.write(signature_string.decode('base64'))
    signature_file.flush()
    signature_file.seek(0)
    content_file = tempfile.NamedTemporaryFile()
    content_file.write(content)
    content_file.flush()
    content_file.seek(0)
    pubkey_file = tempfile.NamedTemporaryFile()
    try:
      last_output = ''
      try:
        last_output = subprocess.check_output([self.openssl, "x509", "-pubkey",
            "-noout", "-in", certificate_file.name])
        pubkey_file.write(last_output)
        pubkey_file.flush()
        pubkey_file.seek(0)
        try:
          last_output = subprocess.check_output([self.openssl, "dgst", "-sha1",
              "-verify", pubkey_file.name, "-signature", signature_file.name,
              content_file.name])
        except subprocess.CalledProcessError, e:
          # in case if verification failed
          last_output = e.output
        if last_output.startswith('Verified OK'):
          return True
      except Exception:
        # in case of failure, emit *anything*, but swallow all what possible
        print last_output
        print traceback.format_exc()
      return False
    finally:
      certificate_file.close()
      signature_file.close()
      content_file.close()
      pubkey_file.close()


class DirectoryNotFound(Exception):
  pass


class UploadError(Exception):
  pass
