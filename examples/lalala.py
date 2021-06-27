import imageio
import cv2
import skimage
import numpy as np
from skimage import feature as ft
# load image
img = imageio.imread('288.png')
# img = cv2.imread(self.data[index])
# img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
# img = Image.open(self.data[index])


gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# gray = cv2.medianBlur(gray, 3)
# create grayscale image
# img_gray = skimage.color.rgb2gray(img)

thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)[1]

# morphology edgeout = dilated_mask - mask
# morphology dilate
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
dilate = cv2.morphologyEx(thresh, cv2.MORPH_DILATE, kernel)

# get absolute difference between dilate and thresh
diff = cv2.absdiff(dilate, thresh)

# invert
edges = 255 - diff

# write result to disk
cv2.imwrite("cartoon_gray.jpg", gray)
cv2.imwrite("cartoon_thresh.jpg", thresh)
cv2.imwrite("cartoon_dilate.jpg", dilate)
cv2.imwrite("cartoon_diff.jpg", diff)
cv2.imwrite("cartoon_edges.jpg", edges)

# print(gray.shape)
# canny = ft.canny(gray, sigma=1.5, mask=None).astype(np.float) * 255.0
canny_img = cv2.canny(gray)
# print(canny)
cv2.imwrite("cartoon_edges_canny.jpg", canny_img)

# display it
# cv2.imshow("thresh", thresh)
# cv2.imshow("dilate", dilate)
# cv2.imshow("diff", diff)
# cv2.imshow("edges", edges)
# cv2.waitKey(0)