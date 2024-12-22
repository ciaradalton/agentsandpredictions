from datetime import datetime
from typing import Dict, List, Union
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from concurrent.futures import ThreadPoolExecutor
from sklearn.ensemble import RandomForestRegressor 

import warnings
warnings.filterwarnings("ignore")


class PricePredictions:
    def __init__(self, database):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.db = database
        self.scalers = {}
        self.models = {}
        
      
        self.supported_stocks = [
            'aapl', 'amd', 'googl', 'ibm', 'intc',
            'meta', 'msft', 'nvda', 'orcl', 'tsla'
        ]
        self.supported_crypto = ['bitcoin', 'dogecoin', 'ethereum']
        self.supported_assets = self.supported_stocks + self.supported_crypto
        
       
        self._initialize_models()

    def _initialize_models(self):
        """Create prediction models for each asset"""
        try:
            for asset in self.supported_assets:
                self.models[asset] = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42,
                    n_jobs=-1
                )
                self.scalers[asset] = MinMaxScaler()
            self.logger.info("Models initialized successfully")
        except Exception as e:
            self.logger.error(f"Model initialization error: {str(e)}")
            raise

    def _get_historical_data(self, asset: str) -> pd.DataFrame:
        """Retrieve historical data from database"""
        try:
            collection = self.db[asset]['historical_data']['daily']
            
            if asset in self.supported_stocks:
                return self._format_stock_data(collection)
            return self._format_crypto_data(collection)
                
        except Exception as e:
            self.logger.error(f"Data retrieval error for {asset}: {str(e)}")
            raise

    def _format_stock_data(self, collection) -> pd.DataFrame:
        """Format stock data"""
        data = {
            'date': collection['dates'],
            'open': collection['opens'],
            'high': collection['highs'],
            'low': collection['lows'],
            'close': collection['closes'],
            'volume': collection['volumes']
        }
        
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'], unit='ms')
        df.set_index('date', inplace=True)
        return df

    def _format_crypto_data(self, collection) -> pd.DataFrame:
        """Format crypto data"""
        current_data = collection.parent.parent.find_one()
        
        df = pd.DataFrame({
            'date': collection['dates'],
            'close': collection['closes'],
            'volume': current_data.get('volume_24h', 0),
            'market_cap': current_data.get('market_cap', 0)
        })
        
        df['date'] = pd.to_datetime(df['date'], unit='ms')
        df.set_index('date', inplace=True)
        return df

    def _prepare_features(self, data: pd.DataFrame, asset: str) -> np.array:
        """Prepare features for prediction"""
        df = data.copy()
        
        
        df['MA20'] = df['close'].rolling(window=20).mean()
        df['RSI'] = self._calculate_rsi(df['close'])
        
        if asset in self.supported_stocks:
            features = df[['open', 'high', 'low', 'close', 'volume', 'MA20', 'RSI']]
        else:
            df['volume_ma'] = df['volume'].rolling(window=7).mean()
            features = df[['close', 'volume', 'market_cap', 'MA20', 'RSI', 'volume_ma']]
        
        features = features.fillna(method='ffill')
        return self.scalers[asset].fit_transform(features)

    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def predict(self, assets: Union[str, List[str]]) -> Dict:
        """Generate predictions"""
        try:
            if isinstance(assets, str):
                return self._predict_single(assets)
            elif isinstance(assets, list):
                return {asset: self._predict_single(asset) for asset in assets}
            else:
                raise ValueError("Assets must be a string or list of strings")
        except Exception as e:
            self.logger.error(f"Prediction error: {str(e)}")
            return {"error": str(e)}

    def _predict_single(self, asset: str) -> Dict:
        """Generate prediction for a single asset"""
        try:
            historical_data = self._get_historical_data(asset)
            features = self._prepare_features(historical_data, asset)
            
            model = self.models[asset]
            prediction = model.predict(features[-1:, :])[0]
            
            current_price = historical_data['close'].iloc[-1]
            
            return {
                "asset": asset,
                "current_price": float(current_price),
                "predicted_price": float(prediction),
                "timestamp": datetime.now().isoformat(),
                "change_percent": ((prediction - current_price) / current_price) * 100
            }
        except Exception as e:
            self.logger.error(f"Error predicting {asset}: {str(e)}")
            return {"asset": asset, "error": str(e)}

    def train_model(self, asset: str) -> bool:
        """Train model for specific asset"""
        try:
            historical_data = self._get_historical_data(asset)
            features = self._prepare_features(historical_data, asset)
            
         
            train_size = int(len(features) * 0.8)
            X_train = features[:train_size]
            y_train = historical_data['close'].iloc[:train_size]
            
            self.models[asset].fit(X_train, y_train)
            self.logger.info(f"Model trained successfully for {asset}")
            return True
        except Exception as e:
            self.logger.error(f"Training error for {asset}: {str(e)}")
            return False
