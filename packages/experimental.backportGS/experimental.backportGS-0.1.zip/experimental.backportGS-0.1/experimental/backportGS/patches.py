

def registerScript(self, id, expression='', inline=False, enabled=True,
                   cookable=True, compression='safe', cacheable=True,
                   conditionalcomment='', skipCooking=False,
                   authenticated=False, bundle='default'):
    # if we provided "authenticated" and not a conditionalcomment, let's translated
    # the authenticated to a TAL expressions
    if authenticated and not expression:
        expression = "not: portal/portal_membership/isAnonymousUser"
    self._old_registerScript(id, expression=expression, inline=inline, enabled=enabled,
                             cookable=cookable, compression=compression, cacheable=cacheable,
                             conditionalcomment=conditionalcomment, skipCooking=skipCooking)

def registerStylesheet(self, id, expression='', media='screen',
                       rel='stylesheet', title='', rendering='import',
                       enabled=1, cookable=True, compression='safe',
                       cacheable=True, conditionalcomment='',
                       authenticated=False, skipCooking=False,
                       applyPrefix=False, bundle='default'):
    # if we provided "authenticated" and not a conditionalcomment, let's translated
    # the authenticated to a TAL expressions
    if authenticated and not expression:
        expression = "not: portal/portal_membership/isAnonymousUser"
    self._old_registerStylesheet(id, expression=expression, media=media, rel=rel,
                           title=title, rendering=rendering,  enabled=enabled,
                           cookable=cookable, compression=compression, cacheable=cacheable,
                           conditionalcomment=conditionalcomment, skipCooking=skipCooking)
