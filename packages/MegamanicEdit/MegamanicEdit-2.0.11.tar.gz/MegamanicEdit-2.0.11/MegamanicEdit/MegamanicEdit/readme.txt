MegamanicEdit is a tool which enables constructing objects where
fields are "dynamic", for example in GrailTact, a user can add several
Email objects, and these are treated as regular fields when editing
the container (Contact) object.

It also enables adding objects from a template, so for example leads
interested in something can be greated from a landing page (see
GrailTact also here).

Has been tested and found working with StringWidget, RichWidget,
LinesWidget.  Assumed to work with everything except the
CalendarWidget.

Thanks to Bluedynamics' AtMultiEdit for giving a good example.

Portions of the templates/skins are taken from the Archetypes
product, which is

"Copyright (c) 2002-2006, Benjamin Saller <bcsaller@ideasuite.com>, and 
                        the respective authors.
All rights reserved."

NOTE: Currently only known to support text fields and areas.

Use the 'Add portal content' permission for all project content types,
so that it integrates nicely with the megamanic template object class.

TODO:

  Add support for more fields and widgets

  Add support for LinguaPlone
