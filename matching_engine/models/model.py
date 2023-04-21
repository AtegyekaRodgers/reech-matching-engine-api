# Importing the libraries
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import pickle
import numpy as np
from flask import Flask, request, jsonify

import requests
import json

'''
This is in-progress and not yet being used anywhere
Developing the RL model
Overview:
Transformer:
    takes as input:
        user information
        job ad information
    returns:
        score
    Loss function:
        Reward function (based off of user interactions with job ad)
    Optimisation algorithm:
        Dyna

References
https://towardsdatascience.com/deploy-a-machine-learning-model-using-flask-da580f84e60c

'''


app = Flask(__name__)


def instantiate_model():
    """
    This isn't set up yet at all, needs to completely overhauled
    :return: None
    """
    # Importing the dataset
    dataset = pd.read_csv('Salary_Data.csv')
    X = dataset.iloc[:, :-1].values
    y = dataset.iloc[:, 1].values
    # Splitting the dataset into the Training set and Test set
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 1/3, random_state = 0)
    # Fitting Simple Linear Regression to the Training set
    regressor = LinearRegression()
    regressor.fit(X_train, y_train)
    # Predicting the Test set results
    y_pred = regressor.predict(X_test)
    # Saving model to disk
    pickle.dump(regressor, open('model.pkl','wb'))
    # Loading model to compare the results
    model = pickle.load(open('model.pkl','rb'))
    print(model.predict([[1.8]]))


model = pickle.load(open('model.pkl','rb'))


@app.route('/api',methods=['POST'])
def predict():
    # Get the data from the POST request.
    data = request.get_json(force=True)
    # Make prediction using model loaded from disk as per the data.
    prediction = model.predict([[np.array(data['exp'])]])
    # Take the first value of prediction
    output = prediction[0]
    return jsonify(output)


if __name__ == '__main__':
    app.run(port=5000, debug=True)