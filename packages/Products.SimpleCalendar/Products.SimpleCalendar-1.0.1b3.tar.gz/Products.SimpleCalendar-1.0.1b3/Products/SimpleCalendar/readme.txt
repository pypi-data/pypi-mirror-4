Products.SimpleCalendar is a simple, accessible display-only
calendaring solution for Plone.  It was created to ensure that a
simple, accessible (table-based listing) calendaring solution exists,
and is a viable alternative to p4a.plonecalendar.

In many ways it is similar to p4a.plonecalendar, as it makes use of
the dateable.chronos and dateable.kalends code as well, and also
depends on some p4a code, a dependency that was discovered when
developing Products.SimpleCalendar.

An alpha release for now, using hacks and adapter goodies to get
things working.  Enjoy.  :)

To install, add Products.SimpleCalendar to buildout and re-run
buildout, restart Zope and install the SimpleCalendar and Chronos
products in the Plone control panel add-ons section.

Customize chronos.css in portal_view_customizations so that it
contains

#chronos-month td.dayNotInThisMonth a {
    display: inline;
}

to have events taking place in a day outside of the current month
displayed.

TODO: Implement interface-based fetching of events
