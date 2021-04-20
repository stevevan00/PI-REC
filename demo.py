import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from ui.ui import Ui_Form
from ui.mouse_event import GraphicsScene
from ui.functions import *
import numpy as np
# from utils.config import Config
# from model import Model
import os
import time
import cv2
import argparse

WIN_SIZE = 176

class Ex(QWidget, Ui_Form):
    # def __init__(self, model, config):
    def __init__(self, models_G, models_R):
        super().__init__()
        self.setupUi(self)
        self.show()
        self.models_G = models_G
        self.model_G = self.models_G[0]
        self.models_R = models_R
        self.model_R = self.models_R[0]
        self.datasets = ['Asian', 'Non_Asian', 'Anime', 'Pixiv', 'Webtoon']
        # self.model.load_demo_graph(config)

        self.output_img = None

        self.mat_img = None

        self.ld_mask = None
        self.ld_sk = None

        self.modes = [0,0,0,0]
        self.mouse_clicked = False
        self.sketch_scene = GraphicsScene(self.modes, sketch=True)
        self.graphicsView.setScene(self.sketch_scene)
        self.graphicsView.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.graphicsView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphicsView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.color_scene = GraphicsScene(self.modes, sketch=False)
        self.graphicsView_2.setScene(self.color_scene)
        self.graphicsView_2.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.graphicsView_2.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphicsView_2.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.result_scene = QGraphicsScene()
        self.graphicsView_3.setScene(self.result_scene)
        self.graphicsView_3.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.graphicsView_3.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphicsView_3.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.dlg = QColorDialog(self.graphicsView)
        self.color = None

    def mode_select(self, mode):
        for i in range(len(self.modes)):
            self.modes[i] = 0
        self.modes[mode] = 1

    def open(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File",
                QDir.currentPath())
        self.fileName = fileName
        if fileName:
            image = QPixmap(fileName)
            mat_img = cv2.imread(fileName)
            if image.isNull():
                QMessageBox.information(self, "Image Viewer",
                        "Cannot load %s." % fileName)
                return

            self.image = image.scaled(self.graphicsView.size(), Qt.IgnoreAspectRatio)

            
            edge, color_domain = initial_colorful_pic(self.fileName, 2,10)
            # edge = np.expand_dims(edge,axis=2)
            edge = cv2.cvtColor(edge,cv2.COLOR_GRAY2BGR)
            self.edge = edge
            self.color_domain = color_domain
            
            if len(self.result_scene.items())>0:
                for i in range(len(self.result_scene.items())):
                    self.result_scene.removeItem(self.result_scene.items()[-1])
                
            self.update_views()

    def update_views(self):
        edge, color_domain = self.edge, self.color_domain
        self.sketch_scene.reset()
        if len(self.sketch_scene.items())>0:
            self.sketch_scene.reset_items()
        qedge = cvImage2QImage(edge)
        self.sketch_scene.addPixmap(QPixmap(qedge))
        
        self.color_scene.reset()
        if len(self.color_scene.items())>0:
            self.color_scene.reset_items()
        
        new_color_domain = self.concat_sketch_color(edge, color_domain)
        qcolor_domain = cvImage2QImage(new_color_domain)
        self.color_scene.addPixmap(QPixmap(qcolor_domain))
            
        if len(self.result_scene.items())>0:
            self.result_scene.removeItem(self.result_scene.items()[-1])
            
        if self.output_img is not None:
            result = self.output_img
            qim = QImage(result.data, result.shape[1], result.shape[0], result.strides[0], QImage.Format_BGR888)
            self.result_scene.addPixmap(QPixmap.fromImage(qim))
        else:
            self.result_scene.addPixmap(self.image)

    def concat_sketch_color(self, edge, color, invert=True):
        img = cv2.addWeighted(color, 1, edge, 1, 0.0)
        if invert:
            r1, g1, b1 = 255, 255, 255 # Original value
            r2, g2, b2 = 0, 0, 0 # Value that we want to replace it with
            red, green, blue = img[:,:,0], img[:,:,1], img[:,:,2]
            mask = (red == r1) & (green == g1) & (blue == b1)
            img[:,:,:3][mask] = [r2, g2, b2]
        return img
        
    # Function for changing mode
    def mask_mode(self):
        self.mode_select(0)

    # Function for changing mode
    def sketch_mode(self):
        self.mode_select(1)

    # Function for changing mode
    def stroke_mode(self):
        if not self.color:
            self.color_change_mode()
        if self.color == '#000000': self.color = '#000001' 
        self.color_scene.get_stk_color(self.color)
        self.mode_select(2)

    # Function for changing mode
    def color_change_mode(self):
        print('Stroke mode', self.color)
        self.dlg.exec_()
        self.color = self.dlg.currentColor().name()
        # print(self.color, type(self.color))
        if self.color == '#000000': self.color = '#000001' 
        self.pushButton_4.setStyleSheet("background-color: %s;" % self.color)
        self.color_scene.get_stk_color(self.color)

    # Function for changing mode
    def crop_mode(self):
        self.mode_select(3)
        
    # Function for generate image
    def complete(self):
        self.edge = self.make_sketch(self.edge, self.sketch_scene.sketch_points)
        self.color_domain = self.make_stroke(self.color_domain, self.color_scene.stroke_points)
            
        print("\nDrawing using color domain and edge...")
        edge = cv2.cvtColor(self.edge, cv2.COLOR_BGR2GRAY)
        # color_domain = cv2.cvtColor(self.color_domain, cv2.COLOR_BGR2RGB)
        color_domain = self.color_domain
        cv2.imwrite('./temp/edge.png', edge)
        cv2.imwrite('./temp/color_domain.png', color_domain)
        self.output_img = model_process(self.model_G, color_domain, edge)
        
        self.update_views()
        print("\nFinished!")

    def refine(self):
        edge = cv2.cvtColor(self.edge, cv2.COLOR_BGR2GRAY)
        self.output_img = model_refine(self.model_R, self.output_img, edge)
        
        self.update_views()
        print("\nFinished!")
        
    def make_sketch(self, sketch, pts):
        if len(pts)>0:
            for pt in pts:
                if pt['eraser']:
                    cv2.line(sketch,pt['prev'],pt['curr'],(0,0,0),4)
                else:
                    cv2.line(sketch,pt['prev'],pt['curr'],(255,255,255),1)
        return sketch

    def make_stroke(self, color_domain, pts):
        if len(pts)>0:
            for pt in pts:
                try:
                    c = pt['color'].lstrip('#')
                    color = tuple(int(c[i:i+2], 16) for i in (0, 2 ,4))
                    color = (color[2],color[1],color[0])
                    cv2.line(color_domain,pt['prev'],pt['curr'],color,4)
                except:
                    print(pt['color'])
        return color_domain
    
    def save_img(self):
        if type(self.output_img):
            fileName, _ = QFileDialog.getSaveFileName(self, "Save File",
                    QDir.currentPath())
            print(fileName)
            cv2.imwrite(fileName+'.png',self.output_img)
        else:
            buttonReply = QMessageBox.question(self, 'Error', "Please click generate to activate save image", QMessageBox.Yes, QMessageBox.Yes)
            if buttonReply == QMessageBox.Yes:
                print('Yes clicked.')

    def color_undo(self):
        self.color_scene.undo()

    def sketch_undo(self):
        self.sketch_scene.undo()
        
    def clear(self):
        edge, color_domain = initial_colorful_pic(self.fileName, 2,10)
        # edge = np.expand_dims(edge,axis=2)
        edge = cv2.cvtColor(edge,cv2.COLOR_GRAY2BGR)
        self.edge = edge
        self.color_domain = color_domain
        
        edge, color_domain = self.edge, self.color_domain
        self.sketch_scene.reset()
        if len(self.sketch_scene.items())>0:
            self.sketch_scene.reset_items()
        qedge = cvImage2QImage(edge)
        self.sketch_scene.addPixmap(QPixmap(qedge))
        
        self.color_scene.reset()
        if len(self.color_scene.items())>0:
            self.color_scene.reset_items()
        
        new_color_domain = self.concat_sketch_color(edge, color_domain)
        qcolor_domain = cvImage2QImage(new_color_domain)
        self.color_scene.addPixmap(QPixmap(qcolor_domain))

    def onComboChanged(self, text):
        ds = [i for i, value in enumerate(self.datasets) if value == text]
        ind = ds[0]
        self.model_G = self.models_G[ind]
        self.model_R = self.models_R[ind]
        
