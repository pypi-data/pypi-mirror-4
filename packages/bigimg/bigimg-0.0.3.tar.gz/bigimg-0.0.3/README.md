bigimg
======

Easily create big images. With just a lambda expression. 

An image can be seen as a function that maps a real-valued (x, y) coordinate
onto a color. With this in mind, I made bigimg.

```bigimg.py``` allows you to define a canvas width and height, a vector
function which will conduct an element wise map over each element in the
canvas, and an output file. If your function returns a single floating point
value, the resulting image will be gray scale, if it returns a 3-tuple, it will
be color.

## Installation

    $ git clone https://github.com/stephenbalaban/bigimg.git
    $ cd bigimg
    $ sudo pip install -e .

You can also create pseudorandom images with:

```bash
./bigimg 128 128 pseudorandom.png --lambda random
```

This is useful in a variety of contexts.

## Examples 

Check out the example images included. You can pull request a new example image
if you find an especially cool formula. Simply add the code to the example set
below, and place the image in the examples/ folder. 


Only the best images, as determined by me, will be accepted.

### Grayscale

```
bigimg 512 512 examples/1.png --lambda "lambda x, y: 2048. * np.sin(x/32.) + 2048. * np.sin(y/32.)"
```
![Example 1](examples/1.png "lambda x, y: 2048. * np.sin(x/32.) + 2048. * np.sin(y/32.)" )

```
bigimg 512 512 examples/2.png --lambda "lambda x, y: y * np.cos(x/128.)"
```
![Example 2](examples/2.png "lambda x, y: y * np.cos(x/128.)")

```
bigimg 512 512 --lambda random examples/0.png
```
![Example 0](examples/0.png "random")

### Color

```
bigimg 512 512 examples/3.png --lambda "lambda x, y: (x, x, y)"
```
![Example 3](examples/3.png "lambda x, y: (x, x, y)")

```
bigimg 512 512 examples/4.png --lambda "lambda x, y: (x, np.sin(x), np.sin(y))"
```
![Example 4](examples/4.png "lambda x, y: (x, np.sin(x), np.sin(y))")

```
bigimg 1024 1024 examples/5.png --lambda "lambda x, y: (512 * np.cos(y/32.), 512 * np.sin(x/32.), 512 * np.sin(y/32.))"
```
![Example 5](examples/5.png "lambda x, y: (512 * np.cos(y/32.), 512 * np.sin(x/32.), 512 * np.sin(y/32.))")

