import numpy as np
np.random.seed(444)

from keras.models import Sequential
from keras.layers.core import Dense
from keras.optimizers import SGD

x = np.array([
    [0, 0],
    [1, 0],
    [0, 1],
    [1, 1],
])

y = np.array([
    [0], [1], [1], [0]
])

model = Sequential()
model.add(Dense(2, input_dim=2, activation="sigmoid"))
model.add(Dense(1, activation='sigmoid'))

sgd = SGD(lr=.1)

model.compile(
    loss="mean_squared_error",
    optimizer=sgd,
    metrics=["accuracy"]
)

model.fit(x, y, batch_size=1, epochs=5000)

if __name__ == "__main__":
    print(model.predict(x))