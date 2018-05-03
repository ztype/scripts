from image_match.goldberg import ImageSignature
import os
import sys
import numpy as np
import cv2

outpath = './pre_result/'

def cv_imread(file_path):
    cv_img = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)
    return cv_img


def loadImg(file):
    STD_LIMIT = 0.20
    global outpath
    img = cv_imread(file)
    if img is None:
        print("cant open", file)
        return
    if not os.path.exists(outpath):
        os.makedirs(outpath)
    name = os.path.basename(file).split('.')[0]
    img_width = img.shape[0]
    img_height = img.shape[1]

    # 灰度
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # cv2.imshow("gray", cv2.resize(gray, (1024, 1024)))
    # cv2.waitKey(0)
    # 锐化
    blur = cv2.GaussianBlur(gray, (0, 0), 3)
    sharpen = cv2.addWeighted(gray, 1.5, blur, -0.5, 0)
    # 再次锐化
    # blur = cv2.GaussianBlur(sharpen, (0, 0), 3)
    # sharpen = cv2.addWeighted(sharpen, 1.5, blur, -0.5, 0)
    # 得到亮度均值
    avg = cv2.mean(sharpen)[0]
    # print("avg", avg)
    # 直方图均衡化
    equ = gray
    # equ = cv2.equalizeHist(gray)
    # 大津法 二值化
    ret, thresh = cv2.threshold(sharpen, 0, 255, cv2.THRESH_OTSU)
    # 自适应二值化
    # thresh = cv2.adaptiveThreshold(equ,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,11,2)
    cv2.imwrite(outpath + name+"_thresh.jpg", thresh) 
    # cv2.imshow("bin", cv2.resize(thresh, (1024, 1024)))
    # cv2.waitKey(0)
    # 去噪点
    noise = cv2.medianBlur(thresh, 3)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    # 腐蚀
    eroded = cv2.erode(noise, kernel)
    # 膨胀
    rect = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dilated = cv2.dilate(eroded, kernel)
    # cv2.imshow("open", cv2.resize(dilated, (1024, 1024)))
    # cv2.waitKey(0)
    cv2.imwrite(outpath + name+"_dilated.jpg", dilated) 
    binary, contours, hierarchy = cv2.findContours(
        dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    imglist = []
    position = []
    color = (255, 255, 0)
    for c in contours:

        x, y, w, h = cv2.boundingRect(c)
        if (w < 10 or h < 10) or (w == img_width and h == img_height) or (x == 0 and y == 0):
            continue
        temp = thresh[y:(y + h), x:(x + w)]
        meam, stddev = cv2.meanStdDev(temp)
        if stddev < avg * STD_LIMIT:
            continue

        cv2.rectangle(img, (x, y), (x+w, y+h), color, 1)
        # cv2.drawContours(img, [box], 0, color, 2)
        cv2.putText(img, "%d" % (stddev), (x, y),
                    cv2.FONT_HERSHEY_PLAIN, 1.0, color, 1)
        # resized = cv2.resize(temp, (64, 64), interpolation=cv2.INTER_CUBIC)
        imglist.append(temp)
        position.append([x, y, w, h])
    cv2.imwrite('out.jpg',img)
    return imglist, position

path = 'test.png'
if len(sys.argv) == 2:
    path = sys.argv[1]
boxes, postions = loadImg(path)