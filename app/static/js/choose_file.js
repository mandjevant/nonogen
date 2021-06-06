window.uploading = function() {
	const input_element = document.getElementById("image");
	const label_element = document.getElementById("file_label");
	if (input_element.value === "") {
		label_element.innerHTML = "Choose file ...";
	} else {
		const theSplit = input_element.value.split("\\");
		label_element.innerHTML = theSplit[theSplit.length - 1];
	}
};
