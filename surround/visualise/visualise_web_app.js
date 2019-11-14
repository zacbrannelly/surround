function uploadCSV(file, gtLabel, predLabel, probLabel, separator) {
    return new Promise((resolve, reject) => {
        var formData = new FormData();
        formData.append("file", file);
        formData.append("groundTruthLabel", gtLabel);
        formData.append("predictLabel", predLabel);
        formData.append("probabilityLabel", probLabel);
        formData.append("separator", separator);

        var request = new XMLHttpRequest();
        request.onreadystatechange = function() {
            if (request.readyState == 4) {
                if (request.status == 200)
                    resolve(JSON.parse(request.response));
                else
                    reject();
            }
        }
        request.open("POST", "./upload_csv", true);
        request.send(formData);
    });
}

function checkForSession(app) {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function() {
        if (request.readyState == 4 && request.status == 200) {
            response = JSON.parse(request.response);
            // Show metrics, etc.
            app.content.isActive = true;
            app.content.report = response;
        }
    }

    request.open("GET", "./metrics", true);
    request.send();
}

function checkValue(val, def) {
    return val == null || val === "" ? def : val; 
}

var app = new Vue({
    el: "#app",
    data: {
        newModal: {
            isActive: false,
            isLoading: false,
            selectedFile: null,
            truthColumn: null,
            predictColumn: null,
            probabilityColumn: null,
            separator: null,
            hasError: false,
            errorMessage: ""
        },
        content: {
            isActive: false,
            report: {
                confusion_matrix: null,
                classes: null,
                report: null,
                normalized_confusion_matrix: null,
                accuracy_score: null,
                cohen_kappa_score: null
            }
        }
    },
    mounted: function() {
        // Check if we have a session in our cookies already, if so load the metrics again.
        this.$nextTick(function() {
            checkForSession(this);
        });
    },
    methods: {
        onFileQueue: function(event) {
            this.newModal.selectedFile = event.target.files[0];
            event.target.value = null;
        },
        resetNewModal: function() {
            app.newModal = {
                isActive: true,
                isLoading: false,
                selectedFile: null,
                truthColumn: null,
                predictColumn: null,
                probabilityColumn: null,
                separator: null,
                hasError: false,
                errorMessage: ""
            }
        },
        upload: function(event) {
            app.newModal.isLoading = true;

            // Get the values from the input fields or default them if empty
            const gtLabel = checkValue(this.newModal.truthColumn, "ground-truth");
            const predLabel = checkValue(this.newModal.predictColumn, "predict");
            const probLabel = checkValue(this.newModal.probabilityColumn, "confidence");
            const separator = checkValue(this.newModal.separator, ",");

            // Upload the CSV file with the user specified properties
            uploadCSV(app.newModal.selectedFile, gtLabel, predLabel, probLabel, separator)
                .then(response => {
                    // Hide modal
                    app.resetNewModal();
                    app.newModal.isActive = false;

                    // Show metrics, etc.
                    app.content.isActive = true;
                    app.content.report = response;
                },
                () => {
                    // Reset modal and show error
                    app.resetNewModal();
                    app.newModal.hasError = true;
                    app.newModal.errorMessage = "Failed to upload the CSV file! Make sure the file is valid!"
                });
        }
    }
});
