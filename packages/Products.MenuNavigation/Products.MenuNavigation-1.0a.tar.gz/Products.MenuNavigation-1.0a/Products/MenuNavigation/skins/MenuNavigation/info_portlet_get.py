## Script (Python) "info_portlet_get"
##title=Handler for old URLs
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=object_=None

def find_menupage_text(context):
    """Searches through context for a menupage"""
    try:
        objects = getattr(context, "objectValues", None)
        if objects is None:
            # Context is not searchable
            return
        for item in objects():
            if getattr(item, "meta_type", None) == "MenuPage":
                if item.portal_workflow.getInfoFor(item, "review_state", "") == "published":
                    # Only published menupages should be shown.
                    return item.getText()
        return
    except Exception, value:
        return

def get_body(context):
    """Searches context and all its parents until site-root for a menupage and returns the body (text) of the closest one found. Site-root is not searched"""
    # Might be a bad idea if site-root isnt the final parent (does this ever happen?), could lock a thread.
    try:
        while getattr(context, "meta_type", None) != "Plone Site":
            text = find_menupage_text(context)
            if text is not None:
                return text
            context = context.aq_inner.aq_parent
        return ""
    except Exception, value:
        raise
        return ""

return get_body(object_ or context)
