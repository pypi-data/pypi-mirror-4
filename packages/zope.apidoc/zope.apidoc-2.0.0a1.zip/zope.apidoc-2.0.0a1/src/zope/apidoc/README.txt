========================
Zope 3 API Documentation
========================

This Zope 3 package provides fully dynamic API documentation of Zope 3 and
registered add-on components. The package is very extensible and can be easily
extended by implementing new modules.

Besides being an application, the API doctool also provides several public
APIs to extract information from various objects used by Zope 3.

 * utilities -- Miscellaneous classes and functions that aid all documentation
   modules. They are broadly usable.

 * interface -- This module contains functions to inspect interfaces and
   schemas.

 * component -- This modules provides utility functions to lookup components
   given an interface.

 * presentation -- Presentation components are generally more complex than
   others, so a separate utilities module is provided to inspect views.

 * classregistry -- Here a simple dictionary-based registry for all known
   classes is provided. It allows us to search in classes.
