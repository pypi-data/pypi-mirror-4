.. -*-doctest-*-

Sorting
=======

Two kinds of sort criteria are supported.  Multiple fixed sort
criteria can be defined allowing the user to select from among them
using links on the batch macro.  One form sort criterion can be added
per collection to allows the user to specify a sort on the sort form.
If both are used, and the user has both submitted a sort from the form
and selected a sort from the batch links, the latter criterion in the
list of criteria takes effect.

Form sort criteria are not yet implemented.

Fixed Sort Criteria
-------------------

Set the item count to 1 so that batches will only have one item.

    >>> from Products.CMFCore.utils import getToolByName
    >>> portal = layer['portal']
    >>> membership = getToolByName(portal, 'portal_membership')

    >>> from plone.app import testing
    >>> folder = membership.getHomeFolder(testing.TEST_USER_ID)
    >>> foo_topic = folder['foo-topic-title']
    >>> foo_topic.setItemCount(1)

    >>> import transaction
    >>> transaction.commit()

Open a browser and log in as a normal user.

    >>> from plone.testing import z2
    >>> from plone.app import testing
    >>> portal = layer['portal']
    >>> browser = z2.Browser(layer['app'])
    >>> browser.handleErrors = False
    >>> browser.open(portal.absolute_url())
    >>> browser.getLink('Log in').click()
    >>> browser.getControl('Login Name').value = testing.TEST_USER_NAME
    >>> browser.getControl(
    ...     'Password').value = testing.TEST_USER_PASSWORD
    >>> browser.getControl('Log in').click()

Load the criteria edit form of a collection.

    >>> browser.open(foo_topic.absolute_url())
    >>> browser.getLink('Criteria').click()

The sort selection form has been removed from the criteria tab.

    >>> browser.getForm(action="criterion_edit_form", index=1)
    Traceback (most recent call last):
    IndexError: list index out of range

Instead, multiple sort criteria can be added to a collection using the
normal criterion add form on the criteria tab.

    >>> form = browser.getForm(name="criteria_select")
    >>> form.getControl('Relevance').selected = True
    >>> form.getControl('Sort results').selected = True
    >>> form.getControl('Add criteria').click()
    >>> print browser.contents
    <...
    ...Added criterion FormSortCriterion for field unsorted...

Add another sort criterion for the Date field reversed.

    >>> form = browser.getForm(name="criteria_select")
    >>> form.getControl('Effective Date').selected = True
    >>> form.getControl('Sort results').selected = True
    >>> form.getControl('Add criteria').click()
    >>> print browser.contents
    <...
    ...Added criterion FormSortCriterion for field effective...

Change the display layout of the collection to the "Search Form" then
submit a search criteria to test that the sort links preserve search
criteria.

    >>> foo_topic.setLayout('criteria_form')
    >>> foo_topic.addCriterion(
    ...     'SearchableText','FormSimpleStringCriterion'
    ...     ).setFormFields(['value'])

    >>> import transaction
    >>> transaction.commit()

    >>> browser.getLink('View').click()
    >>> form = browser.getForm(name="formcriteria_search")
    >>> form.getControl('Search Text').value = 'blah'
    >>> form.getControl(name='submit').click()

When the batch macro is rendered on a collection view, such as one of
the listings, it includes links to the different possible sorts in
order.  By default, the first sort criteria is selected.  The sort
links also have id's and CSS classes for styling support.

    >>> print browser.contents
    <...
              Sort on:
                <span class="formcriteriaSortField selected">Relevance</span>
                <button...>Effective Date</button>
    ...
    >>> form = browser.getForm(name="navigation_form")
    >>> form.getControl(
    ...     name="crit__unsorted_FormSortCriterion:boolean")
    Traceback (most recent call last):
    LookupError: name
    'crit__unsorted_FormSortCriterion:boolean'

The results are listed in order of weight.

    >>> browser.getLink('Baz Event Title')
    <Link text='...Baz Event Title'
    url='http://nohost/plone/Members/test_user_1_/baz-event-title'>
    >>> browser.getLink('Bar Document Title')
    Traceback (most recent call last):
    LinkNotFoundError

