import cv2 as cv
import os
import json
import numpy
from count_config import count_config

if __name__ == "__main__":
    # 车道信息
    image_from_path = 'pre_image' # 图片来源路径
    label_save_path = 'label_image_area' # 结果保存路径

    # 检查结果保存路径是否存在，不存在则新建
    if not os.path.exists(label_save_path):
        os.mkdir(label_save_path)
    # 读取所有图片
    for root,dirs,files in os.walk(image_from_path):
        # 对每一张图片
        for image in files:
            if image.split('.')[1] == "JPG":
                img = cv.imread(image_from_path + '/' +image)
                video_id = image.split('.')[0]
                print(video_id)
                # 读取配置信息
                video_lane = count_config[video_id]['lane']
                video_turn = count_config[video_id]['turn']
                video_area = count_config[video_id]['area']
                # # 画车道标识
                # for i,(lane,pos) in enumerate(video_lane.items()):
                #     cv.line(img,(pos[0],pos[1]),(pos[2],pos[3]),(40*(i+1),60*(i+1),255-70*i),20)
                #     cv.putText(img, lane, (pos[0],pos[1]+100), cv.FONT_HERSHEY_COMPLEX, 5, (100, 88, 230), 10)
                # 画area
                cv.line(img,(video_area[0],video_area[1]),(video_area[2],video_area[3]),(100,200,230),20)
                # 画车道判定区域
                # 读取配置信息
                lane1 = video_lane['1']
                lane2 = video_lane['2']
                lane3 = video_lane.get('3',[])
                # 画左区域
                vertice1 = lane1[-1]
                for vertice2 in lane1:
                    cv.line(img,vertice1,vertice2,(255,255,0),10)
                    vertice1 = vertice2
                # 画中间区域
                vertice1 = lane2[-1]
                for vertice2 in lane2:
                    cv.line(img,vertice1,vertice2,(160,32,240),10)
                    vertice1 = vertice2
                # 画右区域
                if len(lane3)!=0:
                    vertice1 = lane3[-1]
                    for vertice2 in lane3:
                        cv.line(img,vertice1,vertice2,(0,97,255),10)
                        vertice1 = vertice2

                # 画转向判定区域
                # 读取配置信息
                left_area = video_turn['left']
                straight_area = video_turn['straight']
                right_area = video_turn['right']
                # 画左区域
                vertice1 = left_area[-1]
                for vertice2 in left_area:
                    cv.line(img,vertice1,vertice2,(255,0,0),10)
                    vertice1 = vertice2
                # 画中间区域
                vertice1 = straight_area[-1]
                for vertice2 in straight_area:
                    cv.line(img,vertice1,vertice2,(0,0,255),10)
                    vertice1 = vertice2
                # 画右区域
                vertice1 = right_area[-1]
                for vertice2 in right_area:
                    cv.line(img,vertice1,vertice2,(0,255,0),10)
                    vertice1 = vertice2

                # #画 转向角度判断线
                # left = video_turn['left']  
                # cv.line(img,left[0],left[1],(255,0,0),10)
                # cv.line(img,left[1],left[2],(255,0,0),10)
                # right = video_turn['right']
                # cv.line(img,right[0],right[1],(0,255,0),10)
                # cv.line(img,right[1],right[2],(0,255,0),10)


                # 绘制好的图片写入指定路径
                cv.imwrite(label_save_path + '/' + image , img)
                print("图片" + image + " 的车道信息、area信息标注完毕，并保存成功")