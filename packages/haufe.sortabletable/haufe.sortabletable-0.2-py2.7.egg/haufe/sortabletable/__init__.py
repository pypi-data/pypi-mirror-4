
import os
from Products.CMFCore.DirectoryView import registerDirectory

package_home = os.path.dirname(__file__)
registerDirectory('skins', globals())


def initialize(context):
    pass
