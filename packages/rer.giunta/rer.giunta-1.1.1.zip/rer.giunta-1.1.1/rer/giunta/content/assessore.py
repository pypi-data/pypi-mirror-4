# -*- coding: utf-8 -*-
"""Definition of the Assessore content type
"""
from Products.ATContentTypes.content import schemata, folder
from Products.ATContentTypes.content.base import registerATCT
from Products.Archetypes import atapi
from rer.giunta import giuntaMessageFactory as _
from rer.giunta.config import PROJECTNAME
from rer.giunta.interfaces import IRERAssessore
from zope.interface import implements
from Products.validation.config import validation
from Products.validation.interfaces import ivalidator
from Products.validation.validators.SupplValidators import MaxSizeValidator
from Products.validation import V_REQUIRED

RERAssessoreSchema = folder.ATFolderSchema.copy() + atapi.Schema((
    
    atapi.StringField('position',
                required=True,
                widget=atapi.StringWidget(label=_(u'rer_giunta_position', default=u'Position'),
                                    description=_(u'rer_giunta_position_help', default=u"Insert the position of this alderman"),
                                    )
               ),
   
    atapi.TextField('referenceInfos',
              searchable=True,
              storage = atapi.AnnotationStorage(migrate=True),
              validators = ('isTidyHtmlWithCleanup',),
              default_output_type = 'text/x-html-safe',
              widget = atapi.RichWidget(
                        label = _('rer_giunta_referenceinfos',default='References'),
                        description=_('rer_giunta_referenceinfos_help',default=u''),
                        rows = 25),
    ),
    atapi.TextField('biography',
              searchable=True,
              storage = atapi.AnnotationStorage(migrate=True),
              validators = ('isTidyHtmlWithCleanup',),
              default_output_type = 'text/x-html-safe',
              widget = atapi.RichWidget(
                        label = _('rer_giunta_biography',default='Biography'),
                        description=_('rer_giunta_biography_help',default=u''),
                        rows = 25),
    ),
    atapi.StringField('delegations',
                      widget=atapi.TextAreaWidget(label=_(u'rer_giunta_delegations', default=u'Delegations'),
                                    description=_(u'rer_giunta_delegation_help', default=u"Insert the delegations of this alderman"),
                                    )
        ),
    
    atapi.TextField('delegationsDescription',
              searchable=True,
              storage = atapi.AnnotationStorage(migrate=True),
              validators = ('isTidyHtmlWithCleanup',),
              default_output_type = 'text/x-html-safe',
              widget = atapi.RichWidget(
                        label = _('rer_giunta_delegationsdescription',default='Delegations description'),
                        description=_('rer_giunta_delegationsdescriptions_help',default=u''),
                        rows = 25),
    ),
    
    atapi.ImageField('imageDetail',
            widget=atapi.ImageWidget(
                label=_(u'rer_giunta_imagedetail', default=u'Alderman image'),
                description=_(u'rer_giunta_imagedetail_help', default=u"Insert an image for the detail of this alderman"),
            ),
            storage=atapi.AttributeStorage(),
            max_size=(768,768),
            sizes= {'large'   : (768, 768),
                    'preview' : (400, 400),
                    'mini'    : (200, 200),
                    'thumb'   : (128, 128),
                    'tile'    :  (64, 64),
                    'icon'    :  (32, 32),
                    'listing' :  (16, 16),
                      },
            validators = (('isNonEmptyFile', V_REQUIRED)),
            ),
            
    atapi.ImageField('imageCollection',
            widget=atapi.ImageWidget(
                label=_(u'rer_giunta_imagecollection', default=u'Image for collection of aldermans'),
                description=_(u'rer_giunta_imagecollection_help', default=u"Insert an image for the collection view of aldermans"),
            ),
            storage=atapi.AttributeStorage(),
            max_size=(768,768),
            sizes= {'large'   : (768, 768),
                    'preview' : (400, 400),
                    'mini'    : (200, 200),
                    'thumb'   : (128, 128),
                    'tile'    :  (64, 64),
                    'icon'    :  (32, 32),
                    'listing' :  (16, 16),
                      },
            validators = (('isNonEmptyFile', V_REQUIRED)),
            ),
))

RERAssessoreSchema['title'].storage = atapi.AnnotationStorage()
RERAssessoreSchema['title'].widget.label = _('rer_giunta_nomecognome',
                                             default='Fullname')
RERAssessoreSchema['title'].widget.description = _('rer_giunta_nomecognome_help',
                                             default='Insert the fullname of this alderman')
RERAssessoreSchema['description'].storage = atapi.AnnotationStorage()
RERAssessoreSchema['description'].widget.visible = {'edit': 'hidden', 'view': 'hidden'}

schemata.finalizeATCTSchema(RERAssessoreSchema, moveDiscussion=False)

class RERAssessore(folder.ATFolder):
    """Folder for RERAssessore"""
    implements(IRERAssessore)
    meta_type = "RERAssessore"
    schema = RERAssessoreSchema
    
registerATCT(RERAssessore, PROJECTNAME)
