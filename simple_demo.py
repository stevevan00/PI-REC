
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ui.functions import *
from ui.photoviewer import PhotoWindow
from ui.designer.paint import DesignerWindow
from MainWindow import Ui_MainWindow
import sys
from colorutils import rgb_to_hex, hex_to_rgb, rgb_to_hsv
import cv2
import numpy as np
import argparse

sketchButtons = [
    'designerSketchBtn',
    'viewerSketchBtn',
    'saveSketchBtn'
]

colorButtons = [
    'dominantColor_1',
    'dominantColor_2',
    'dominantColor_3',
    'dominantColor_4',
    'designerColorBtn',
    'viewerColorBtn',
    'saveColorBtn'
]

outputButtons = [
    'reconstructBtn',
    'refinementBtn',
    'viewerOutputBtn',
    'saveOutputBtn'
]

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self,param, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        
        self.outputImg = None
        self.fileName = None
        self.clearMode = False
        self.input_size = 176
        self.dlg = QColorDialog(self.colorGraphicsView)
        self.labelColors = None
        self.colors = None
        self.K = param.kmeans
        self.sigma = param.canny
        # check the exist of path and the weights files
        self.datasets = ['Asian', 'Non_Asian', 'Anime', 'Pixiv', 'Webtoon']
        self.models_G = []
        self.models_R = []
        for ds in self.datasets:
            config = check_load_G('./models/{}'.format(ds))
            model_G = load_model_G(config)

            config = check_load_R('./models/{}'.format(ds))
            model_R = load_model_R(config)
            
            self.models_G.append(model_G)
            self.models_R.append(model_R)
        self.model_G = self.models_G[0]
        self.model_R = self.models_R[0]
        
        # Add item to combobox
        for d in ['Asian', 'Non_Asian', 'Anime', 'Pixiv', 'Webtoon']:
            self.modelCombo.addItem(d)
        self.modelCombo.activated[str].connect(self.on_model_changed)
        
        self.actionOpen_Image.triggered.connect(self.open_image)
        self.actionReset_Image.triggered.connect(self.reset)
        self.actionFlip_Horizontal.triggered.connect(self.flip_image_horizontal)
        self.actionFlip_Vertical.triggered.connect(self.flip_image_vertical)
        
        
        #sketch button
        self.designerSketchBtn.clicked.connect(self.open_sketch_designer)
        self.viewerSketchBtn.clicked.connect(self.open_sketch_viewer)
        self.saveSketchBtn.clicked.connect(self.save_sketch)
        
        #color button
        self.dominantColor_1.clicked.connect(self.open_palette_1)
        self.dominantColor_2.clicked.connect(self.open_palette_2)
        self.dominantColor_3.clicked.connect(self.open_palette_3)
        self.dominantColor_4.clicked.connect(self.open_palette_4)
        self.designerColorBtn.clicked.connect(self.open_color_designer)
        self.viewerColorBtn.clicked.connect(self.open_color_viewer)
        self.saveColorBtn.clicked.connect(self.save_color)
        
        #result button
        self.reconstructBtn.clicked.connect(self.reconstruct_image)
        self.refinementBtn.clicked.connect(self.refine_image)
        self.viewerOutputBtn.clicked.connect(self.open_output_viewer)
        self.saveOutputBtn.clicked.connect(self.save_output)
    
    def open_palette(self, index):
        color = self.colors[index]
        result = QColorDialog.getColor(QColor(color[2], color[1], color[0]))
        if QColor.isValid(result):
            if color[2] == color[1] == color[0] == 0: self.colors[index] = [1,1,1]
            else: self.colors[index] = [result.blue(), result.green(), result.red()]
            res = self.colors[self.labelColors.flatten()]
            res = res.reshape((self.color_domain.shape))
            self.color_domain = res
            
            self.update_views()
            
    def open_palette_1(self):
        self.open_palette(0)
        
    def open_palette_2(self):
        self.open_palette(1)
        
    def open_palette_3(self):
        self.open_palette(2)
        
    def open_palette_4(self):
        self.open_palette(3)
    
    def reconstruct_image(self):
        # self.edge = self.make_sketch(self.edge, self.sketch_scene.sketch_points)
        # self.color_domain = self.make_stroke(self.color_domain, self.color_scene.stroke_points)
            
        print("\nDrawing using color domain and edge...")
        edge = cv2.cvtColor(self.edge, cv2.COLOR_BGR2GRAY)
        # color_domain = cv2.cvtColor(self.color_domain, cv2.COLOR_BGR2RGB)
        color_domain = self.color_domain
        cv2.imwrite('./temp/edge.png', edge)
        cv2.imwrite('./temp/color_domain.png', color_domain)
        self.outputImg = model_process(self.model_G, color_domain, edge)
        
        self.update_views()
        self.button_enabled(outputButtons)
        print("\nFinished!")
    
    def refine_image(self):
        edge = cv2.cvtColor(self.edge, cv2.COLOR_BGR2GRAY)
        self.outputImg = model_refine(self.model_R, self.outputImg, edge)
        
        self.update_views()
        print("\nFinished!")
        
    def open_sketch_viewer(self):
        path = './temp/sketch.png'
        if type(self.edge):
            cv2.imwrite(path,self.edge)
            self.window = PhotoWindow(path=path)
            self.window.setGeometry(500, 300, 800, 600)
            self.window.show()
        else:
            buttonReply = QMessageBox.question(self, 'Error', "No Image detected", QMessageBox.Yes, QMessageBox.Yes)
            if buttonReply == QMessageBox.Yes:
                print('Yes clicked.')   
                
    def open_color_viewer(self):
        if type(self.color_domain):
            path = './temp/color_domain.png'
            cv2.imwrite(path,self.color_domain)
            new_color_domain = self.concat_sketch_color(self.edge, self.color_domain)
            path = './temp/color_domain_sketch.png'
            cv2.imwrite(path,new_color_domain)
            self.window = PhotoWindow(path=path)
            self.window.setGeometry(500, 300, 800, 600)
            self.window.show()
        else:
            buttonReply = QMessageBox.question(self, 'Error', "No Image detected", QMessageBox.Yes, QMessageBox.Yes)
            if buttonReply == QMessageBox.Yes:
                print('Yes clicked.')    
                           
    def open_output_viewer(self):
        path = './temp/output.png'
        if type(self.outputImg):
            cv2.imwrite(path,self.outputImg)
            self.window = PhotoWindow(path=path)
            self.window.setGeometry(500, 300, 800, 600)
            self.window.show()
        else:
            buttonReply = QMessageBox.question(self, 'Error', "Please click generate to activate save image", QMessageBox.Yes, QMessageBox.Yes)
            if buttonReply == QMessageBox.Yes:
                print('Yes clicked.')    
    
    def save_sketch(self):
        if type(self.edge):
            fileName, _ = QFileDialog.getSaveFileName(self, "Save File",
                    QDir.currentPath())
            if fileName:
                cv2.imwrite(fileName+'.png',self.edge)
                
    def save_color(self):
        if type(self.color_domain):
            fileName, _ = QFileDialog.getSaveFileName(self, "Save File",
                    QDir.currentPath())
            if fileName:
                cv2.imwrite(fileName+'.png',self.color_domain)
                
    def save_output(self):
        # name = 'Webtoon'
        
        # for index, ds in enumerate(self.datasets):
        #     self.outputImg = None
        #     self.model_G = self.models_G[index]
        #     self.model_R = self.models_R[index]
            
        #     for c in ['Generate', 'Refine']:
        #         if c == 'Generate': self.reconstruct_image()
        #         else: self.refine_image()
        #         fileName = './output/{}_{}_{}'.format(name, ds, c)
        #         cv2.imwrite(fileName+'.png',self.outputImg)
            
        if type(self.outputImg):
            fileName, _ = QFileDialog.getSaveFileName(self, "Save File",
                    QDir.currentPath())
            if fileName:
                cv2.imwrite(fileName+'.png',self.outputImg)
        else:
            buttonReply = QMessageBox.question(self, 'Error', "Please click reconstruct to activate save image", QMessageBox.Yes, QMessageBox.Yes)
            if buttonReply == QMessageBox.Yes:
                print('Yes clicked.')   
                     
    def open_image(self):
        if not self.clearMode:
            fileName, _ = QFileDialog.getOpenFileName(self, "Open File",
                    QDir.currentPath())
            # fileName = './examples/draw_output.png'
            self.fileName = fileName
        if self.fileName:
            image = QPixmap(self.fileName)
            if image.isNull():
                QMessageBox.information(self, "Image Viewer",
                        "Cannot load %s." % self.fileName)
                return

            # self.image = image.scaled(self.sketchGraphicsView.size(), Qt.IgnoreAspectRatio)

            
            img, edge, color_domain = initial_colorful_pic(self.fileName, self.sigma,self.K)
            self.image = img
            # edge = np.expand_dims(edge,axis=2)
            edge = cv2.cvtColor(edge,cv2.COLOR_GRAY2BGR)
            self.edge = edge
            self.color_domain = color_domain
            
            # if len(self.outputGraphicsView.items())>0:
            #     for i in range(len(self.outputGraphicsView.items())):
            #         self.outputGraphicsView.removeItem(self.outputGraphicsView.items()[-1])
                
            self.update_views()
            self.button_enabled(sketchButtons)
            self.button_enabled(colorButtons)
            self.button_enabled(outputButtons[:1])
            self.button_disabled(outputButtons[1:])
            
    def update_views(self):
        edge, color_domain = self.edge, self.color_domain
        # self.sketchGraphicsView.reset()
        # if len(self.sketchGraphicsView.items())>0:
        #     self.sketchGraphicsView.reset_items()
        qedge = cvImage2QImage(edge)
        scene = QGraphicsScene(self)
        scene.addPixmap(QPixmap(qedge))
        self.sketchGraphicsView.setScene(scene)
        
        # self.colorGraphicsView.reset()
        # if len(self.colorGraphicsView.items())>0:
        #     self.colorGraphicsView.reset_items()
        
        new_color_domain = self.concat_sketch_color(edge, color_domain)
        qcolor_domain = cvImage2QImage(new_color_domain)
        scene = QGraphicsScene(self)
        scene.addPixmap(QPixmap(qcolor_domain))
        self.colorGraphicsView.setScene(scene)
            
        # if len(self.outputGraphicsView.items())>0:
        #     self.outputGraphicsView.removeItem(self.outputGraphicsView.items()[-1])
            
        if self.outputImg is not None:
            result = self.outputImg
            qim = QImage(result.data, result.shape[1], result.shape[0], result.strides[0], QImage.Format_BGR888)
            scene = QGraphicsScene(self)
            scene.addPixmap(QPixmap.fromImage(qim))
            self.outputGraphicsView.setScene(scene)
        
        result = self.image
        qim = QImage(result.data, result.shape[1], result.shape[0], result.strides[0], QImage.Format_BGR888)
        scene = QGraphicsScene(self)
        scene.addPixmap(QPixmap.fromImage(qim))
        self.gtGraphicsView.setScene(scene)
        
        self.update_color_dominant()
    
    def update_color_dominant(self):
        img = self.color_domain
        Z = img.reshape((-1, 3))

        # convert to np.float32
        Z = np.float32(Z)

        # define criteria, number of clusters(K) and apply kmeans()
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        # K = 8
        ret, label, center = cv2.kmeans(Z, self.K, None, criteria, 8, cv2.KMEANS_PP_CENTERS)

        # Now convert back into uint8, and make original image
        center = np.uint8(center)
        
        #returning after converting to integer from float
        # print('Color Domain',center)
        self.labelColors = label
        print(self.labelColors)
        self.colors = center
        print(self.colors)
        for i in range(1,5):
            btn = getattr(self, 'dominantColor_{}'.format(i))
            btn.setStyleSheet('')
            
        for index, color in enumerate(center):
            if index > 3: break
            btn = getattr(self, 'dominantColor_{}'.format(index+1))
            hex = rgb_to_hex(tuple(color[::-1]))
            btn.setStyleSheet('QPushButton { background-color: %s; }' % hex)
    
    def button_disabled(self, attrs):
        for attr in attrs:
            btn = getattr(self, attr)
            btn.setEnabled(False)
    
    def button_enabled(self, attrs):
        for attr in attrs:
            btn = getattr(self, attr)
            btn.setEnabled(True)    
                        
    def on_model_changed(self, text):
        ds = [i for i, value in enumerate(self.datasets) if value == text]
        ind = ds[0]
        self.model_G = self.models_G[ind]
        self.model_R = self.models_R[ind]
        self.reconstruct_image()
    
    def concat_sketch_color(self, edge, color, invert=True):
        img = cv2.addWeighted(color, 1, edge, 1, 0.0)
        if invert:
            r1, g1, b1 = 255, 255, 255 # Original value
            r2, g2, b2 = 0, 0, 0 # Value that we want to replace it with
            red, green, blue = img[:,:,0], img[:,:,1], img[:,:,2]
            mask = (red == r1) & (green == g1) & (blue == b1)
            img[:,:,:3][mask] = [r2, g2, b2]
        return img
 
 
    def check_input_image(self, command):
        if self.fileName: 
            return True
        else: 
            buttonReply = QMessageBox.question(self, 'Error', "Please click File > Open Image to activate %s image"%command, QMessageBox.Yes, QMessageBox.Yes)
            return False
        
    def reset(self):
        if self.check_input_image('reset'):
            self.clearMode = True
            self.open_image()
            self.clearMode = False

    def flip_image_horizontal(self):
        if self.check_input_image('flip horizontal'):
            self.edge = cv2.flip(self.edge, 1)
            self.color_domain = cv2.flip(self.color_domain, 1)
            self.image = cv2.flip(self.image, 1)
            if type(self.outputImg):
                self.outputImg = cv2.flip(self.outputImg, 1)
            self.update_views()
    
    def flip_image_vertical(self):
        if self.check_input_image('flip vertical'):
            self.edge = cv2.flip(self.edge, 0)
            self.color_domain = cv2.flip(self.color_domain, 0)
            self.image = cv2.flip(self.image, 0)
            if type(self.outputImg):
                self.outputImg = cv2.flip(self.outputImg, 0)
            self.update_views()
    
    def open_sketch_designer(self):
        path = './temp/sketch.png'
        cv2.imwrite(path,self.edge)
        self.canvasWindow = DesignerWindow(mode=0)
        self.canvasWindow.show()
        self.canvasWindow._signal.connect(self.on_close_sketch_designer)
            
    def open_color_designer(self):
        path = './temp/color_domain.png'
        cv2.imwrite(path,self.color_domain)
        path = './temp/sketch.png'
        cv2.imwrite(path,self.edge)
        new_color_domain = self.concat_sketch_color(self.edge, self.color_domain)
        path = './temp/color_domain_sketch.png'
        cv2.imwrite(path,new_color_domain)
        self.canvasWindow = DesignerWindow(mode=1)
        self.canvasWindow.show() 
        self.canvasWindow._signal.connect(self.on_close_color_designer)
    
    def on_close_sketch_designer(self, path):
        edge = cv2.imread(path)
        edge = cv2.resize(edge, (self.input_size, self.input_size), interpolation=cv2.INTER_LANCZOS4)
        edge[edge <= 59] = 0
        edge[edge > 59] = 255
        self.edge = edge
        self.update_views()
        print(path)
    
    def on_close_color_designer(self, path):
        color_domain = cv2.imread(path)
        self.color_domain = cv2.resize(color_domain, (self.input_size, self.input_size), interpolation=cv2.INTER_LANCZOS4)
        self.update_views()
        print(path)
                                
if __name__ == "__main__":
    app = QApplication(sys.argv)
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--canny', type=float, default=2.6, help='sigma of canny')
    parser.add_argument('-k', '--kmeans', type=int, default=4, help='color numbers of kmeans')
    args = parser.parse_args()
    application = MainWindow(args)
    application.show()
    sys.exit(app.exec_())