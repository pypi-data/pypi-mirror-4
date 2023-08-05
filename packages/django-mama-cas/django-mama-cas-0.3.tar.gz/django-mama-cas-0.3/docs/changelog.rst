.. _changelog:

Changelog
=========

This is an overview of all notable changes between each release of
django-mama-cas. Backwards incompatible changes or other potential problems
are noted here, so it's great reading material before upgrading. Unlisted
versions are internal milestone releases and are not official release
versions.

Not enough detail? Perhaps the complete `commit history
<https://github.com/jbittel/django-mama-cas/commits/>`_ meets your needs.

**django-mama-cas 0.3**
   * Implement warn parameter for the credential acceptor
   * Parse XML in tests to better check validity
   * Fix partial logout with the renew parameter
   * Implement custom attributes returned with a validation success

**django-mama-cas 0.2**
   * Implement internationalization
   * Add proxy ticket validation
   * Substantial improvements to the test suite
   * Add traversed proxies to proxy validation response
   * Add form class to extract usernames from email addresses
