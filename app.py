from flask import Flask,render_template,request
import pandas as pd
import joblib

gb=joblib.load("gb_trained.pkl")

app=Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict",methods=['POST'])
def predict():
    education_map={
        "High School":0,
        "Associate":1,
        "Bachelor":2,
        "Master":3,
        "Doctorate":4
    }
    home_map={
        "RENT":0,
        "OWN":1,
        "MORTGAGE":2,
        "OTHER":3
    }
    loan_map={
        "PERSONAL":0,
        "EDUCATION":1,
        "MEDICAL":2,
        "VENTURE":3,
        "HOMEIMPROVEMENT":4,
        "DEBTCONSOLIDATION":5
    }
    default_loan={
        "No":0,
        "Yes":1
    }
    education=education_map[request.form['person_education']]
    home=home_map[request.form['person_home_ownership']]
    loan=loan_map[request.form['loan_intent']]
    default=default_loan[request.form['previous_loan_defaults_on_file']]
    data={
        "person_age":float(request.form['person_age']),
        "person_education":education,
        "person_income":float(request.form['person_income']),
        "person_home_ownership":home,
        "loan_amnt":float(request.form['loan_amnt']),
        "loan_intent":loan,
        "loan_int_rate":float(request.form['loan_int_rate']),
        "loan_percent_income":float(request.form['loan_percent_income']),
        "credit_score":float(request.form['credit_score']),
        "previous_loan_defaults_on_file":default

    }
    input_data=pd.DataFrame([data])
    prediction=gb.predict(input_data)[0]
    print("model prediction",prediction)

    if prediction == 1:
        result="loan approved"
    else:
        result="loan not approaved"
    return render_template("index.html",prediction=result)
if __name__=="__main__":
    app.run(debug=True)

