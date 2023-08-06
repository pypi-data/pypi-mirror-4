MenuNavigation lets you add HTML descriptions to objects in Plone.

Add a new HTML-description by selecting MenuPage from the "Add new..."
Menu. The Title is automatically generated, and the Content-field
takes HTML or text. (It is added with tal:replace structure)

You can add portlets to show the HTML-description:
    Add a Classic Portlet with the following settings:

        Template: info_portlet
    	Macro: portlet

The portlet searches through context for a MenuPage, if none are found
it searches all the parents of context until site-root, and returns
the first MenuPage it finds. Site-root is not searched, and can not
use the portlet. If no menupages are found, the portlet displays
nothing.
