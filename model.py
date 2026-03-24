"""
Linear Regression Model Module
Class untuk training dan prediction menggunakan Linear Regression algorithm
"""

import numpy as np


class LinearRegression:
    """
    Custom Linear Regression implementation menggunakan Gradient Descent
    
    Attributes:
        learn_r (float): Learning rate untuk gradient descent
        iters (int): Jumlah iterasi training
        weights (np.ndarray): Model weights/coefficients
        bias (float): Model bias/intercept
    """
    
    def __init__(self, learn_r=0.01, iters=14000):
        """
        Inisialisasi Linear Regression model
        
        Args:
            learn_r (float): Learning rate, default=0.01
                            - Semakin besar: training cepat tapi kurang akurat
                            - Semakin kecil: training detail tapi lambat
            iters (int): Jumlah iterasi training, default=14000
                        - Semakin banyak: model semakin akurat (hingga titik tertentu)
        """
        self.learn_r = learn_r
        self.iters = iters
        self.weights = None
        self.bias = None

    def fit(self, x_train, y_train):
        """
        Train model menggunakan training data
        
        Args:
            x_train (np.ndarray atau pd.DataFrame): Training features dengan shape (n_samples, n_features)
            y_train (np.ndarray atau pd.Series): Training target/labels dengan shape (n_samples,)
        
        Returns:
            None (weights dan bias diupdate secara internal)
        """
        # Get dimensi data
        n_samples, n_features = x_train.shape
        
        # Initialize weights dan bias
        self.weights = np.zeros(n_features)
        self.bias = 0

        # Training loop menggunakan Gradient Descent
        for iteration in range(self.iters):
            # Forward pass - hitung prediction
            y_pred = np.dot(x_train, self.weights) + self.bias
            
            # Calculate error
            error = y_pred - y_train
            
            # Calculate gradients menggunakan Mean Squared Error
            dw = (1 / n_samples) * np.dot(x_train.T, error)
            db = (1 / n_samples) * np.sum(error)
            
            # Update weights dan bias menggunakan gradient descent
            self.weights -= self.learn_r * dw
            self.bias -= self.learn_r * db

    def predict(self, x_test):
        """
        Lakukan prediction pada test data
        
        Args:
            x_test (np.ndarray atau pd.DataFrame): Test features dengan shape (n_samples, n_features)
        
        Returns:
            np.ndarray: Prediction hasil dengan shape (n_samples,)
        """
        return np.dot(x_test, self.weights) + self.bias

    def get_parameter(self):
        """
        Ambil trained model parameters
        
        Returns:
            tuple: (weights, bias)
                - weights: np.ndarray dengan shape (n_features,)
                - bias: float
        """
        return self.weights, self.bias

    def score(self, x_test, y_test):
        """
        Hitung R-squared score pada test data
        
        Args:
            x_test: Test features
            y_test: Test target
        
        Returns:
            float: R-squared score (0-1, semakin tinggi semakin baik)
        """
        y_pred = self.predict(x_test)
        ss_res = np.sum((y_test - y_pred) ** 2)
        ss_tot = np.sum((y_test - np.mean(y_test)) ** 2)
        return 1 - (ss_res / ss_tot)
