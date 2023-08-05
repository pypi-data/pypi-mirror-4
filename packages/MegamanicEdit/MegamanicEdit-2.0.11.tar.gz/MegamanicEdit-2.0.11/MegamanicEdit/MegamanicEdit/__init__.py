
import ArchetypesHack

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    pass

from AccessControl import allow_class, allow_module
allow_module('MegamanicEdit.MegamanicEdit.FakeRequest')

import monkey_patches
