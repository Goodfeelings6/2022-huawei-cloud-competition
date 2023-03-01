import cv2 as cv
import os
import json
import numpy
from count_config import count_config


def video2picture(video_path,save_path,start_frame,frame_rate):
    """
    从视频间隔指定帧提取图片
    :param video_path:源视频路径（此处为.mp4文件）
    :param save_path:图片保存路径（文件夹）
    :param start_frame:表示从第几帧开始截取（int）
    :param frame_rate:帧数截取间隔（int）
    """
    # 与视频建立联系
    cap = cv.VideoCapture(video_path)
    # 检查结果保存路径是否存在，不存在则新建
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    
    # 开始捕获
    fCount = 0  # 帧计数器
    while (True):
        fCount += 1 # 帧数递增
        ret, frame = cap.read() # 获取一帧
        if ret: # 当上文成功获取帧时
            if (fCount >= start_frame and (fCount-start_frame) % frame_rate == 0): # 在指定帧下
                # 这里就可以做一些操作了，保存截取帧到本地
                print("开始截取视频第：" + str(fCount) + " 帧")
                cv.imwrite(save_path + '/' + str(fCount) + '.jpg', frame) # 以帧数为名字保存
                print("视频第：" + str(fCount) + " 帧保存成功")
        else:
            print("已无帧可存")
            break
    # 释放资源
    cap.release()

def label_image(position_path,image_dir_path,save_path):
    """
    把车辆矩形框标注在图片上显示
    :param position_path:轨迹文件路径（此处为txt文件）
    :param image_dir_path:图片来源路径（文件夹）
    :param save_path:标注后图片保存路径（文件夹）
    """
    # 读取轨迹文件
    f = open(position_path,'r',encoding='utf-8')
    car_id2color = {}
    while(1):
        # 对每一行进行处理
        line = f.readline()
        if not line:  # 到 EOF，返回空字符串，则终止循环
            break
        frame_label = json.loads(line) # 当前帧标注数据
        timestamp = frame_label['timestamp']
        cars = frame_label['cars']
        # 读取对应图片
        img = cv.imread(image_dir_path + '/' + str(timestamp) + '.jpg')
        # 对每辆车
        for car in cars:
            x1 = car['bounding_box']['x']
            y1 = car['bounding_box']['y']
            x2 = x1 + car['bounding_box']['w']
            y2 = y1 + car['bounding_box']['h']
            car_id = car['id']
            if car_id not in car_id2color: # 当前车第一次出现
                # 随机生成三原色
                r = numpy.random.randint(0,256)
                g = numpy.random.randint(0,256)
                b = numpy.random.randint(0,256)
                car_id2color[car_id] = (b,g,r)
            label_color = car_id2color[car_id] # 用 car_id 对应该车的标注颜色
            # 画矩形框标注
            img = cv.rectangle(img, (x1,y1), (x2,y2), label_color, 10)

        # 检查结果保存路径是否存在，不存在则新建
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        # 绘制好框线的图片写入指定路径
        cv.imwrite(save_path + '/' + str(timestamp) + '.jpg' , img)
        print("视频第：" + str(timestamp) + " 帧车辆矩形框标注完毕，并保存成功")

