Integration with CKEditor
=========================

Using CKEditor 3.x or higher you have to set the URL of the file manager in your
configure instance.

Assuming you are following this document your URL will be
``MEDIA_URL/C5FILEMANAGER_MEDIA/index.html``, so your configuration might be:

.. code-block:: javascript

    CKEDITOR.editorConfig = function( config )
    {
        // Define changes to default configuration here. For example:
        // config.language = 'it';
        // config.uiColor = '#AADC6E';
        config.filebrowserBrowseUrl = '/static/filemanager/index.html';
        // Other configuration
    };

