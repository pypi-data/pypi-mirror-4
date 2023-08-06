------------
Z3C template
------------

This package allows you to register templates independently from view code.

In Zope 3, when registering a `browser:page` both presentation and computation
are registered together. Unfortunately the registration tangles presentation
and computation so tightly that it is not possible to re-register a different
template depending on context. (You can override the whole registration but
this is not the main point of this package.)

With z3c.template the registration is split up between the view and the
template and allows to differentiate the template based on the skin layer and
the view.

In addition this package lays the foundation to differentiate between
templates that provide specific presentation templates and generic layout
templates.
