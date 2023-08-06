Testing the configlet
=====================

Basic Setup
-----------

	>>> from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD
	>>> from openmultimedia.headband.testing import generate_jpeg_file
		
	>>> portal = layer.get('app').plone
	>>> browser = z2.Browser(layer['app'])
	>>> browser.open(portal.absolute_url() + '/login_form')
	>>> browser.getControl(name='__ac_name').value = SITE_OWNER_NAME
	>>> browser.getControl(name='__ac_password').value = SITE_OWNER_PASSWORD
	>>> browser.getControl(name='submit').click()

	>>> browser.open(portal.absolute_url() + '/@@overview-controlpanel')
	>>> browser.getLink('openmultimedia.headband settings').click()
	>>> 'openmultimedia.headband settings' in browser.contents
	True

	# Testing cancel action
	>>> browser.getControl('Cancel').click()
	>>> 'openmultimedia.headband settings' in browser.contents
	True
	>>> '@@openmultimedia.headband/image' in browser.contents
	False

	# Testing save action
	>>> browser.open(portal.absolute_url() + '/@@overview-controlpanel')
	>>> browser.getLink('openmultimedia.headband settings').click()
	>>> control = browser.getControl(name='form.widgets.image')
  	>>> control.filename = 'bar.gif'
  	>>> control.value = generate_jpeg_file(200, 100)
	>>> browser.getControl('Save').click()
	>>> 'openmultimedia.headband settings' in browser.contents
	True
	>>> '@@openmultimedia.headband/image' in browser.contents
	True

	# Testing save action without changing the image
	>>> browser.open(portal.absolute_url() + '/@@overview-controlpanel')
	>>> browser.getLink('openmultimedia.headband settings').click()
	>>> browser.getControl('Save').click()
	>>> 'openmultimedia.headband settings' in browser.contents
	True
	>>> '@@openmultimedia.headband/image' in browser.contents
	True

	# Testing cancel action without changing the image
	>>> browser.open(portal.absolute_url() + '/@@overview-controlpanel')
	>>> browser.getLink('openmultimedia.headband settings').click()
	>>> browser.getControl('Cancel').click()
	>>> 'openmultimedia.headband settings' in browser.contents
	True
	>>> '@@openmultimedia.headband/image' in browser.contents
	True
