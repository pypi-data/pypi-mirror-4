""" EEA Relations override default widget for ATContentTypes relatedItems
"""
def override(context):
    """ Zope 2 setup """


    from eea.relations.widget.referencewidget import EEAReferenceBrowserWidget
    from Products.ATContentTypes import ATCTMessageFactory as _

    from Products.ATContentTypes import content as atcontent
    from plone.app.blob import content as blobcontent

    widget = EEAReferenceBrowserWidget(
        label = _(u'Related Items'),
        description='',
        visible = {'edit' : 'visible', 'view' : 'invisible' },
        i18n_domain="plone"
    )


    # Event
    atcontent.event.ATEvent.schema['relatedItems'].widget = widget

    # News Item
    atcontent.newsitem.ATNewsItem.schema['relatedItems'].widget = widget

    # File
    atcontent.file.ATFile.schema['relatedItems'].widget = widget

    # Image
    atcontent.image.ATImage.schema['relatedItems'].widget = widget

    # Link
    atcontent.link.ATLink.schema['relatedItems'].widget = widget

    # Topic
    atcontent.topic.ATTopic.schema['relatedItems'].widget = widget

    # Document
    atcontent.document.ATDocument.schema['relatedItems'].widget = widget

    # Folder
    atcontent.folder.ATFolder.schema['relatedItems'].widget = widget

    # Blob
    blobcontent.ATBlob.schema['relatedItems'].widget = widget