if __name__ == '__main__':
    # config = Config('demo.yaml')
    # os.environ["CUDA_VISIBLE_DEVICES"] = str(config.GPU_NUM)
    # model = Model(config)

    parser = argparse.ArgumentParser()
    # parser.add_argument('-p', '--path', type=str, help='path of model weights files <.pth>')
    parser.add_argument('-c', '--canny', type=float, default=3, help='sigma of canny')
    parser.add_argument('-k', '--kmeans', type=int, default=3, help='color numbers of kmeans')
    parser.add_argument('-r', '--refinement', action='store_true', help='load refinement model')
    args = parser.parse_args()

    # check the exist of path and the weights files
    datasets = ['Asian', 'Non_Asian', 'Anime', 'Pixiv', 'Webtoon']
    # datasets = ['Anime']
    models_G = []
    models_R = []
    
    for ds in datasets:
        config = check_load_G('./models/{}'.format(ds))
        model_G = load_model_G(config)

        config = check_load_R('./models/{}'.format(ds))
        model_R = load_model_R(config)
        
        models_G.append(model_G)
        models_R.append(model_R)

    # WIN_SIZE = config.INPUT_SIZE
    app = QApplication(sys.argv)
    # ex = Ex(model, config)
    ex = Ex(models_G=models_G, models_R=models_R)
    sys.exit(app.exec_())
