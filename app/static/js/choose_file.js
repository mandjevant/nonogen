window.uploading = function() {
	const inputElement = document.getElementById("image");
	const labelElement = document.getElementById("file_label");
	if (inputElement.value === "") {
		labelElement.innerHTML = "Choose file ...";
	} else {
		const theSplit = inputElement.value.split("\\");
		labelElement.innerHTML = theSplit[theSplit.length - 1];
	}
};
