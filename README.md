# Image-Ellipsifier


Image Ellipsifier is a small Python program that scans an image and searches for the largest circular regions that contain all pixels of roughly the same color as each other. The application uses the Python Pillow Imaging Library for image processing and is supports parallelization using the Python Multiprocessing Library. 

To see a simplified example of the inner workings of the program, check out the Jupyter notebook for the project [here](https://github.com/BrianHooper/Image-Ellipsify-Notebook/blob/master/ellipsify-simple.ipynb).

### Examples

The project was inspired by a poster belonging to my girlfriend depicting Buddha made out of small colored circles. I wanted to be able to generate a similar type of image from a photograph or drawing. Some examples of the program output are shown below, along with their input images. 

![Gecko](/Docs/gecko_example.png)

![Cheetah](/Docs/cheetah_example.png)

![Landscape](/Docs/landscape_example.png)

![Chameleon](/Docs/chameleon_example.png)

### Configuration

The program uses a configuration file to input the settings. An example configuration file is given below. 
Multiple filenames can be added to the [FILES] section to process multiple filenames sequentially. Multiple passes can be performed by adding multiple parameters to each setting in the [IMAGE SETTINGS] section, but the length of each setting must match. 

    [FILES]
    images/1.jpg

    [SETTINGS]
    Parse = true
    Draw = true
    LoadPartial = true
    Threads = 4

    [OUTPUT]
    Format = png
    Scale = 1.0

    [IMAGE SETTINGS]
    Thresholds = {5, 15, 25, 50, 100}
    Min_size = {20, 10, 5, 3, 3}
    Max_size = {250, 250, 100, 10, 10}
    Precision = {5, 5, 5, 5, 5}

    [DRAWING]
    Background_Color = (0.2, 0.2, 0.2)
    Outer_Color = 0.5
    Inner_Width = 0.66
    Border_Width = 2
    Border_Color = (0, 0, 0)
    Border_Threshold = 10
    
The program stores a partially-parsed image as a list of points in a text file, allowing the computation to be stopped and resumed, as well as allowing the colors of an input image to be manipulated after the points have already been calculated. 
    
### Best Results

For best results, a high-resolution image should be used. I've found that images smaller than about 2000 pixels wide are too low of a resolution to produce a quality image, and anything over about 4000 pixels wide takes too long to compute (>12 hours runtime). Multiple passes can be used to help with areas of small detail, so that an initial pass can have a precise threshold, but a later pass can essentially fill in any details that have not yet been drawn. 
