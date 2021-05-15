import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

import pickle


def preprocess(df: pd.DataFrame):
    df.dropna(inplace=True)
    df['kast'] = df['kast'].map(lambda x: float(x.strip('%')) / 100.0)

    X = np.array(df[['dpr', 'kast', 'impact', 'adr', 'kpr']])
    y = np.array(df[['rating']])
    return (X, y)

def save(model):
    with open('model.pkl', 'wb') as f:
        pickle.dump(model, f)

def train(df: pd.DataFrame):
    X, y = preprocess(df)
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0, test_size=0.3)

    model = LinearRegression()

    reg = model.fit(X_train, y_train)
    reg.score(X_test, y_test)

    y_pred = reg.predict(X_test)

    #print(f'Coefficients: {reg.coef_}')
    print(f"Train score : {reg.score(X_train,y_train)}")
    print(f"Validation score : {reg.score(X_test,y_test)}")
    print(f'R2 score:{r2_score(y_test, y_pred)}')
    print(f'RMSE:{mean_squared_error(y_test, y_pred, squared=False)}')
    print(f'MAE:{mean_absolute_error(y_test, y_pred)}')

    return model 

if __name__ == '__main__':
    dfstats = pd.read_csv('stats.csv')
    print(dfstats.head())

    model = train(dfstats)
    save(model)
