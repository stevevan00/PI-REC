import cv2
import numpy as np
import os
import shutil
import glob
from src.utils import resize, img_kmeans
from skimage.feature import canny
from skimage.color import rgb2gray
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from main import main
from src.config import Config

WIN_SIZE=176

def initial_pics(edge_file=None, color_domain_file=None):
    if edge_file:
        edge_file = cv2.imread(edge_file, cv2.IMREAD_GRAYSCALE)
        imgh, imgw = edge_file.shape[0:2]
        if imgh != imgw:
            # center crop
            side = np.minimum(imgh, imgw)
            j = (imgh - side) // 2
            i = (imgw - side) // 2
            edge_file = edge_file[j:j + side, i:i + side, ...]
        edge_file = cv2.resize(edge_file, (WIN_SIZE, WIN_SIZE), interpolation=cv2.INTER_LANCZOS4)
        edge_file[edge_file <= 59] = 0
        edge_file[edge_file > 59] = 255
    if color_domain_file:
        imgh, imgw = color_domain_file.shape[0:2]
        if imgh != imgw:
            # center crop
            side = np.minimum(imgh, imgw)
            j = (imgh - side) // 2
            i = (imgw - side) // 2
            color_domain_file = color_domain_file[j:j + side, i:i + side, ...]
        color_domain_file = cv2.imread(color_domain_file)
        color_domain_file = cv2.resize(color_domain_file, (WIN_SIZE, WIN_SIZE))
    
    return edge_file, color_domain_file

def cvImage2QImage(img, bgr=True):
    try:
        height, width, channel = img.shape
        bytesPerLine = 3 * height
        qImg = QImage(img.data, width, height, bytesPerLine, QImage.Format_BGR888)
    except:
        # img = np.require(img, np.uint8, 'C')
        height, width = img.shape
        # bytesPerLine = 3 
        qImg = QImage(img.data, width, height, QImage.Format_Grayscale8)
    return qImg

def initial_colorful_pic(file, sigma, kmeans):
    img = cv2.imread(file)
    
    imgh, imgw = img.shape[0:2]
    if imgh != imgw:
        # center crop
        side = np.minimum(imgh, imgw)
        j = (imgh - side) // 2
        i = (imgw - side) // 2
        img = img[j:j + side, i:i + side, ...]
        
    img = resize(img, WIN_SIZE, WIN_SIZE, )
    img_gray = rgb2gray(img)

    # edge
    out_edge = canny(img_gray, sigma=float(sigma), mask=None).astype(np.uint8)
    out_edge[out_edge == 1] = 255
    # color_domain
    # random_blur = 2 * np.random.randint(7, 18) + 1
    out_blur = cv2.medianBlur(img, 23)
    # K = np.random.randint(2, 6)
    out_blur = img_kmeans(out_blur, int(kmeans))
    out_blur = cv2.medianBlur(out_blur, np.random.randint(1, 4) * 2 - 1)
    return img, out_edge, out_blur


def load_model_G(config):
    """
    Load generate phase model, the key function to interact with backend.
    """
    model = main(mode=5, config=config)
    return model


def load_model_R(config):
    """
    Load refinement phase model, the key function to interact with backend.
    """
    model = main(mode=6, config=config)
    return model


def check_load_G(path):
    """
    Check the directory and weights files. Load the config file.
    """
    if not os.path.exists(path):
        raise NotADirectoryError('Path <' + str(path) + '> does not exist!')

    G_weight_files = list(glob.glob(os.path.join(path, 'G_Model_gen*.pth')))
    if len(G_weight_files) == 0:
        raise FileNotFoundError('Weights file <G_Model_gen*.pth> cannot be found under path: ' + path)

    config_path = os.path.join(path, 'config.yml')
    # copy config template if does't exist
    if not os.path.exists(config_path):
        shutil.copyfile('./config.yml.example', config_path)

    # load config file
    config = Config(config_path)

    return config


def check_load_R(path):
    """
    Check the directory and weights files. Load the config file.
    """

    R_weight_files = list(glob.glob(os.path.join(path, 'R_Model_gen*.pth')))
    if len(R_weight_files) == 0:
        raise FileNotFoundError('Weights file <R_Model_gen*.pth> cannot be found under path: ' + path)

    config_path = os.path.join(path, 'config.yml')

    # load config file
    config = Config(config_path)

    return config



def model_process(model_G, color_domain, edge):
    """
    Key function to reconstruct image from edge and color domain.
    :param color_domain: channel=3
    :param edge: channel=1
    :return: reconstruction
    """
    # print(color_domain.shape, edge.shape)
    size_origin = color_domain.shape[:2]
    img = cv2.cvtColor(color_domain, cv2.COLOR_BGR2RGB)
    result = model_G.draw(img, edge)
    result = cv2.resize(result, size_origin)
    result = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)
    return result


def model_refine(model_R, img_blur, edge):
    """
    Key function to refine image from 2nd phase output.
    :param img_blur: channel=3
    :param edge: channel=1
    :return: refinement
    """
    # print(color_domain.shape, edge.shape)
    size_origin = img_blur.shape[:2]
    img_blur = cv2.cvtColor(img_blur, cv2.COLOR_BGR2RGB)
    result = model_R.refine(img_blur, edge)
    result = cv2.resize(result, size_origin)
    result = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)
    return result
