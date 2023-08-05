Introduction
============

Provides an archetypes validator for file and image fields to only
allow specific content types to be added.

Example
-------

::

    from Products.ContentTypeValidator.validator import ContentTypeValidator
    
      ...
    
    FileField('file',
        validators = (ContentTypeValidator(('audio/mpeg', 'audio/x-mp3', 'audio/x-mpeg', 'audio/mp3',))),
        widget = atapi.FileWidget(
            description = '',
            label=_(u'label_audio', default=u'Audio file'),
            show_content_type = False,),
    ),
    
      ...
