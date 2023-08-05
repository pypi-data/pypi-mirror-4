.. -*-doctest-*-

Comma List
==========

An extension of the list criteria provides a text form input accepting
a comma separated list of keywords.

We start with a topic.

    >>> from Products.CMFCore.utils import getToolByName
    >>> portal = layer['portal']
    >>> membership = getToolByName(portal, 'portal_membership')

    >>> from plone.app import testing
    >>> folder = membership.getHomeFolder(testing.TEST_USER_ID)
    >>> foo_topic = folder['foo-topic-title']

Open a browser as an anonymous user.

    >>> from plone.testing import z2
    >>> from plone.app import testing
    >>> browser = z2.Browser(layer['app'])
    >>> browser.handleErrors = False

Add a list criterion for the subject/keywords.

    >>> foo_topic.addCriterion(
    ...     'Subject', 'FormCommaCriterion')
    <FormCommaCriterion at
    /plone/Members/test_user_1_/foo-topic-title/crit__Subject_FormCommaCriterion>

Designate the criterion's field as a form field.

    >>> crit = foo_topic.getCriterion('Subject_FormCommaCriterion')
    >>> crit.setValue(['foobar', 'bax'])
    >>> crit.setFormFields(['value'])

    >>> import transaction
    >>> transaction.commit()

When viewing the collection in a browser lists will be rendered
for the field with the default values selected.

    >>> browser.open(foo_topic.absolute_url())
    >>> ctrl = browser.getControl(
    ...     name='form_crit__Subject_FormCommaCriterion_value')
    >>> ctrl
    <Control name='form_crit__Subject_FormCommaCriterion_value'
    type='text'>
    >>> ctrl.value
    'foobar, bax'

By default the criterion values determine the search results.

    >>> browser.getLink('Bar Document Title')
    Traceback (most recent call last):
    LinkNotFoundError
    >>> browser.getLink('Baz Event Title')
    Traceback (most recent call last):
    LinkNotFoundError

Also note that criteria that use a 'value' field as the primary search
value do not render the label for the value field as it would be
redundant.

    >>> 'Values</label>' in browser.contents
    False

Since the comma widget require special input syntax, however, the help
text is rendered.

    >>> ('form_crit__Subject_FormCommaCriterion_value_help'
    ...  in browser.contents)
    True

Change the checked values and search

    >>> browser.getControl(
    ...     name='form_crit__Subject_FormCommaCriterion_value'
    ...     ).value = 'bah, quux'
    >>> form = browser.getForm(name="formcriteria_search")
    >>> form.getControl(name='submit').click()

Now the default has been overriden by the submitted query.

    >>> browser.getLink('Bar Document Title')
    <Link text='...Bar Document Title'
    url='http://nohost/plone/Members/test_user_1_/bar-document-title'>
    >>> browser.getLink('Baz Event Title')
    <Link text='...Baz Event Title'
    url='http://nohost/plone/Members/test_user_1_/baz-event-title'>

The form reflects the submitted value.

    >>> form = browser.getForm(name="formcriteria_search")
    >>> form.getControl(
    ...     name='form_crit__Subject_FormCommaCriterion_value'
    ...     ).value
    'bah, quux'
