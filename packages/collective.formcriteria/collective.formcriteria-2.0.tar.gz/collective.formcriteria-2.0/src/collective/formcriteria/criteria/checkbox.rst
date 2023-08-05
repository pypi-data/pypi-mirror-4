.. -*-doctest-*-

==========
Checkboxes
==========

Three criterion are provided for rendering checkboxes on the search
form: FormCheckboxCriterion, FormPortalTypeCheckboxCriterion,
FormReferenceCheckboxCriterion.

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

Add a checkbox criterion for the portal type.

    >>> foo_topic.addCriterion(
    ...     'Type', 'FormPortalTypeCheckboxCriterion')
    <FormPortalTypeCheckboxCriterion at
    /plone/Members/test_user_1_/foo-topic-title/crit__Type_FormPortalTypeCheckboxCriterion>

Designate the criterion's field as a form field.

    >>> crit = foo_topic.getCriterion(
    ...     'Type_FormPortalTypeCheckboxCriterion')
    >>> crit.setFormFields(['value'])

The values set on the criterion are the default values checked on the
search form.

    >>> crit.setValue(['Page'])

    >>> import transaction
    >>> transaction.commit()

When viewing the collection in a browser checkboxes will be rendered
for the field with the default values selected.

    >>> browser.open(foo_topic.absolute_url())
    >>> browser.getControl('Page')
    <ItemControl
    name='form_crit__Type_FormPortalTypeCheckboxCriterion_value:list'
    type='checkbox' optionValue='Page' selected=True>
    >>> browser.getControl('Event')
    <ItemControl
    name='form_crit__Type_FormPortalTypeCheckboxCriterion_value:list'
    type='checkbox' optionValue='Event' selected=False>

The portal type checkbox form criterion doesn't allow using "and" as a
query operator since it wouldn't make any sense.  As such the operator
field isn't rendered on the search form.

    >>> browser.getControl(
    ...     name='form_crit__Type_FormPortalTypeCheckboxCriterion'
    ...     '_operator')
    Traceback (most recent call last):
    LookupError: name
    'form_crit__Type_FormPortalTypeCheckboxCriterion_operator'

By default the criterion values determine the search results.

    >>> browser.getLink('Bar Document Title')
    <Link text='...Bar Document Title'
    url='http://nohost/plone/Members/test_user_1_/bar-document-title'>
    >>> browser.getLink('Baz Event Title')
    Traceback (most recent call last):
    LinkNotFoundError

Change the checked values and search

    >>> browser.getControl('Page').selected = False
    >>> browser.getControl('Event').selected = True
    >>> form = browser.getForm(name="formcriteria_search")
    >>> form.getControl(name='submit').click()

Now the default has been overriden by the submitted query.

    >>> browser.getLink('Bar Document Title')
    Traceback (most recent call last):
    LinkNotFoundError
    >>> browser.getLink('Baz Event Title')
    <Link text='...Baz Event Title'
    url='http://nohost/plone/Members/test_user_1_/baz-event-title'>
