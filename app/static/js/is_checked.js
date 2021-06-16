$(function() {
    $(":checkbox[class='boolean_input']").click( function () {
        let element = document.getElementsByClassName("boolean_input")[0];
        if ($(this).is(":checked")) {
            element.style.backgroundColor="#1d72b7";
            element.style.border="None";
        }
        else {
            element.style.backgroundColor="#eee";
            element.style.border="1px solid #2f86ce";
        }
    });
});
