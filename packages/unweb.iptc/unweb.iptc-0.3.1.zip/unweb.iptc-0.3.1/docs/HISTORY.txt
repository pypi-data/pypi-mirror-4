Changelog
=========

0.3.1 (2012-12-21)
------------------

- handle images with latin-1 encoded iptc data too. description works
  ootb, title needs an extra encoding try. [fRiSi] 

0.3 (2011-12-02)
----------------

- Cleanup dependencies [fRiSi]

  * remove unnecessary depencency on grok
  * no need to initialize the package as Zope2 product
  * move dependencies on plone.app.testing and interlude to
    `unweb.iptc[test]` extra
  * Add dependency on Procuts.CMFPlone and ATContentTypes


0.2 (2010-11-22)
----------------

- Remove empty locales folder which was causing problems in some buildouts

0.1 (2010-11-13)
----------------

- Initial release
