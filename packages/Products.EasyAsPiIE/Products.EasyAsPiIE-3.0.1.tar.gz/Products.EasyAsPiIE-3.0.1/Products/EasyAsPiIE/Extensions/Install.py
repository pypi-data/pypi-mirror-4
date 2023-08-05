from OFS.Folder import manage_addFolder
from Products.CMFCore.utils import getToolByName
from Products.ExternalMethod.ExternalMethod import manage_addExternalMethod

def _skinsTool(portal):
    return getToolByName(portal, 'portal_skins')

def install(portal):
    setup_tool = getToolByName(portal, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile('profile-Products.EasyAsPiIE:default')
    return "Ran all import steps."

def uninstall(portal):
    setup_tool = getToolByName(portal, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile('profile-Products.EasyAsPiIE:uninstall')
    # Remove layers, since GenericSetup doesn't support doing it through a profile yet:
    deleteLayers(_skinsTool(portal), ['EasyAsPiIE'])
    return "Ran all uninstall steps."
    
""" took below from WebLionLibrary """

"""Utility functions for manipulating portal_skins. portal_skins' native API is cumbersome for some common tasks; these wrappers make them easy."""


def deleteLayers(skinsTool, layersToDelete):
    """Remove each of the layers in `layersToDelete` from all skins.
    
    (We check them all, in case the user manually inserted it into some.)
    
    Pass getToolByName(portal, 'portal_skins') for `skinsTool`.
    
    """
    # Thanks to SteveM of PloneFormGen for a good example.
    for skinName in skinsTool.getSkinSelections():
        layers = [x.strip() for x in skinsTool.getSkinPath(skinName).split(',')]
        try:
            for curLayer in layersToDelete:
                layers.remove(curLayer)
        except ValueError:  # thrown if a layer ain't in there
            pass
        skinsTool.addSkinSelection(skinName, ','.join(layers))  # more like "set" than "add"