When a sort link is clicked, that sort will show as selected and
results will be sorted according to the sort criteria.

    >>> form = browser.getForm(name="navigation_form")
    >>> form.getControl(
    ...     name="crit__effective_FormSortCriterion:boolean").click()
    >>> print browser.contents
    <...
    ...Sort on:...
    ...Relevance...
    ...Effective Date</span>...
    >>> form = browser.getForm(name="navigation_form")
    >>> form.getControl(
    ...     name="crit__effective_FormSortCriterion:boolean")
    <Control name='crit__effective_FormSortCriterion:boolean' type='hidden'>
    >>> form = browser.getForm(name="navigation_form")
    >>> form.getControl(
    ...     name="crit__unsorted_FormSortCriterion:boolean")
    <SubmitControl name='crit__unsorted_FormSortCriterion:boolean'
    type='submitbutton'>

The results reflect that the search query is preserved across the new
sort selection.

    >>> browser.getLink('Bar Document Title')
    <Link text='...Bar Document Title'
    url='http://nohost/plone/Members/test_user_1_/bar-document-title'>
    >>> browser.getLink('Baz Event Title')
    Traceback (most recent call last):
    LinkNotFoundError

If the next batch is selected the sort and search query are
preserved.

    >>> form = browser.getForm(name="navigation_form")
    >>> form.getControl(name="b_start", index=0).click()
    >>> browser.getLink('Bar Document Title')
    Traceback (most recent call last):
    LinkNotFoundError
    >>> browser.getLink('Baz Event Title')
    <Link text='...Baz Event Title'
    url='http://nohost/plone/Members/test_user_1_/baz-event-title'>

The batch macro will render the sort links even if there's only one
batch.

    >>> foo_topic.setItemCount(0)

    >>> import transaction
    >>> transaction.commit()

    >>> browser.open(foo_topic.absolute_url()+'/atct_topic_view')
    >>> form = browser.getForm(name="navigation_form")
    >>> form.getControl(
    ...     name="crit__effective_FormSortCriterion:boolean")
    <SubmitControl name='crit__effective_FormSortCriterion:boolean'
    type='submitbutton'>

Ensure that the extended sort criteria work inside previously created
ATTopic instances.

    >>> topic = folder['at-topic-title']
    >>> topic.setSortCriterion('effective', True)
    >>> topic.queryCatalog()[0].getObject()
    <ATEvent at /plone/Members/test_user_1_/baz-event-title>

Grouped Listing
---------------

A variation on the default collection view is provided that lists
items grouped by the sort used.  This requires that the index used for
sorting is also in the catalog metadata columns and this available on
the catalog brains.

Sort by creator to that we get at least one group with multiple
items.

    >>> foo_topic.deleteCriterion('crit__unsorted_FormSortCriterion')
    >>> foo_topic.setSortCriterion('Creator', False)

    >>> import transaction
    >>> transaction.commit()

Select the layout.

    >>> browser.open(foo_topic.absolute_url())
    >>> browser.getLink('Grouped Listing').click()
    >>> print browser.contents
    <...
    ...View changed...
    >>> browser.getLink('Log out').click()

Now the items are grouped by the sort values.

    >>> browser.open(foo_topic.absolute_url())
    >>> print browser.contents
    <...
    ...<dl...
    ...<dt...bar_creator_id...</dt>...
    ...<dd...
    ...Baz Event Title...
    ...</dd...
    ...<dt...foo_creator_id...</dt>...
    ...<dd...
    ...Foo Event Title...
    ...Bar Document Title...
    ...</dd...
    ...</dl>...

The grouped listing layout requires a sort criterion to render and
raises an error if one is not present.

    >>> foo_topic.deleteCriterion('crit__Creator_ATSortCriterion')

    >>> import transaction
    >>> transaction.commit()

    >>> browser.open(foo_topic.absolute_url())
    Traceback (most recent call last):
    AssertionError: ...

The batch macros still work for topics that have no sort criteria.

    >>> foo_topic.setLayout('criteria_form')

    >>> import transaction
    >>> transaction.commit()

    >>> browser.open(foo_topic.absolute_url())
    >>> form = browser.getForm(name="formcriteria_search")
    >>> form.getControl('Search Text').value = 'blah'
    >>> form.getControl(name='submit').click()
    >>> 'Sort on:' in browser.contents
    False
