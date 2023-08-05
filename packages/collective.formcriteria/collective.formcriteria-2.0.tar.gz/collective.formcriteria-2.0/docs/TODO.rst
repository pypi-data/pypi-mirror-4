TODO
====

* Replace KSS with jQuery for the AJAX folder contents stuff

* Tabs for folder_contents based multiple object edit form for topic
  containers such as topic columns.

* Separate query and sort criteria out into topic containers and use
  folder_contents based multi-edit form

* Add coverage for folder contents buttons when using KSS select all
  from all screens.  It didn't work for one deployment.

* Add a sort icon to sortable folder_contents columns

* Add support for including the URL in CSV export

  Not sure what the right UI is for this, maybe add a special case
  into the customViewFields field.

* Add criteria ordering support

* Form Sort Criteria
  
  An widget is avialable for selecting which of the possible
  sort fields should be available for sorting on.  The InAndOutWidget is
  used so that the order can be specified.
  
      >>> print browser.contents
      <...
      <div class="field ArchetypesInAndOutWidget
      kssattr-atfieldname-sortFields"
      id="archetypes-fieldname-sortFields">...
      ...>Relevance</option>...
      ...>Effective Date</option>...
  
  The InAndOutWidget uses JavaScript so we'll set the field manually for
  testing.
  
      >>> self.login()
      >>> foo_topic.setSortFields(['', 'effective', 'Type'])
  
      >>> form = browser.getForm(name="criteria_select")
      >>> form.getControl('Sort Order').selected = True
  
  Form sort criteria default to sorting on the "Relevance" field
  corresponds to a sort by weight for searches that include queries
  against indexs that support weighted results.
  
      >>> form = browser.getForm(action="criterion_edit_form", index=0)
      >>> form.getControl('Relevance').selected
      True

* Add AJAX search results refresh

* Add single selection (pulldown, radio) criteria (davisagli)

* Use subcollections to support AdvancedQuery operations

  Collections will act as grouping/parenthesis *and* operators.  IOW,
  a collection will have a boolean field to set whether it uses AND or
  OR to find the intersection or union of its result sets.
  Sub-collections will not acquire criteria but instead parent
  collections will treat sub-collections as criteria groupings.  Not
  yet sure how to handle sorting.
