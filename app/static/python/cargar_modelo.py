import tensorflow as tf
import pandas as pd
import sys

from tensorflow import keras
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder

#data=pd.read_csv("..\\CIDDS-001\\traffic\\ExternalServer\\CIDDS-001-external-week1.csv")
data=pd.read_csv(sys.argv[1])

modelo = keras.models.load_model('./static/python/modelo_entrenado3.keras')

X = data.drop('class', axis=1)

le = LabelEncoder()
for col in X.select_dtypes(include=['object']):
    X[col] = le.fit_transform(X[col])

scaler = StandardScaler()
X[X.select_dtypes(include=['float64']).columns] = scaler.fit_transform(X.select_dtypes(include=['float64']))

results = modelo.predict(X)



