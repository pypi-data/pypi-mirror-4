# -*- coding: utf-8 -*-

from experimental.backportGS import logger


def registerScript(self, id, expression='', inline=False, enabled=True,
                   cookable=True, compression='safe', cacheable=True,
                   conditionalcomment='', skipCooking=False,
                   authenticated=False, bundle='default'):
    # if we provided "authenticated" and not a conditionalcomment, let's translated
    # the authenticated to a TAL expressions
    if authenticated and not expression:
        logger.info('"authenticated" provided; translating it to old-style expression')
        expression = "not: portal/portal_membership/isAnonymousUser"
    elif authenticated and expression:
        logger.warn('"authenticated" provided but also "expression"; please check final configuration')
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
        logger.info('"authenticated" provided; translating it to old-style expression')
        expression = "not: portal/portal_membership/isAnonymousUser"
    elif authenticated and expression:
        logger.warn('"authenticated" provided but also "expression"; please check final configuration')
    self._old_registerStylesheet(id, expression=expression, media=media, rel=rel,
                           title=title, rendering=rendering,  enabled=enabled,
                           cookable=cookable, compression=compression, cacheable=cacheable,
                           conditionalcomment=conditionalcomment, skipCooking=skipCooking)


def _initProperties(self, node):
    obj = self.context
    if node.hasAttribute('i18n:domain'):
        i18n_domain = str(node.getAttribute('i18n:domain'))
        obj._updateProperty('i18n_domain', i18n_domain)
    for child in node.childNodes:
        if child.nodeName != 'property':
            continue
        prop_id = str(child.getAttribute('name'))
        prop_map = obj.propdict().get(prop_id, None)

        # swap icon_expr with old content_icon
        if prop_id == 'icon_expr' and not prop_map:
            logger.info('Found new style "icon_expr"')
            prop_id = 'content_icon'
            prop_map = obj.propdict().get(prop_id, None)
            child.setAttribute('name', 'content_icon')
            if child.firstChild and child.firstChild.data:
                # trying to normalize content_icon
                if child.firstChild.data.find('string:${portal_url}/')>-1:
                    logger.info('Replacing with a backported version of "content_icon"')
                    child.firstChild.replaceWholeText(child.firstChild.data.replace('string:${portal_url}/',''))
                else:
                    logger.warn('Don\'t know hot to fix it; please check final configuration')

        if prop_map is None:
            if child.hasAttribute('type'):
                val = str(child.getAttribute('select_variable'))
                prop_type = str(child.getAttribute('type'))
                obj._setProperty(prop_id, val, prop_type)
                prop_map = obj.propdict().get(prop_id, None)
            else:
                raise ValueError("undefined property '%s'" % prop_id)

        if not 'w' in prop_map.get('mode', 'wd'):
            raise BadRequest('%s cannot be changed' % prop_id)

        new_elements = []
        remove_elements = []
        for sub in child.childNodes:
            if sub.nodeName == 'element':
                value = sub.getAttribute('value').encode(self._encoding)
                if self._convertToBoolean(sub.getAttribute('remove')
                                      or 'False'):
                    remove_elements.append(value)
                    if value in new_elements:
                        new_elements.remove(value)
                else:
                    new_elements.append(value)
                    if value in remove_elements:
                        remove_elements.remove(value)

        if new_elements or prop_map.get('type') == 'multiple selection':
            prop_value = tuple(new_elements) or ()
        elif prop_map.get('type') == 'boolean':
            prop_value = self._convertToBoolean(self._getNodeText(child))
        else:
            # if we pass a *string* to _updateProperty, all other values
            # are converted to the right type
            prop_value = self._getNodeText(child).encode(self._encoding)

        if not self._convertToBoolean(child.getAttribute('purge')
                                      or 'True'):
            # If the purge attribute is False, merge sequences
            prop = obj.getProperty(prop_id)
            if isinstance(prop, (tuple, list)):
                prop_value = (tuple([p for p in prop
                                     if p not in prop_value and 
                                        p not in remove_elements]) +
                              tuple(prop_value))

        obj._updateProperty(prop_id, prop_value)
