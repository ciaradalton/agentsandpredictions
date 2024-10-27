import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM

import warnings
warnings.filterwarnings("ignore")


class PricePredictions:

    def __init__(self):
        self.technology_stocks = ["AAPL", "AMD", "NVDA", "CSCO", "EA", "GOOG", "MSFT", "INTC", "PYPL"]
        self.crypto_assets = ["BTC", "ETH", "DOGE"]
        self.prediction_timeframes = [7, 30, 90, 180]
        self.confidence_level = 0.95

    def load_data(self, asset, start_date, end_date):
        data = yf.download(asset, start=start_date, end=end_date)
        if data.empty:
            raise ValueError(f"No data found for {asset}")
        return data

    def process_data(self, data, prediction_timeframe):
        data_scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = data_scaler.fit_transform(data['Adj Close'].values.reshape(-1, 1))

        x_train = []
        y_train = []

        for x in range(prediction_timeframe, len(scaled_data)):
            x_train.append(scaled_data[x - prediction_timeframe:x, 0])
            y_train.append(scaled_data[x, 0])

        x_train, y_train = np.array(x_train), np.array(y_train)
        x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
        return x_train, y_train, data_scaler

    def build_model(self, input_shape):
        model = Sequential([
            LSTM(units=50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(units=50, return_sequences=True),
            Dropout(0.2),
            LSTM(units=50),
            Dropout(0.2),
            Dense(units=1)
        ])

        model.compile(optimizer="adam", loss="mean_squared_error")

        return model

    def calculate_conf_interval(self, price_predictions, real_prices):
        errors = np.array(price_predictions) - np.array(real_prices)
        mean_error = np.mean(errors)
        std_dev = np.std(errors)
        interval = std_dev * self.confidence_level
        lower_bound = price_predictions - interval
        upper_bound = price_predictions + interval
        return lower_bound, upper_bound

    def accuracy_tracker(self, price_predictions, real_prices):
        mean_abs_err = mean_absolute_error(real_prices, price_predictions)
        root_mean_sqr_dev = np.sqrt(mean_squared_error(real_prices, price_predictions))

        prediction_accuracy = 100 - np.mean(np.abs((real_prices - price_predictions) / real_prices)) * 100
        return {
            "Mean Absolute Error (MAE)": mean_abs_err,
            "Root Mean Squared Deviation (RMSD)": root_mean_sqr_dev,
            "Prediction Accuracy": prediction_accuracy
        }

    def predictions(self, asset, prediction_timeframe=30):
        end_date = dt.datetime.today()
        start_date = end_date - dt.timedelta(days=365 * 3)

        data = self.load_data(asset, start_date, end_date)
        if data is None:
            return None

        x_train, y_train, scaler = self.process_data(data, prediction_timeframe)

        model = self.build_model((x_train.shape[1], 1))
        model.fit(x_train, y_train, epochs=25, batch_size=30)

        final = x_train[-1:]
        future_predictions = []

        for _ in range(prediction_timeframe):
            next_prediction = model.predict(final)
            future_predictions.append(next_prediction[0, 0])
            final = np.roll(final, -1)
            final[0, -1, 0] = next_prediction

        future_predictions = scaler.inverse_transform(np.array(future_predictions).reshape(-1, 1))

        last_date = data.index[-1]
        future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=prediction_timeframe, freq="B")

        return {
            "Predictions": future_predictions,
            "Dates": future_dates
        }

    def plot_prices(self, asset, past_data, future_dates, predictions):
        past_prices = past_data["Adj Close"].values
        past_dates = past_data.index


        plt.plot(past_dates, past_prices, label="Past Data", color="blue")


        plt.plot(future_dates, predictions, label="Predictions", color="green", linestyle="--")


        last_prices = past_prices[-len(predictions):]

        lower_bound, upper_bound = self.calculate_conf_interval(predictions.flatten(), last_prices)


        plt.fill_between(future_dates, lower_bound, upper_bound, color="red", alpha=0.2, label="Confidence Interval")


        accuracy = self.accuracy_tracker(predictions.flatten(), last_prices)

        plt.text(0.02, 0.98,
                 f"MAE: {accuracy['Mean Absolute Error (MAE)']:.2f}\n"
                 f"RMSD: {accuracy['Root Mean Squared Deviation (RMSD)']:.2f}\n"
                 f"Accuracy: {accuracy['Prediction Accuracy']:.2f}%",
                 transform=plt.gca().transAxes,
                 bbox=dict(facecolor='white', alpha=0.8),
                 verticalalignment='top')

        plt.title(f'{asset} Price Prediction ({len(predictions)} days)', fontsize=16)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Price', fontsize=12)
        plt.legend(loc='lower right')
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()

        return plt.gcf()


predictor = PricePredictions()
asset = "AAPL"
timeframe = 90


results = predictor.predictions(asset, timeframe)


past_data = predictor.load_data(asset, dt.datetime.today() - dt.timedelta(days=365 * 3), dt.datetime.today())
plt.figure()
predictor.plot_prices(asset, past_data, results['Dates'], results['Predictions'])

plt.show()












