from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        self.input_size = 176
        
        Form.setObjectName("Form")
        Form.resize(1200, 660)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        
        self.openImageButton = QtWidgets.QPushButton(Form)
        self.openImageButton.setGeometry(QtCore.QRect(10, 10, 100,25))
        self.openImageButton.setObjectName("openImageButton")
        # Sketch component
        self.graphicsView = QtWidgets.QGraphicsView(Form)
        self.graphicsView.setGeometry(QtCore.QRect(20, 120, self.input_size, self.input_size))
        self.graphicsView.setObjectName("graphicsView")
        self.eraserSketchButton = QtWidgets.QPushButton(Form)
        self.eraserSketchButton.setGeometry(QtCore.QRect(200, 120, 100, 25))
        self.eraserSketchButton.setObjectName("eraserSketchButton")
        self.strokeSketchButton = QtWidgets.QPushButton(Form)
        self.strokeSketchButton.setGeometry(QtCore.QRect(325, 120, 100, 25))
        self.strokeSketchButton.setObjectName("strokeSketchButton")
        self.selectionSketchButton = QtWidgets.QPushButton(Form)
        self.selectionSketchButton.setGeometry(QtCore.QRect(450, 120, 100, 25))
        self.selectionSketchButton.setObjectName("selectionSketchButton")
        self.undoSketchButton = QtWidgets.QPushButton(Form)
        self.undoSketchButton.setGeometry(QtCore.QRect(200, 160, 100, 25))
        self.undoSketchButton.setObjectName("undoSketchButton")
        
        # Color component
        self.graphicsView_2 = QtWidgets.QGraphicsView(Form)
        self.graphicsView_2.setGeometry(QtCore.QRect(20, 320, self.input_size, self.input_size))
        self.graphicsView_2.setObjectName("graphicsView_2")
        self.strokeColorButton = QtWidgets.QPushButton(Form)
        self.strokeColorButton.setGeometry(QtCore.QRect(200, 320, 100, 25))
        self.strokeColorButton.setObjectName("strokeColorButton")
        self.undoColorButton = QtWidgets.QPushButton(Form)
        self.undoColorButton.setGeometry(QtCore.QRect(200, 360, 100,25))
        self.undoColorButton.setObjectName("undoColorButton")
        self.paletteColorButton = QtWidgets.QPushButton(Form)
        self.paletteColorButton.setGeometry(QtCore.QRect(325, 320, 100, 25))
        self.paletteColorButton.setObjectName("paletteColorButton")
        self.dropperColorButton = QtWidgets.QPushButton(Form)
        self.dropperColorButton.setGeometry(QtCore.QRect(325, 350, 100, 25))
        self.dropperColorButton.setObjectName("dropperColorButton")
                
        # Result component
        self.graphicsView_3 = QtWidgets.QGraphicsView(Form)
        self.graphicsView_3.setGeometry(QtCore.QRect(660, 120, self.input_size, self.input_size))
        self.graphicsView_3.setObjectName("graphicsView_3")
        self.completeResultButton = QtWidgets.QPushButton(Form)
        self.completeResultButton.setGeometry(QtCore.QRect(560, 360, 100,25))
        self.completeResultButton.setObjectName("completeResultButton")
        self.resetButton = QtWidgets.QPushButton(Form)
        self.resetButton.setGeometry(QtCore.QRect(370, 40, 100,25))
        self.resetButton.setObjectName("resetButton")
        self.refinementResultButton = QtWidgets.QPushButton(Form)
        self.refinementResultButton.setGeometry(QtCore.QRect(560, 400, 100, 25))
        self.refinementResultButton.setObjectName("refinementResultButton")
        

        self.saveImageButton = QtWidgets.QPushButton(Form)
        self.saveImageButton.setGeometry(QtCore.QRect(610, 10, 97, 27))
        self.saveImageButton.setObjectName("saveImageButton")
        
        self.modelCombo = QtWidgets.QComboBox(self)
        for d in ['Asian', 'Non_Asian', 'Anime', 'Pixiv', 'Webtoon']:
            self.modelCombo.addItem(d)
        self.modelCombo.setGeometry(QtCore.QRect(610, 40, 97, 27))
        self.modelCombo.setObjectName("modelCombo")

        self.imageViewerButton = QtWidgets.QPushButton(Form)
        self.imageViewerButton.setGeometry(QtCore.QRect(610, 70, 97, 27))
        self.imageViewerButton.setObjectName("imageViewerButton")

        self.retranslateUi(Form)
        self.openImageButton.clicked.connect(Form.open)
        self.eraserSketchButton.clicked.connect(Form.mask_mode)
        self.strokeSketchButton.clicked.connect(Form.sketch_mode)
        self.strokeColorButton.clicked.connect(Form.stroke_mode)
        self.completeResultButton.clicked.connect(Form.complete)
        self.undoColorButton.clicked.connect(Form.color_undo)
        self.paletteColorButton.clicked.connect(Form.color_change_mode)
        self.resetButton.clicked.connect(Form.clear)
        self.selectionSketchButton.clicked.connect(Form.crop_mode)
        self.refinementResultButton.clicked.connect(Form.refine)
        self.undoSketchButton.clicked.connect(Form.sketch_undo)

        self.saveImageButton.clicked.connect(Form.save_img)
        self.modelCombo.activated[str].connect(self.onComboChanged)
        self.imageViewerButton.clicked.connect(Form.open_viewer)

        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "PI-REC"))
        self.openImageButton.setText(_translate("Form", "Open Image"))
        self.eraserSketchButton.setText(_translate("Form", "Eraser Mode"))
        self.strokeSketchButton.setText(_translate("Form", "Sketches Mode"))
        self.strokeColorButton.setText(_translate("Form", "Color Mode"))
        self.completeResultButton.setText(_translate("Form", "Complete"))
        self.undoColorButton.setText(_translate("Form", "Undo Color"))
        self.paletteColorButton.setText(_translate("Form", "Palette"))
        self.resetButton.setText(_translate("Form", "Reset"))
        self.selectionSketchButton.setText(_translate("Form", "Selection Mode"))
        self.refinementResultButton.setText(_translate("Form", "Refinement"))
        self.undoSketchButton.setText(_translate("Form", "Undo Sketch"))

        self.saveImageButton.setText(_translate("Form", "Save Img"))
        self.imageViewerButton.setText(_translate("Form", "Open Viewer"))
        

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
