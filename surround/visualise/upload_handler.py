import io
import tornado.web
import pandas as pd
from .visualise_classifier import calculate_classifier_metrics

class UploadHandler(tornado.web.RequestHandler):
    def post(self):
        if 'file' not in self.request.files:
            self.set_status(400)
            self.write("Bad request")
            return

        gt_label = self.get_body_argument("groundTruthLabel", default="ground-truth")
        pred_label = self.get_body_argument("predictLabel", default="predict")
        prob_label = self.get_body_argument("probabilityLabel", default="confidence")
        sep = self.get_body_argument("separator")

        # Get the uploaded file as a file-like object
        uploaded_file = self.request.files['file'][0]
        uploaded_file = io.BytesIO(uploaded_file['body'])

        # Read the uploaded file as CSV
        file_contents = pd.read_csv(uploaded_file, sep=sep, header=0, engine='python')
        file_contents.columns = [i.strip() for i in file_contents.columns]
        file_contents.fillna(value="UNKNOWN", inplace=True)

        if gt_label not in file_contents or pred_label not in file_contents:
            self.set_status(404)
            self.write("Bad request")
            return

        y_true = file_contents[gt_label]
        y_pred = file_contents[pred_label]

        if prob_label in file_contents:
            y_prob = file_contents[prob_label]
            # TODO: Do something with probability column

        result = calculate_classifier_metrics(y_true, y_pred)
        self.write(result)
