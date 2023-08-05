//----------------------------------------------------------------------------
var asv_files__uploaders = {};
//----------------------------------------------------------------------------
function asv_files__AddFileToList(filelist, data) {
    filelist.append(
        '<tr id="' + data.id + '">' +
            '<td class="filename">' + data.name + '</td>' +
            '<td class="filesize">' + data.size + '</td>' +
            '<td class="filestatus">' + data.status + '</td>' +
            '</tr>'
    );
};
function asv_files__check_submit(a) {
    var t = $(this);
    var EE = false;
    var needUpload = {};
    var ufs = asv_files__uploaders[t.data('FormID')];
    for (var f in ufs) {
        for (var ff in ufs[f].files) {
            if (ufs[f].files[ff].status != plupload.DONE){
                EE = true;
                needUpload[f] = true;
            }
        }
    }
    if (EE) {
        // need upload files, but disable submit form, for protect async upload process
        for (var f in needUpload) {
            ufs[f].start();
        }
        return false;
    } else {
        //no unuploaded files, submit form.
        return true;
    }
};
function asv_files__I_am_filebox__worker(form, Container, CFG) {
    Container.attr('id', CFG.PLUPLOAD_CFG['container']);
    Container.data('CFG',CFG); // do not remove!!!
    var M = CFG['MESSAGES'];
    $('textarea.asv_files_cfg', Container).html($.toJSON(CFG));
    var FileList = $('table.filelist', Container);
    FileList.attr('id', CFG.PLUPLOAD_CFG['file_list']);
    var Browse_BTN = $('a.add', Container);
    Browse_BTN.attr('id', CFG.PLUPLOAD_CFG['browse_button']);
    Browse_BTN.html(M['ADD_FILES']);
    var Upload_BTN = $('a.upload', Container);
    Upload_BTN.attr('id', CFG.PLUPLOAD_CFG['start_uploads_button']);
    Upload_BTN.html(M['UPLOAD_FILES']);
    if (CFG.PROTECT_FILES_ON_SUBMIT)
        form.bind('submit', asv_files__check_submit);
    for (var f in CFG.FILES) {
        asv_files__AddFileToList(FileList, {
            'id': CFG.FILES[f].id,
            'name': CFG.FILES[f].name,
            'size': M.ALREADY,
            'status':M.LOADED
        });
    }
    Container.data('configured', true);
    Container.data('processed', false);
    Container.next().hide(); // hide Loading... picture
    Container.show();

    var uploader = new plupload.Uploader(CFG.PLUPLOAD_CFG);
    asv_files__uploaders[form.data('FormID')].push(uploader);

    uploader.bind('Init', function(up, params) {
        //FileList.html("<div>Current runtime: " + params.runtime + "</div>");
    });

    Upload_BTN.click(function(e) {
        uploader.start();
        e.preventDefault();
    });

    uploader.init();

    uploader.bind('FilesAdded', function(up, files) {
        var store = $('#'+up.settings['file_list']);
        $.each(files, function(i, file) {
            if (store.data('errors__file_'+file.id)) {
                //console.log('file "'+file.name+'" is Forbiden');
            } else {
                //console.log('file "'+file.name+'" is OK');
                asv_files__AddFileToList(FileList, {
                    'id': file.id,
                    'name': file.name,
                    'size': plupload.formatSize(file.size),
                    'status': ''
                });
            }
        });
        up.refresh();
    });

    uploader.bind('UploadProgress', function(up, file) {
        $('td.filestatus', $('#' + file.id)).html(file.percent + '%'); // + file.status);
    });

    uploader.bind('Error', function(up, err) {
        var store = $('#'+up.settings['file_list']);
        if (err.code == plupload.FILE_EXTENSION_ERROR) {
            //console.log('f='+store+'   errors__file_'+err.file.id+'  filename='+err.file.name);
            store.data('errors__file_'+err.file.id, plupload.FILE_EXTENSION_ERROR);
        }
        up.refresh(); // Reposition Flash/Silverlight
    });

    uploader.bind('FileUploaded', function(up, file, resp) {
        var store = $('#'+up.settings['file_list']);
        var cfg = $('#'+up.settings['container']).data('CFG');
        var M = cfg['MESSAGES'];
        //console.log('resp='+$.toJSON(resp))
        if (resp.status && resp.status != 200) {
            $('td.filestatus', $('#' + file.id)).html(M['HTTP_ERROR']);
            return false;
        }
        var msg = 'unkn.status='+file.status;
        //console.log('file='+$.toJSON(file))
        switch  (file.status) {
            case plupload.DONE :
                msg = M['OK'];
                break;
            case plupload.FAILED :
                msg = M['ERROR'];
                break;
        }
        $('td.filestatus', $('#' + file.id)).html(msg); //+' '+ $.toJSON(resp));
    });
};
//----------------------------------------------------------------------------
function asv_files__I_am_filebox__config_me(index,El) {
    var t = $(El);
    // block widget
    if (t.data('configured') || t.data('processed'))
        return false;
    t.data('processed', true);
    //find form
    var form = t.parents('form');
    //configure widget
    var CFG = $.secureEvalJSON( $('textarea.asv_files_cfg', t).html());
    var cmt = $('input[name="csrfmiddlewaretoken"]', form).val();
    form.data('FormID', cmt);
    asv_files__uploaders[cmt] = [];
    if (CFG && cmt &&  CFG.URL_CONFIG) {
        $.post(CFG.URL_CONFIG, {
            'csrfmiddlewaretoken': cmt
        }, function(data){
            asv_files__I_am_filebox__worker(form, t,data);
        }, "json");
    } else {
        //config by initial URL
        var u = $('span.cfgurl', t).html();
        $.post(u, {
            'csrfmiddlewaretoken': cmt
        }, function(data){
            asv_files__I_am_filebox__worker(form, t, data);
        }, "json");
    }
    return true;
}
//----------------------------------------------------------------------------
$(document).ready(function() {
    $('div.asv_files__file_select_widget').each(asv_files__I_am_filebox__config_me);
});
;
