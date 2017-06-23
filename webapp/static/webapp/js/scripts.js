'use strict';

function overlay() {
    let element = document.getElementById("overlay");
    element.style.visibility = (element.style.visibility == "visible") ? "hidden" : "visible";
}

function AddPopUp(element) {
    $.get(element.href, function(data, status) {
        $('#overlay').empty().append($.parseHTML(data));
        overlay();
    });
}