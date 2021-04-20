from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1200, 660)
        self.input_size = 176
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(10, 10, 100,25))
        self.pushButton.setObjectName("pushButton")
        
        # Sketch component
        self.graphicsView = QtWidgets.QGraphicsView(Form)
        self.graphicsView.setGeometry(QtCore.QRect(20, 120, self.input_size, self.input_size))
        self.graphicsView.setObjectName("graphicsView")
        self.pushButton_2 = QtWidgets.QPushButton(Form)
        self.pushButton_2.setGeometry(QtCore.QRect(200, 120, 100, 25))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QtWidgets.QPushButton(Form)
        self.pushButton_3.setGeometry(QtCore.QRect(325, 120, 100, 25))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_9 = QtWidgets.QPushButton(Form)
        self.pushButton_9.setGeometry(QtCore.QRect(450, 120, 100, 25))
        self.pushButton_9.setObjectName("pushButton_9")
        self.pushButton_11 = QtWidgets.QPushButton(Form)
        self.pushButton_11.setGeometry(QtCore.QRect(200, 160, 100, 25))
        self.pushButton_11.setObjectName("pushButton_11")
        
        # Color component
        self.graphicsView_2 = QtWidgets.QGraphicsView(Form)
        self.graphicsView_2.setGeometry(QtCore.QRect(20, 320, self.input_size, self.input_size))
        self.graphicsView_2.setObjectName("graphicsView_2")
        self.pushButton_4 = QtWidgets.QPushButton(Form)
        self.pushButton_4.setGeometry(QtCore.QRect(200, 320, 100, 25))
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_6 = QtWidgets.QPushButton(Form)
        self.pushButton_6.setGeometry(QtCore.QRect(200, 360, 100,25))
        self.pushButton_6.setObjectName("pushButton_6")
        self.pushButton_7 = QtWidgets.QPushButton(Form)
        self.pushButton_7.setGeometry(QtCore.QRect(325, 320, 100, 25))
        self.pushButton_7.setObjectName("pushButton_7")
                
        # Result component
        self.graphicsView_3 = QtWidgets.QGraphicsView(Form)
        self.graphicsView_3.setGeometry(QtCore.QRect(660, 120, self.input_size, self.input_size))
        self.graphicsView_3.setObjectName("graphicsView_3")
        self.pushButton_5 = QtWidgets.QPushButton(Form)
        self.pushButton_5.setGeometry(QtCore.QRect(560, 360, 100,25))
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_8 = QtWidgets.QPushButton(Form)
        self.pushButton_8.setGeometry(QtCore.QRect(370, 40, 100,25))
        self.pushButton_8.setObjectName("pushButton_8")
        self.pushButton_10 = QtWidgets.QPushButton(Form)
        self.pushButton_10.setGeometry(QtCore.QRect(560, 400, 100, 25))
        self.pushButton_10.setObjectName("pushButton_10")
        

        self.saveImg = QtWidgets.QPushButton(Form)
        self.saveImg.setGeometry(QtCore.QRect(610, 10, 97, 27))
        self.saveImg.setObjectName("saveImg")

        self.retranslateUi(Form)
        self.pushButton.clicked.connect(Form.open)
        self.pushButton_2.clicked.connect(Form.mask_mode)
        self.pushButton_3.clicked.connect(Form.sketch_mode)
        self.pushButton_4.clicked.connect(Form.stroke_mode)
        self.pushButton_5.clicked.connect(Form.complete)
        self.pushButton_6.clicked.connect(Form.color_undo)
        self.pushButton_7.clicked.connect(Form.color_change_mode)
        self.pushButton_8.clicked.connect(Form.clear)
        self.pushButton_9.clicked.connect(Form.crop_mode)
        self.pushButton_10.clicked.connect(Form.refine)
        self.pushButton_11.clicked.connect(Form.sketch_undo)

        self.saveImg.clicked.connect(Form.save_img)


        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "PI-REC"))
        self.pushButton.setText(_translate("Form", "Open Image"))
        self.pushButton_2.setText(_translate("Form", "Eraser Mode"))
        self.pushButton_3.setText(_translate("Form", "Sketches Mode"))
        self.pushButton_4.setText(_translate("Form", "Color Mode"))
        self.pushButton_5.setText(_translate("Form", "Complete"))
        self.pushButton_6.setText(_translate("Form", "Undo Color"))
        self.pushButton_7.setText(_translate("Form", "Palette"))
        self.pushButton_8.setText(_translate("Form", "Clear"))
        self.pushButton_9.setText(_translate("Form", "Crop Mode"))
        self.pushButton_10.setText(_translate("Form", "Refinement"))
        self.pushButton_11.setText(_translate("Form", "Undo Sketch"))

        self.saveImg.setText(_translate("Form", "Save Img"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
