Introduction
============

Create a GalleryImage type. The purpose of this field is to provide
a more robust field for collective.plonetruegallery to utilize
for some of it's galleries.

Implementation
--------------

Utilizes the Image type along with archetypes.schemaextender to create
the type. The benefit of using this approach is that there is no new
persistent object types added to the zodb so uninstall should be a breeze
and removing the product will mean those existing types will behave just
like the normal image type.
