=============================
Sample Data Generator Manager
=============================

The sample data generator manager allowes the user to configurate the
parameters for the registered generators.

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.addHeader('Authorization','Basic mgr:mgrpw')
  >>> browser.handleErrors = False

We select the sample data manager overview.

  >>> browser.open('http://localhost/@@managesamples.html')

Now we select our samplemanager.

  >>> browser.getLink(text='samplemanager').click()
  >>> browser.url
  'http://localhost/@@generatesample.html?manager=samplemanager'

We are now in the configuration view for the selected manager.

  >>> browser.getControl(name='generator.seed').value = 'lovely'
  >>> browser.getControl(
  ...       name='z3c.sampledata.site.sitename').value = 'testsite'
  >>> browser.getControl(
  ...       name='z3c.sampledata.principals.minPrincipals').value = '2'
  >>> browser.getControl(
  ...       name='z3c.sampledata.principals.maxPrincipals').value = '34'
  >>> browser.getControl(
  ...       name='z3c.sampledata.principals.pauLocation').value = 'default/pau'
  >>> browser.getControl('Generate').click()

