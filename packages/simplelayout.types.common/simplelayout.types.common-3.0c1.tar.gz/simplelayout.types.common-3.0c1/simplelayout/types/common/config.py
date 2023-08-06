   
from Products.Archetypes.public import DisplayList
from Products.CMFCore.permissions import setDefaultRoles 

product_globals = globals()



PROJECTNAME = "simplelayout.types.common"
DEPENDENCIES = ('DataGridField',
               )

ADD_PERMISSIONS = { 
    'Page': 'simplelayout.types.common: Add Page',
    'Paragraph': 'simplelayout.types.common: Add Paragraph',
}


# Image sizes
ORIGINAL_SIZE = (900,900)

TAG_SIZES = {
    'thumb' :   (100,100),
    'normal':   (200,200),
    'medium':   (300,300),
    'large' :   (400,400)
    }

SIMPLE_LAYOUT_SIZES ={
    'squarish' :   (175,175),
    'half' :   (260,260),
    'full':   (530,530),
    'thumb'   : (128, 128),
    'micro': (64,64),
    'mini'    : (200, 200),        
    'no-image':   (0,0),             
}
    
TAG_NAMES = DisplayList((lambda l: (l.sort(), l.reverse(), l)[2])
                        ([(k, '%d x %d pixels' % v) for k, v in TAG_SIZES.items()]))


