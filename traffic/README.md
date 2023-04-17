# Testing Procedures for Traffic.py

In order to test out the model that I made for the CS50AI Traffic project, I started off by creating a neural network that mimicked the example given in the video lecture. This included one convolution layer, one pooling layer, a flattening layer, a dense layer, a dropout layer, then an output layer.

The input the my first Conv2D layer must be the IMG_WIDTH and IMG_HEIGHT variables, while the output of the model(the last dense layer) has a shape of NUM_CATEGORIES, so there is a potential answer for every traffic sign. I then started off by seeing what changes the convolution and pooling layer pairs made to the model, then I test the changes that various Dense layer changes made. My Results are below:


### Conv2D & MaxPooling

(w/ 1 Dense layer @ 128 nodes)

1 pair - 12ms/step 5.5% accurate

2 pair - 11ms/step 90% accurate

3 pair - 10ms/step 87% accurate

Conclusions - performing more opperations can provide beneficial to a point

#### 2 pair

first pair w/ 128 filters - 30ms/step 5.5% accurate

first pair w/ 16 filters - 7ms/step 97% accurate
          w/ 4, 4 filter - 6ms/step 96% accurate
          w/ 6, 6 filter - 7ms/step 95% accurate

first pair w/ 8 filters - 6ms/step 90% accurate

1st&2nd pair w/ 16 filters - 6ms/step 94% accurate

1st pooling size 4, 4 - 5ms/step 79% accurate
2nd pooling size 4, 4 - 7ms/step 91% accurate

only 1 pooling - 19ms/step 98% accurate

Conclusions - Too many filters is bad, but so is too few. Additionally, pooling can reduce accuracy, but dramatically speeds up your model(use in moderation)

### Dense 

(w/ 2 Conv2D and Pooling pairs)

1 pair - 11ms/step 90% accurate (9ms and 95% w/ no dropout & 9ms and 95% w/ .25 dropout)

1 pair w/ 1152 nodes (matching output from conv2d) - 21ms/step 93% accurate 
(Note: this reached accuracy much quicker)

2 pair - 10ms/step 91% accurate

2 pair w/ 1 pair 1152 nodes (matching output from conv2d) - 23ms/step 94% accurate 
(Note: this reached accuracy much quicker)

3 pair - 10ms/step 90% accurate

Conclussions - more hidden layers does not necessarily equate to better accuracy, but does add to time. Additionally, more nodes in a single layer can increase accuracy, but at the expense of time.