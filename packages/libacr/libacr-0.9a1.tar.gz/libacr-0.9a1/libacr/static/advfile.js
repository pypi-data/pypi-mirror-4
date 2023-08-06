function adv_file_remove(container_id, name) {
    var el = document.getElementById(container_id);

    while (el.hasChildNodes()) {
        el.removeChild(el.lastChild);
    }

    var message = document.createTextNode('file removed');
    el.appendChild(message);

    var fileupload = document.createElement('input');
    fileupload.setAttribute('type', 'hidden');
    fileupload.setAttribute('name', name);
    el.appendChild(fileupload);
}

function adv_file_upload(container_id, name) {
    var el = document.getElementById(container_id);

    while (el.hasChildNodes()) {
        el.removeChild(el.lastChild);
    }
    
    var fileupload = document.createElement('input');
    fileupload.setAttribute('type', 'file');
    fileupload.setAttribute('name', name);
    el.appendChild(fileupload);
}