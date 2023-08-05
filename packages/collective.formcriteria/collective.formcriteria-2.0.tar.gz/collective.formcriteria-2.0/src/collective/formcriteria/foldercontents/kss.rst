.. -*-doctest-*-

KSS Folder Contents
===================

The folder contents view uses KSS/AJAX to select all items and to sort
on the columns.

Set the batch size to force batching.

    >>> from Products.CMFCore.utils import getToolByName
    >>> portal = layer['portal']
    >>> membership = getToolByName(portal, 'portal_membership')

    >>> from plone.app import testing
    >>> folder = membership.getHomeFolder(testing.TEST_USER_ID)
    >>> foo_topic = folder['foo-topic-title']
    >>> foo_topic.update(itemCount=2)
    >>> foo_topic.crit__path_FormRelativePathCriterion.setRecurse(False)

Change the columns and link columns.

    >>> from plone.testing import z2
    >>> z2.login(portal.getPhysicalRoot().acl_users, testing.SITE_OWNER_NAME)
    >>> columns = foo_topic.columns
    >>> columns.manage_delObjects(
    ...     ['ModificationDate-column', 'get_size-column',
    ...      'review_state-column'])
    >>> columns['Title-column'].update(link=False, sort='')
    >>> desc_column = columns[columns.invokeFactory(
    ...     type_name='TopicColumn', id='Description-column',
    ...     link=True)]
    >>> effective_column = columns[columns.invokeFactory(
    ...     type_name='TopicColumn', id='EffectiveDate-column',
    ...     link=True)]
    >>> foo_topic.manage_delObjects(
    ...     ['crit__sortable_title_FormSortCriterion',
    ...      'crit__get_size_FormSortCriterion',
    ...      'crit__modified_FormSortCriterion',
    ...      'crit__review_state_FormSortCriterion'])
    >>> testing.logout()

    >>> import transaction
    >>> transaction.commit()

Open a browser and log in as a user who can view the topic.

    >>> portal = layer['portal']
    >>> browser = z2.Browser(layer['app'])
    >>> browser.handleErrors = False
    >>> browser.open(portal.absolute_url())
    >>> browser.getLink('Log in').click()
    >>> browser.getControl('Login Name').value = testing.TEST_USER_NAME
    >>> browser.getControl(
    ...     'Password').value = testing.TEST_USER_PASSWORD
    >>> browser.getControl('Log in').click()

Use the browser to load the XML KSS uses to update the table.

    >>> browser.open(
    ...     foo_topic.absolute_url()+'/foldercontents_update_table')

The XML reflects the customized columns

    >>> print browser.contents
    <...
    ...Title...
    ...Description...
    ...Effective Date...
    <input type="checkbox" class="noborder" name="paths:list"
    id="cb_-plone-Members-test_user_1_-bar-document-title"
    value="/plone/Members/test_user_1_/bar-document-title" alt="Select
    Bar Document Title" title="Select Bar Document Title" />
    ...Bar Document Title...
    ...blah...
    >>> from collective.formcriteria.testing import CONTENT_FIXTURE
    >>> now = CONTENT_FIXTURE.now
    >>> (now-2).ISO() in browser.contents
    True

    >>> 'Size' in browser.contents
    False
    >>> 'Modification Date' in browser.contents
    False
    >>> '&#160;State&#160;' in browser.contents
    False

    >>> '0 kB' in browser.contents
    False
    >>> '<span class="state-published">Published</span>' in browser.contents
    False

If the "Select: All" link is clicked, the screen is selected.

    >>> browser.open(
    ...     foo_topic.absolute_url()+'/foldercontents_update_table?'
    ...     'show_all=False&pagenumber=1&'
    ...     'sort_on=getObjPositionInParent&select=screen')

    >>> print browser.contents
    <...
    ...Select all 4 items in this collection...
    ...Title...
    ...Description...
    ...Effective Date...
    <input type="checkbox" class="noborder" name="paths:list"
    id="cb_-plone-Members-test_user_1_-bar-document-title"
    value="/plone/Members/test_user_1_/bar-document-title"...
    ...Bar Document Title...
    ...blah...
    >>> (now-2).ISO() in browser.contents
    True

If the next "Select all" link is clicked, all items in the collection
are selected.

    >>> browser.open(
    ...     foo_topic.absolute_url()+'/foldercontents_update_table?'
    ...     'show_all=False&pagenumber=1&'
    ...     'sort_on=getObjPositionInParent&select=all')

    >>> print browser.contents
    <...
    ...All 4 items in this collection are selected...
    ...Title...
    ...Description...
    ...Effective Date...
    <input type="checkbox" class="noborder" name="paths:list"
    id="cb_-plone-Members-test_user_1_-bar-document-title"
    value="/plone/Members/test_user_1_/bar-document-title"...
    ...Bar Document Title...
    ...blah...
    >>> (now-2).ISO() in browser.contents
    True

Finally, the batching can be overridden by clicking "Show all" at the
bottom of the table.

    >>> browser.open(
    ...     foo_topic.absolute_url()+'/foldercontents_update_table?'
    ...     'show_all=true&pagenumber=1&'
    ...     'sort_on=getObjPositionInParent')

    >>> print browser.contents
    <...
    ...Title...
    ...Description...
    ...Effective Date...
    ...Show batched...
    <input type="checkbox" class="noborder" name="paths:list"
    id="cb_-plone-Members-test_user_1_-bar-document-title"
    value="/plone/Members/test_user_1_/bar-document-title"...
    ...Bar Document Title...
    ...blah...
    ...Foo Topic Title...
    >>> (now-2).ISO() in browser.contents
    True

KSS sorting

TODO
