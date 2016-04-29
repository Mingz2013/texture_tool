#!/usr/bin/env python
__author__ = 'zhaojm'





import sys
import os
import Image



result_list = []    # 最终的 数据列表
rect_list = []  # 空的 矩形 列表

result_w = result_h = 2 # 最终 大图的  宽高



def cmpImg(x, y):
    x_img = x
    w, h = x_img.size
    x_size = w * h
    y_img = y
    w, h = y_img.size
    y_size = w * h
    if x_size > y_size:
        return -1
    elif x_size < y_size:
        return 1
    else:
        return 0
    pass

def cmpRect(x, y):
    x_size = x[2] * x[3]
    y_size = y[2] * y[3]
    if x_size > y_size:
        return -1
    elif x_size < y_size:
        return 1
    else:
        return 0
    pass

def doResultList():
    global result_h, result_w, result_list
    bigImg = Image.new('RGBA', (result_w, result_h), (0, 0, 0, 0))
    for result in result_list:
        rect = result[1]
        bigImg.paste(result[0], (rect[0], rect[1], rect[0] + rect[2], rect[1] + rect[3]))
        pass
    bigImg.save('test2.png')
    bigImg.show()
    pass

def resetBigImg():
    global result_h, result_w, result_list, rect_list
    result_list = []
    rect_list = []
    if result_w <= result_h:
        result_w = result_w * 2
    else:
        result_h = result_h * 2

    rect_list.append((0, 0, result_w, result_h))
    pass

def downImg(img):
    global rect_list, result_list
    w, h = img.size
    down = False
    for rect in rect_list:

        if w <= rect[2] and h <= rect[3]: # 可以放下

            down = True
            result_list.append((img, (rect[0], rect[1], w, h)))

            right_rect = (rect[0] + w, rect[1], rect[2] - w, h)
            bottom_rect = (rect[0], rect[1] + h, rect[2], rect[3] - h)

            if (right_rect[2] > 0) and (right_rect[3] > 0):
                rect_list.append(right_rect)
                pass
            if (bottom_rect[2] > 0) and (bottom_rect[3] > 0):
                rect_list.append(bottom_rect)
                pass
            rect_list.remove(rect)
            rect_list.sort(cmpRect)
            return down

    return down


def doImgList(imgList, rootPath):


    down = True
    for image in imgList:
        down = downImg(image)

        if not down:
            break

    if not down:
        resetBigImg()
        # print(imgList, global_list.result_w, global_list.result_w, global_list.rect_list, global_list.result_list)

        doImgList(imgList, rootPath)
    else:
        # print(global_list.result_list)
        doResultList()


    pass



def doPath(imgList, path):

    for root, dirs, files in os.walk(path):

        for f in files:
            filePath = os.path.join(root, f)
            print(filePath)
            if filePath[-3:] == 'jpg' or filePath[-3:] == 'png':# TODO 修改为二进制检测
                im = Image.open(filePath)

                imgList.append(im)

        # for d in dirs:
        #     dirPath = os.path.join(root, d)
        #     doPath(imgList, dirPath)

    pass






def pack(path):
    print('path=', path)
    imgList = []
    doPath(imgList, path)
    # print(imgList)
    imgList.sort(cmpImg)
    doImgList(imgList, path)
    pass



def main(argv):
    # print('hello python')
    # for arg in argv:
    #     print arg

    global rect_list, result_w, result_h

    rect_list.append((0, 0, result_w, result_h))

    pack(argv[1])

    pass


if __name__ == '__main__':
    main(sys.argv)