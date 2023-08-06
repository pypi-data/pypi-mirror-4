import numpy as np
from likelihood import likelihood

class Gaussian(likelihood):
    def __init__(self,data,variance=1.,normalize=False):
        self.is_heteroscedastic = False
        self.Nparams = 1
        self.Z = 0. # a correction factor which accounts for the approximation made
        N, self.D = data.shape

        #normaliztion
        if normalize:
            self._mean = data.mean(0)[None,:]
            self._std = data.std(0)[None,:]
        else:
            self._mean = np.zeros((1,self.D))
            self._std = np.ones((1,self.D))

        self.set_data(data)

        self._set_params(np.asarray(variance))

    def set_data(self,data):
        self.data = data
        self.N,D = data.shape
        assert D == self.D
        self.Y = (self.data - self._mean)/self._std
        if D > self.N:
            self.YYT = np.dot(self.Y,self.Y.T)
            self.trYYT = np.trace(self.YYT)
        else:
            self.YYT = None
            self.trYYT = None

    def _get_params(self):
        return np.asarray(self._variance)

    def _get_param_names(self):
        return ["noise_variance"]

    def _set_params(self,x):
        self._variance = float(x)
        self.covariance_matrix = np.eye(self.N)*self._variance
        self.precision = 1./self._variance

    def predictive_values(self,mu,var):
        """
        Un-normalize the prediction and add the likelihood variance, then return the 5%, 95% interval
        """
        mean = mu*self._std + self._mean
        true_var = (var + self._variance)*self._std**2
        _5pc = mean + - 2.*np.sqrt(true_var)
        _95pc = mean + 2.*np.sqrt(true_var)
        return mean, _5pc, _95pc

    def fit_full(self):
        """
        No approximations needed
        """
        pass

    def _gradients(self,partial):
        return np.sum(partial)
