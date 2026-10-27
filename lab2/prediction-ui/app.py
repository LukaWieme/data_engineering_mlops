# importing Flask and other modules
import json
import os
import logging
import requests
from flask import Flask, request, render_template, jsonify

# Flask constructor
app = Flask(__name__)


# A decorator used to tell the application
# which URL is associated function
@app.route('/checkdiabetes', methods=["GET", "POST"])
def check_diabetes():
    if request.method == "GET":
        return render_template("input_form_page.html")

    elif request.method == "POST":
        prediction_input = [
            {
                "Age": float(request.form.get("Age")),  # getting input with name = ntp in HTML form
                "Gender": float(request.form.get("Gender")),  # getting input with name = pgc in HTML form
                "Education": float(request.form.get("Education")),
                "Country": float(request.form.get("Country")),
                "Ethnicity": float(request.form.get("Ethnicity")),
                "Nscore": float(request.form.get("Nscore")),
                "Escore": float(request.form.get("Escore")),
                "Oscore": float(request.form.get("Oscore")),
                "Ascore": float(request.form.get("Ascore")),
                "Cscore": float(request.form.get("Cscore")),
                "Impulsive": float(request.form.get("Impulsive")),
                "SS": float(request.form.get("SS"))
            }
        ]

        app.logger.debug("Prediction input : %s", prediction_input)

        # use requests library to execute the prediction service API by sending an HTTP POST request
        # use an environment variable to find the value of the diabetes prediction API
        # json.dumps() function will convert a subset of Python objects into a json string.
        # json.loads() method can be used to parse a valid JSON string and convert it into a Python Dictionary.
        predictor_api_url = os.environ['PREDICTOR_API']
        res = requests.post(predictor_api_url, json=json.loads(json.dumps(prediction_input)))

        prediction_value = res.json()['result']
        app.logger.info("Prediction Output : %s", prediction_value)

        class_labels = {0: "Never Used",
                        1: "Used over a Decade Ago",
                        2: "Used in Last Decade",
                        3: "Used in Last Year",
                        4: "Used in Last Month",
                        5: "Used in Last Week",
                        6: "Used in Last Day"}

        prediction_label = class_labels.get(int(prediction_value), "Unkown class")

        return render_template("response_page.html",
                               prediction_variable=prediction_label)

    else:
        return jsonify(message="Method Not Allowed"), 405  # The 405 Method Not Allowed should be used to indicate
    # that our app that does not allow the users to perform any other HTTP method (e.g., PUT and  DELETE) for
    # '/checkdiabetes' path


# The code within this conditional block will only run the python file is executed as a
# script. See https://realpython.com/if-name-main-python/
if __name__ == '__main__':
    app.run(port=int(os.environ.get("PORT", 5000)), host='0.0.0.0', debug=True)
