import PIL
import os
from PIL import Image
import pandas as pd


def export_image_sizes(folder,filename):

    files = os.listdir(folder)

    names = []
    size_x = []
    size_y = []

    for file in files:
        filepath = folder + file
        img = Image.open(filepath)
        x, y = img.size
        names.append(file)
        size_x.append(x)
        size_y.append(y)

    df = pd.DataFrame(list(zip(names,size_x,size_y)))
    df.to_csv(filename)

def resize_all_images_in_folder(input_folder, output_folder, size_x, size_y):

    files = os.listdir(input_folder)

    for file in files:
        filepath = input_folder + file
        img = Image.open(filepath)
        img = img.resize((size_x,size_y))
        img.save(output_folder + file)


def main():
    input_path = "images/"
    output_path = "scaled_images/"

    x_dim = 200
    y_dim = 300

    resize_all_images_in_folder(input_path,output_path,x_dim,y_dim)
    #export_image_sizes(input_path,"image_sizes.csv")



if __name__ == "__main__":
    main()