def msg_image(image_dir_path,save_path,video_id):
    """
    把车道信息、area信息、转向判定区域标注在图片上显示
    :param image_dir_path:图片源路径（文件夹）
    :param save_path:图片保存路径（文件夹）
    :param video_id:标识图片源来自于哪个视频
    """
    # 检查结果保存路径是否存在，不存在则新建
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    # 读取配置信息
    video_lane = count_config[video_id]['lane']
    video_turn = count_config[video_id]['turn']
    video_area = count_config[video_id]['area']
    
    # 读取所有图片
    for root,dirs,files in os.walk(image_dir_path):
        # 对每一张图片
        for image in files:
            img = cv.imread(image_dir_path + '/' +image)
            # 画车道标识
            for i,(lane,pos) in enumerate(video_lane.items()):
                cv.line(img,(pos[0],pos[1]),(pos[2],pos[3]),(40*(i+1),60*(i+1),255-70*i),20)
                cv.putText(img, lane, (pos[0],pos[1]+100), cv.FONT_HERSHEY_COMPLEX, 5, (100, 88, 230), 10)
            #画 转向角度判断线
            left = video_turn['left']  
            cv.line(img,left[0],left[1],(255,0,0),10)
            cv.line(img,left[1],left[2],(255,0,0),10)
            right = video_turn['right']
            cv.line(img,right[0],right[1],(0,255,0),10)
            cv.line(img,right[1],right[2],(0,255,0),10)
            
            # 画area
            cv.line(img,(video_area[0],video_area[1]),(video_area[2],video_area[3]),(150,180,230),20)
            # # 画转向判定区域
            # # 读取配置信息
            # left_area = video_turn['left_area']
            # straight_area = video_turn['straight_area']
            # right_area = video_turn['right_area']
            # # 画左区域
            # vertice1 = left_area[-1]
            # for vertice2 in left_area:
            #     cv.line(img,vertice1,vertice2,(255,0,0),10)
            #     vertice1 = vertice2
            # # 画中间区域
            # vertice1 = straight_area[-1]
            # for vertice2 in straight_area:
            #     cv.line(img,vertice1,vertice2,(0,0,255),10)
            #     vertice1 = vertice2
            # # 画右区域
            # vertice1 = right_area[-1]
            # for vertice2 in right_area:
            #     cv.line(img,vertice1,vertice2,(0,255,0),10)
            #     vertice1 = vertice2
            # 绘制好的图片写入指定路径
            cv.imwrite(save_path + '/' + image , img)
            print("视频第：" + image + " 帧车道信息、area信息、转向判定区域标注完毕，并保存成功")

def picture2video(image_dir_path,save_path,video_name,fps):
    """
    把众多图片合成视频
    :param image_path:源图片文件夹路径（文件夹）
    :param save_path:视频保存路径（文件夹）
    :param video_name:视频名称（string）
    :param fps:合成视频的帧频（int）
    """

    # 路径分隔符最好使用“/”,而不是“\”,“\”本身有转义的意思；或者“\\”也可以。
    image_name_lst = []
    # 获取目录下文件名列表（所有图片名）
    for root ,dirs, files in os.walk(image_dir_path):
        for image_name in files:
            image_name_lst.append(image_name)  
    # 图片排个序,按序号
    image_name_lst.sort(key=lambda x:int(x.split('.')[0]))
    print(image_name_lst)
    # 如果图片列表不为空
    image_count = len(image_name_lst)
    if image_count != 0:
        # VideoWriter是cv2库提供的视频保存方法
        # fourcc 指定编码器
        fourcc = cv.VideoWriter_fourcc(*'mp4v')
        # fps = 5代表视频的帧频为5，如果图片不多，帧频最好设置的小一点
        # video_size(元组) 是生成的视频像素，一般要与所使用的图片像素大小一致，否则生成的视频无法播放
        w = cv.imread(image_dir_path + '/' + image_name_lst[0]).shape[1]
        h = cv.imread(image_dir_path + '/' + image_name_lst[0]).shape[0]
        video_size = (w,h)
        print('视频像素: ',video_size)  

        # 定义保存视频目录及名称和压缩格式，像素为 video_size  
        video = cv.VideoWriter(save_path+'/'+video_name,fourcc,fps,video_size)

        for idx,image_name in enumerate(image_name_lst):
            #读取图片
            img = cv.imread(image_dir_path + '/' + image_name)     
            # 写入视频
            video.write(img)
            print("已写入 ",idx+1,"/",image_count)
        print("视频",video_name,"已成功合成并保存")
        # 释放资源
        video.release()
    else:
        print("失败！图片路径文件夹下没有图片")

if __name__ == "__main__":
    video_id = ["video01"]#,"video03","video05","video09"]
    # 对每个视频
    for id in video_id:
        # # 帧提取
        video_path = "C:/Users/lenovo/Desktop/data/video/"+id+".mp4"
        frame_save_path = "C:/Users/lenovo/Desktop/data/video/"+id+"_image"
        #video2picture(video_path,frame_save_path,11,12)

        # 帧打标
        position_path = "C:/Users/lenovo/Desktop/data/position/"+id+".position.txt"
        label_save_path = "C:/Users/lenovo/Desktop/data/video/"+id+"_label_image"
        label_image(position_path,frame_save_path,label_save_path)

        # 渠化关键信息
        msg_image(label_save_path,label_save_path,id)

        # 帧合并
        video_save_path = "C:/Users/lenovo/Desktop/data/video"
        video_name = id+"_label.mp4"
        #picture2video(label_save_path,video_save_path,video_name,12)




