.. -*-doctest-*-

=================
Pulldown Criteria
=================

Three criterion are provided for rendering pulldown menus on the
search form: FormPulldownCriterion, FormPortalTypePulldownCriterion,
FormReferencePulldownCriterion.

We start with a topic.

    >>> from Products.CMFCore.utils import getToolByName
    >>> portal = layer['portal']
    >>> membership = getToolByName(portal, 'portal_membership')

    >>> from plone.app import testing
    >>> folder = membership.getHomeFolder(testing.TEST_USER_ID)
    >>> foo_topic = folder['foo-topic-title']

Add a criterion to the topic.

    >>> path_crit = foo_topic.addCriterion(
    ...     'path', 'FormRelativePathCriterion')
    >>> path_crit.setRecurse(True)

Open a browser as an anonymous user.

    >>> from plone.testing import z2
    >>> from plone.app import testing
    >>> browser = z2.Browser(layer['app'])
    >>> browser.handleErrors = False

Add a pulldown criterion for the portal type.

    >>> foo_topic.addCriterion(
    ...     'Type', 'FormPortalTypePulldownCriterion')
    <FormPortalTypePulldownCriterion at
    /plone/Members/test_user_1_/foo-topic-title/crit__Type_FormPortalTypePulldownCriterion>

Designate the criterion's field as a form field.

    >>> crit = foo_topic.getCriterion(
    ...     'Type_FormPortalTypePulldownCriterion')
    >>> crit.setFormFields(['value'])

The values set on the criterion are the default values checked on the
search form.

    >>> crit.setValue('Page')

    >>> import transaction
    >>> transaction.commit()

When viewing the collection in a browser pulldown menus will be
rendered for the field with the default values selected.

    >>> browser.open(foo_topic.absolute_url())
    >>> browser.getControl('Page')
    <ItemControl
    name='form_crit__Type_FormPortalTypePulldownCriterion_value'
    type='select' optionValue='Page' selected=True>
    >>> browser.getControl('Event')
    <ItemControl
    name='form_crit__Type_FormPortalTypePulldownCriterion_value'
    type='select' optionValue='Event' selected=False>

By default the criterion values determine the search results.

    >>> browser.getLink('Bar Document Title')
    <Link text='...Bar Document Title'
    url='http://nohost/plone/Members/test_user_1_/bar-document-title'>
    >>> browser.getLink('Baz Event Title')
    Traceback (most recent call last):
    LinkNotFoundError

Change the checked values and search

    >>> form = browser.getForm(name="formcriteria_search")
    >>> form.getControl('Event').selected = True
    >>> form.getControl(name='submit').click()

Now the default has been overriden by the submitted query.

    >>> browser.getLink('Bar Document Title')
    Traceback (most recent call last):
    LinkNotFoundError
    >>> browser.getLink('Baz Event Title')
    <Link text='...Baz Event Title'
    url='http://nohost/plone/Members/test_user_1_/baz-event-title'>

If no value is set, all results should be returned.

    >>> crit.setValue('')

    >>> import transaction
    >>> transaction.commit()

    >>> browser.open(foo_topic.absolute_url())
    >>> form = browser.getForm(name="formcriteria_search")
    >>> form.getControl(name='submit').click()
    >>> browser.getLink('Bar Document Title')
    <Link text='...Bar Document Title'
    url='http://nohost/plone/Members/test_user_1_/bar-document-title'>
    >>> browser.getLink('Baz Event Title')
    <Link text='...Baz Event Title'
    url='http://nohost/plone/Members/test_user_1_/baz-event-title'>
