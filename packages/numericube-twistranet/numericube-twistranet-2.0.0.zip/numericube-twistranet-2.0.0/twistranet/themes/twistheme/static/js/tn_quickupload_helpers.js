/**
 *
 * JQuery Helpers for Quick Upload
 *   
 */    

var TwistranetQuickUpload = {};
var lastUploadUrl = '';
var lastUploadPreviewUrl = '';
var lastUploadMiniUrl = '';
var lastUploadThumbUrl = '';
var lastUploadSummaryUrl = '';
var lastUploadLegend = '';
var lastUploadValue = '';  
var scopeValue = '';
var lastUploadType = '';
    
TwistranetQuickUpload.onAfterSelect = function(uploader, domelement, file, id, fillTitles) {
    // if you want to fill some fields before upload
    if (fillTitles)  {
        var labelfiletitle = jq('#uploadify_label_file_title').val();
        var blocFile = uploader._getItemByFileId(id);
        if (typeof id == 'string') id = parseInt(id.replace('qq-upload-handler-iframe',''));
        var formBloc = '<div class="uploadField">';
        formBloc += '<label>' + labelfiletitle + '&nbsp;:&nbsp;</label>';
        formBloc += '<input type="text" class="file_title_field" id="title_' + id + '" name="title" value="" />';
        formBloc += '</div>';
        jq('.qq-upload-cancel', blocFile).after(formBloc);
    }
    TwistranetQuickUpload.showButtons(uploader, domelement);
}

TwistranetQuickUpload.showButtons = function(uploader, domelement) {
    var handler = uploader._handler;
    if (handler._files.length) {
        jq('.uploadifybuttons', jq(domelement).parent()).show();
        return 'ok';
    }
    return false;
}

TwistranetQuickUpload.onDragAndDrop = function() {
    // because we want to allow drag and drop in status update textarea (outside quickupload form)
    // when drag&dropping, we must show the file quickupload fieldset
    // before starting upload
    // so we use some magic here since the inlinefom tabs switcher is not perfect
    // and if the user has started to write in Status Update textarea we must copy the text
    fileformbutton = jq('a#formhandle-File');
    if (fileformbutton.width()) {
        fileformbutton.parents("fieldset").hide();
        jq(''+ fileformbutton.attr('href')).show();
        sutextfield = jq('#form-StatusUpdate textarea:first');
        jq('#form-File textarea:first').val(sutextfield.val());
        sutextfield.val('');
    }
}

TwistranetQuickUpload.sendDataAndUpload = function(uploader, domelement, typeupload) {
    /* regular stuff */
    var handler = uploader._handler;
    var files = handler._files;
    var params = uploader._options.params;
    var missing = 0;
    for ( var id = 0; id < files.length; id++ ) {
        if (files[id]) {
            var fileContainer = jq('.qq-upload-list li', domelement)[id-missing];
            var file_title = '';
            if (fillTitles)  {
                file_title = jq('.file_title_field', fileContainer).val();
            }
            params['title'] = file_title;
            params['typeupload'] = typeupload;
            uploader._queueUpload(id, params);
        }
        // if file is null for any reason jq block is no more here
        else missing++;
    }
}


TwistranetQuickUpload.onAllUploadsComplete = function(){
    showPreview (lastUploadUrl, lastUploadThumbUrl, lastUploadMiniUrl, lastUploadSummaryUrl, lastUploadPreviewUrl, lastUploadLegend, lastUploadType);
    // fix selector value in a form
    if (typeof selector != 'undefined') {
        selector.val(lastUploadValue);
        new_selection = lastUploadValue;
        // reload the publisher panel with last upload value if exists
        if (scopeValue && typeof reloadScope != 'undefined') reloadScope(scopeValue.toString(), lastUploadValue, true, media_type);
    }
    // XXX FIXME > JMG it's not safe
    // in inline forms after upload
    jq('#form-File .tnQuickUpload').remove();
    jq('#form-File #resources-renderer').append(jq('#form-File textarea'));
    jq('#form-File  textarea').show();
    jq('#form-File input[type=submit]').css('visibility', 'visible');

}
TwistranetQuickUpload.clearQueue = function(uploader, domelement) {
    var handler = uploader._handler;
    var files = handler._files;
    for ( var id = 0; id < files.length; id++ ) {
        if (files[id]) {
            handler.cancel(id);
        }
    }
    jq('.qq-upload-list li', domelement).remove();
    jq('.qq-upload-list', domelement).hide();
    handler._files = [];
    if (typeof handler._inputs != 'undefined') handler._inputs = {};
}    
TwistranetQuickUpload.onUploadComplete = function(uploader, domelement, id, fileName, responseJSON) {
    var uploadList = jq('.qq-upload-list', domelement);
    if (responseJSON.success) {        
        window.setTimeout( function() {
            jq(uploader._getItemByFileId(id)).remove();
            // after the last upload, if no errors, reload the page
            var newlist = jq('li', uploadList);
            if (! newlist.length) {
                lastUploadUrl = responseJSON.url;
                lastUploadPreviewUrl = responseJSON.preview_url;
                lastUploadMiniUrl = responseJSON.mini_url;
                lastUploadThumbUrl = responseJSON.thumbnail_url;  
                lastUploadSummaryUrl = responseJSON.summary_url;
                lastUploadType = responseJSON.type;
                lastUploadLegend = responseJSON.legend; 
                lastUploadValue = responseJSON.value;
                scopeValue = responseJSON.scope;
                uploadList.hide();
                if(scopeValue && typeof Panels!='undefined') Panels[scopeValue.toString()] = 'unloaded';
                window.setTimeout( TwistranetQuickUpload.onAllUploadsComplete, 5);
            }       
        }, 50);
    }
    
}

