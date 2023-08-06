==========
 Bugfixes
==========

Traversed objects were not security proxied
===========================================

When an object got traversed its security proxy was removed, so its
sub-objects could be publically accessed. To show that this behavior
was fixed we put a folder into the root folder and look at its
contents using a view:

  >>> import zope.site.folder
  >>> getRootFolder()['test'] = zope.site.folder.Folder()

  >>> from webtest.app import TestApp
  >>> browser = TestApp(
  ...     make_wsgi_app(), extra_environ={
  ...         'wsgi.handleErrors': False,
  ...         'HTTP_AUTHORIZATION': 'Basic mgr:mgrpw'})
  >>> skinURL = 'http://localhost/++skin++PageletTestSkin'
  >>> res = browser.get(skinURL + '/container_contents.html')

The view displays the types of the content objects inside the root
folder. The content objects are security proxied:

  >>> print(res.body.decode())
  [<type 'zope.security._proxy._Proxy'>]
