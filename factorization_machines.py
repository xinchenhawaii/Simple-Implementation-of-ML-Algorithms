import numpy as np
from sklearn.datasets import load_boston
# TO DO: improve performance and classification


def squared_loss(y, pred):
	return np.square(pred - y).mean() / 2

def squared_loss_gradient(y, pred):
	return pred - y

class FactorizationMachines(object):
	def __init__(self):
		self.learning_rate = 0.5
		self.embedding_dim = 1
		self.lmbda = 0.001 # regularization coefficient
		self.reg = 2
		self.eps = 1e-12

	def fit(self, x, y):
		n_data = x.shape[0]
		n_dim = x.shape[1]
		self.w0 = 0
		self.w = np.random.randn(n_dim)
		self.v = np.random.randn(self.embedding_dim, n_dim)

		self.mom_w0, self.cache_w0 = 0, 0
		self.mom_w, self.cache_w = np.zeros(n_dim), np.zeros(n_dim)
		self.mom_v, self.cache_v = np.zeros(self.v.shape), np.zeros(self.v.shape)

		for i in range(5000):
			grad = squared_loss_gradient(y, self.predict(x))
			squares = np.repeat(np.square(x), self.embedding_dim, axis=0).reshape(n_data, -1, n_dim)
			vx = [np.matmul(vkx.reshape(-1,1), xi.reshape(1,-1)) for vkx, xi in zip(x.dot(self.v.T), x)]
			grad_v = grad.T.dot((np.array(vx) - squares).reshape(n_data, -1)).reshape(self.v.shape)
			self.adam(grad.sum(), grad.T.dot(x), grad_v, i+1)
			self.regularization()
			if i % 100 == 0:
				print('loss {}'.format(squared_loss(self.predict(x), y)))

	def sgd(self, grad_w0, grad_w, grad_v):  # use a very small learning rate for sgd, e.g., 1e-14
			self.w0 -= self.learning_rate * grad_w0
			self.w -= self.learning_rate * grad_w
			self.v -= self.learning_rate * grad_v

	def adam(self, grad_w0, grad_w, grad_v, i):
		beta1 = 0.9
		beta2 = 0.999
		alpha = self.learning_rate
		self.mom_w0 = beta1 * self.mom_w0 + (1 - beta1) * grad_w0
		self.cache_w0 = beta2 * self.cache_w0 + (1 - beta2) * np.square(grad_w0)
		self.w0 -= alpha * self.mom_w0 / (1 - beta1**i) / (np.sqrt(self.cache_w0 / (1 - beta2**i)) + self.eps)
		
		self.mom_w = beta1 * self.mom_w + (1 - beta1) * grad_w
		self.cache_w = beta2 * self.cache_w + (1 - beta2) * np.square(grad_w)
		self.w -= alpha * self.mom_w / (1 - beta1**i) / (np.sqrt(self.cache_w / (1 - beta2**i)) + self.eps)

		self.mom_v = beta1 * self.mom_v + (1 - beta1) * grad_v
		self.cache_v = beta2 * self.cache_v + (1 - beta2) * np.square(grad_v)
		self.v -= alpha * self.mom_v / (1 - beta1**i) / (np.sqrt(self.cache_v / (1 - beta2**i)) + self.eps)

	def regularization(self):
		if(self.reg==1):
			self.w0 -= self.lmbda * np.sign(self.w0)
			self.w -= self.lmbda * np.sign(self.w)
			self.v -= self.lmbda * np.sign(self.v)
		elif(self.reg==2):
			self.w0 -= self.lmbda * self.w0
			self.w -= self.lmbda * self.w
			self.v -= self.lmbda * self.v

	def predict(self, x):
		xvt = np.matmul(x, self.v.T)
		return self.w0 + x.dot(self.w) + (np.square(xvt).sum(axis=1) - np.square(x).dot(np.square(self.v).sum(axis=0))) / 2


def main():
	data = load_boston()
	test_ratio = 0.2
	test_split = np.random.uniform(0, 1, len(data.data))
	train_x = data.data[test_split >= test_ratio]
	test_x = data.data[test_split < test_ratio]
	train_y = data.target[test_split >= test_ratio]
	test_y = data.target[test_split < test_ratio]

	fm = FactorizationMachines()
	fm.fit(train_x, train_y)
	print(squared_loss(fm.predict(train_x), train_y))
	print(squared_loss(fm.predict(test_x), test_y))


if __name__ == "__main__":
    main()
