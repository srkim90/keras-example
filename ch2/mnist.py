# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : mnist.py
  Release  : 1
  Date     : 2020-02-02
 
  Description : Stock Simulator Main module
 
  Notes :
  ===================
  History
  ===================
  2020/02/02  created by Kim, Seongrae
'''


# common package import
import os
import json
import numpy as np
#from PIL import Image, ImageDraw
import PIL
from time import *
from PIL import ImageDraw
from tkinter import *

# keras package import
from keras.datasets import mnist
from keras import models
from keras import layers
from keras.utils import to_categorical

# tensorflow package import

try:
    from tensorflow.python.util import module_wrapper as deprecation
except ImportError:
    from tensorflow.python.util import deprecation_wrapper as deprecation
deprecation._PER_MODULE_WARNING_LIMIT = 0
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 


LINE80="================================================================================"
line80="--------------------------------------------------------------------------------"

class MnistDataSet:
    def __init__(self, n_train_set=60000, n_test_set=10000):
        self.n_test_set     = n_test_set
        self.n_train_set    = n_train_set

        mnist_dataset = self.__mnist_loads()
        if mnist_dataset == None:
            mnist_dataset = self.__mnist_download()

        self.train_images   = mnist_dataset["train-images"]
        self.train_labels   = mnist_dataset["train-labels"]
        self.test_images    = mnist_dataset["test-images"]
        self.test_labels    = mnist_dataset["test-labels"]

        #self.__print_image_to_console(self.train_images[0])
        #sleep(999)
        self.network        = None

    def do_train(self):
        self.network = models.Sequential()
        self.network.add(layers.Dense(512, activation='relu', input_shape=(28 * 28,)))
        self.network.add(layers.Dense(10, activation='softmax'))

        self.network.compile(optimizer='rmsprop',
            loss='categorical_crossentropy',
            metrics=['accuracy'])

        self.network.fit(self.train_images, self.train_labels, epochs=30, batch_size=128)

    def do_evaluation(self):
        if self.network == None:
            return None

        test_loss, test_acc = self.network.evaluate(self.test_images, self.test_labels)

        return test_loss, test_acc 

    def get_image_input(self):
        window = None 
        canvas = None 
        frame  = None
        self.old_x, self.old_y = None,None
        
        N_MULTI = 4
        CANVAS_WIDTH    = 28 * N_MULTI
        CANVAS_HEIGHT   = 28 * N_MULTI

        def mouseMove(event):
            if self.old_x != None and self.old_y != None:
                #canvas.create_line(self.old_x, self.old_y, event.x, event.y, fill = "black", width=N_MULTI*2)
                #self.draw.line([(self.old_x, self.old_y), (event.x, event.y)], fill=(255,), width=N_MULTI*2)
                pass
            else:
                canvas.delete("all")
                self.image_out = PIL.Image.new("L", (CANVAS_WIDTH, CANVAS_HEIGHT), (0,))
                self.draw      = ImageDraw.Draw(self.image_out)
            canvas.create_oval(event.x-N_MULTI, event.y-N_MULTI, event.x+N_MULTI, event.y+N_MULTI, fill = "black")
            self.draw.ellipse([(event.x-N_MULTI, event.y-N_MULTI), (event.x+N_MULTI, event.y+N_MULTI)], fill=(255,))

            self.old_x = event.x
            self.old_y = event.y

        def buttonSubmit():
            self.image_out = self.image_out.resize((28, 28), resample=PIL.Image.LANCZOS)
            np_image = np.array(self.image_out)
            np_image = np_image.reshape((1, 28 * 28,))

            np_image = np_image.astype('float32') / 255
            self.__print_image_to_console(np_image)
            result = self.network.predict(np_image)
            detectd_value = np.argmax(result[0])

            self.old_x, self.old_y = None,None
            canvas.create_text(25, 5, text="[%d]" % detectd_value)
            
            


        def buttonClear():
            canvas.delete("all")
            self.old_x, self.old_y = None,None

        window = Tk() 
        window.title("input number") 
        frame  = Frame(window)
        frame.pack()

        canvas = Canvas(window, height = CANVAS_HEIGHT, width = CANVAS_WIDTH, background = "white") 
        canvas.bind("<B1-Motion>", mouseMove)
        canvas.pack() 

        btDoTest = Button(frame, text="submit", command=buttonSubmit)
        btDoTest.pack()
        btDoClear = Button(frame, text="clear", command=buttonClear)
        btDoClear.pack()

        window.mainloop() 

    def __print_image_to_console(self, np_image):
        print("\n%s" % (LINE80))
        np_image = np_image.reshape((28, 28,))
        for item in np_image:
            line = ""
            for at in item:
                line += "%-3d, " % (int(at * 256.0),)
            print("%s\n" % line)

    def __get_datafile_info(self):
        datafile_path    = "/tmp/keras-example/mnist"
        json_file_name   = datafile_path + "/mnist_rawdata.json"  
        train_image_path = datafile_path + "/train_images"
        test_image_path  = datafile_path + "/test_images"
        check_path       = ""
        image_paths      = [train_image_path, test_image_path]
        for item in datafile_path[1:].split("/"):
            check_path += "/" + item
            if not os.path.exists(check_path):
                os.makedirs(check_path)

        for item in image_paths:
            if not os.path.exists(item):
                os.makedirs(item)

        path_dict = {
            "datafile-path"     : datafile_path,
            "json-file-name"    : json_file_name,
            "train-image-path"  : train_image_path,
            "test-image-path"   : test_image_path,
        }

        return path_dict

    def __mnist_download(self):
        mnist_dataset = mnist.load_data()

        (train_images, train_labels), (test_images, test_labels) = mnist_dataset

        train_images = train_images.tolist()
        train_labels = train_labels.tolist()

        test_images  = test_images.tolist()
        test_labels  = test_labels.tolist()

        mnist_dict   = {
            "train-images"  : train_images,
            "train-labels"  : train_labels,
            "test-images"   : test_images,
            "test-labels"   : test_labels,
        }

        mnist_json = json.dumps(mnist_dict)

        path_dict = self.__get_datafile_info()
        datafile_path       = path_dict["datafile-path"]
        json_file_name      = path_dict["json-file-name"]
        train_image_path    = path_dict["train-image-path"]
        test_image_path     = path_dict["test-image-path"]

        with open(json_file_name, "w") as fd:
            fd.write(mnist_json)

        return self.__mnist_loads()

        for idx,image_at in enumerate(train_images):
            image_at = np.array(image_at)
            file_name = "%s/%05d_%d.bmp" % (train_image_path, idx, train_labels[idx])
            img = Image.fromarray(image_at, '1')
            img.save(file_name)
            print("[%d/%d] save test train image : %s" % (idx,len(train_images),file_name))

        for idx,image_at in enumerate(test_images):
            image_at = np.array(image_at)
            file_name = "%s/%05d_%d.bmp" % (test_image_path, idx, test_labels[idx])
            img = Image.fromarray(image_at, '1')
            img.save(file_name)
            print("[%d/%d] save test test image : %s" % (idx,len(test_images),file_name))

        return self.__mnist_loads()

    def __mnist_loads(self):
        path_dict = self.__get_datafile_info()
        datafile_path   = path_dict["datafile-path"]
        json_file_name  = path_dict["json-file-name"]

        if not os.path.exists(json_file_name):
            return None

        mnist_dataset = mnist.load_data()
        (train_images, train_labels), (test_images, test_labels) = mnist_dataset

        print("train_images: shape=%s, dtype=%s, ndim=%d" % (train_images.shape, train_images.dtype, train_images.ndim))
        print("train_labels: shape=%s, dtype=%s, ndim=%d" % (train_labels.shape, train_labels.dtype, train_labels.ndim))

        if self.n_test_set:
            train_images = train_images[0:self.n_train_set]
            train_labels = train_labels[0:self.n_train_set]
            test_labels  = test_labels[0:self.n_test_set]
            test_images  = test_images[0:self.n_test_set]

        train_images = train_images.reshape((self.n_train_set, 28 * 28))
        train_images = train_images.astype('float32') / 255

        test_images = test_images.reshape((self.n_test_set, 28 * 28))
        test_images = test_images.astype('float32') / 255

        train_labels = to_categorical(train_labels)
        test_labels = to_categorical(test_labels)

        mnist_dict   = {
            "train-images"  : train_images,
            "train-labels"  : train_labels,
            "test-images"   : test_images,
            "test-labels"   : test_labels,
        }       

        return mnist_dict

def main():
    e = MnistDataSet()#(10000, 2000)
    e.do_train()
    result = e.do_evaluation()
    if result != None:
        test_loss, test_acc = result
        print("test_loss=%s, test_acc=%s" % (test_loss, test_acc))
    e.get_image_input()

if __name__ == "__main__":
    main()
