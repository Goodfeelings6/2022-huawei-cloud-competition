import json
from count_config import count_config
import math

def base_algorithm(data):
    """
    路口车辆流量统计算法
    :param data: dict，key为文件名，value为轨迹记录
    :return ans: dict，存储结果
    """   
    def degree(p0:tuple,p1:tuple,p2:tuple):
        """
        传入三个点的坐标,计算向量 p0p1 和 p1p2 的夹角角度
        """
        # 计算两向量相乘值，以及两向量各自的模
        p0p1_mul_p1p2 = (p1[0]-p0[0])*(p2[0]-p1[0])+(p1[1]-p0[1])*(p2[1]-p1[1])
        p0p1_mod = math.sqrt((p1[0]-p0[0])**2+(p1[1]-p0[1])**2)
        p1p2_mod = math.sqrt((p2[0]-p1[0])**2+(p2[1]-p1[1])**2)
        # 模为0时异常处理
        if p0p1_mod*p1p2_mod == 0:
            #print("模为0错误")
            return 0
        # 计算转弯角度余弦值
        cos_val = p0p1_mul_p1p2/(p0p1_mod*p1p2_mod)
        # 转为角度
        deg = math.acos(cos_val)
        deg = deg/math.pi*180
        return deg
   
    def laneCount(start_box: dict, through_box: dict,end_box:dict, lane_ans: dict, lane_config: dict):
        """
        统计车道流量,由起始点坐标和通过红灯停止线时坐标确定直线,
        用直线与红灯停止线的交点的x坐标判断所属车道。
        :param start_box:车辆起始位置
        :param through_box: 车辆通过红灯停止线时位置
        :param lane_ans: 结果存储
        :param lane_config:车道配置信息
        :return total_lane: 返回当前车辆所在地方的总车道数
        :return lane: 返回当前车辆所属车道
        """
        
        # 计算起始点时和穿过红灯停止线时车辆矩形框中心点坐标
        X1 = start_box['x'] + start_box['w'] / 2
        Y1 = start_box['y'] + start_box['h'] / 2
        X2 = through_box['x'] + through_box['w'] / 2
        Y2 = through_box['y'] + through_box['h'] / 2
        X3 = end_box['x'] + end_box['w'] / 2
        Y3 = end_box['y'] + end_box['h'] / 2

        lane = '0' 
        # 如果数据可以计算斜率
        if X2-X1 != 0 and Y2-Y1!=0:
            # 计算两点连线L的斜率
            k = (Y2-Y1)/(X2-X1)
            # 计算直线L与红灯停止线交叉点的x坐标:x_value
            y_value = (lane_config['2'][1]+lane_config['2'][3])/2
            x_value = X1+(y_value-Y1)/k
            # 判断车道  
            for lane_id in lane_config:
                 # 如果这辆车交叉点的x坐标在这车道内，并且他的 ending_box 中心点小于一个y值（超出一个范围，防止误判），才把它判如此车道内
                if lane_config[lane_id][0] <= x_value <= lane_config[lane_id][2] and Y3<y_value: 
                    #if video_id == 'video01':
                        # print({'car_start_box':start_box,'car_through_box':through_box,'car_end_box':end_box,'car_id':car_id},",")
                    lane_ans[lane_id] = lane_ans[lane_id] + 1
                    lane = lane_id
                    break
        total_lane = len(lane_config)
        return total_lane,lane

    def turnCount(start_box: dict, through_box: dict, end_box: dict, turn_config: dict, turn_ans: dict,total_lane:int,lane:str,isbranch:int):
        """
        统计转向流量。通过三点计算轨迹转向变化角度的余弦值，再结合所属车道和转向阈值判断车辆转向
        :param start_box: 车辆起始位置
        :param through_box: 车辆通过红灯停止线时位置
        :param end_box: 车辆终止位置
        :param turn_config: 转向配置信息
        :param turn_ans: 结果存储
        :param total_lane: 车辆所属地方的总车道数
        :param lane: 车辆所属车道
        :param isbranch: 是否两车道分叉出3车道
        :return:
        """
        # 计算p0,p1,p2 三点坐标
        p0_x, p0_y = start_box['x']+start_box['w']/2, 2000 - (start_box['y']+start_box['h']/2)
        p1_x, p1_y = through_box['x']+through_box['w']/2, 2000 - (through_box['y']+through_box['h']/2)
        p2_x, p2_y = end_box['x']+end_box['w']/2, 2000 - (end_box['y']+end_box['h']/2)
        
        #轨迹运动角度
        deg = degree((p0_x,p0_y),(p1_x,p1_y),(p2_x,p2_y))
        # 左转角
        lt = turn_config['left']
        left_deg = degree(lt[0],lt[1],lt[2])
        # 右转角
        rt = turn_config['right']
        right_deg = degree(rt[0],rt[1],rt[2])
        # 转向判断
        if total_lane==2: # 如果总车道数为2
            if lane=='1':  # 如果当前为第1车道,只可能左转或直行
                if deg >= left_deg and p2_x < p1_x: # 用左转阈值判断
                    turn_ans['left'] += 1
                else:
                    turn_ans['straight'] += 1        
            elif lane=='2': # 如果当前为第2车道,只可能右转或直行
                if deg >= right_deg and p2_x > p1_x: # 用右转阈值判断
                    turn_ans['right'] += 1
                else:
                    turn_ans['straight'] += 1
        elif total_lane==3:  # 如果总车道数为3
            if lane=='1':  # 如果当前为第1车道，只可能左转或直行
                if deg >= left_deg and p2_x < p1_x: # 用左转阈值判断
                    turn_ans['left'] += 1
                else:
                    turn_ans['straight'] += 1    

            elif lane=='2': # 如果当前为第2车道
                if deg >= left_deg and p2_x < p1_x: # 用左转阈值判断
                    turn_ans['left'] += 1
                elif deg >= right_deg and p2_x > p1_x:
                    turn_ans['right'] += 1 
                else:
                    turn_ans['straight'] += 1

            elif lane=='3':  # 如果当前为第3车道，只可能右转或直行
                if  isbranch==1: # 由两车道分叉出3车道
                    turn_ans['right']+=1
                elif deg >= right_deg and p2_x > p1_x: # 用右转阈值判断
                    turn_ans['right'] += 1
                else:
                    turn_ans['straight'] += 1

    # 获取轨迹文件名和每一帧的车辆位置信息
    for filename, car_record in data.items():
        # 获取视频id，用于读取视频对应config
        video_id = filename.split('.')[0]
        video_isbranch = count_config[video_id]['isbranch']
        video_lane = count_config[video_id]['lane']
        video_turn = count_config[video_id]['turn']
        video_area = count_config[video_id]['area']
        video_ans = count_config[video_id]['result']
        # 遍历每一帧各个车辆的位置，按照id存储到list，作为车辆的运动轨迹
        car_routes = {}     
        for frame in car_record:
            for car in frame['cars']:
                x = car['bounding_box']['x']
                y = car['bounding_box']['y']
                X = x + car['bounding_box']['w'] / 2
                Y = y + car['bounding_box']['h'] / 2                
                car_id = car['id']

                #记录轨迹，其中flag标志用以记录过线点（中间点）
                if car_id in car_routes.keys():
                    car_routes[car_id]['track'].append(car['bounding_box'])
                    if car_routes[car_id]['flag']>0 and Y-(video_lane['2'][1]+video_lane['2'][3])/2<0:
                        car_routes[car_id]['flag'] = Y-(video_lane['2'][1]+video_lane['2'][3])/2
                        car_routes[car_id]['idx'] = len(car_routes[car_id]['track'])-1
                # 过滤起始点位于统计区域之外的车辆
                elif Y > video_area[1] and video_area[0] < X < video_area[2]:
                    car_routes[car_id] = {'track':[],'flag':1,'idx':0}
                    car_routes[car_id]['track'].append(car['bounding_box'])

        # 遍历每辆车的轨迹，统计所属车道和转向
        for car_id in car_routes.keys():
            # 过滤只出现5次的误识别框
            if len(car_routes[car_id]['track']) < 6:
                continue
            index=car_routes[car_id]['idx']

            # 从车辆轨迹中取出 起始点，过红灯停止线时点，及终止点
            car_start_box = car_routes[car_id]['track'][1]
            try:
                car_through_box = car_routes[car_id]['track'][index+1]
            except:
                car_through_box = car_routes[car_id]['track'][index]
            car_end_box = car_routes[car_id]['track'][-1]
            
            #print({'car_start_box':car_start_box,'car_through_box':car_through_box,'car_end_box':car_end_box,'car_id':car_id},",")
            
            # 判断车道
            total_lane,lane = laneCount(car_start_box, car_through_box,car_end_box,video_ans, video_lane)
            # 判断转向
            turnCount(car_start_box, car_through_box, car_end_box, video_turn, video_ans, total_lane, lane,video_isbranch)
        return video_ans


# if __name__ == "__main__":  
#     #加载轨迹文件，打印流量统计结果
#     filenames =["video01.position.txt","video03.position.txt","video05.position.txt","video09.position.txt"]
#     for filename in filenames:
#         fileurl = "../position/" + filename
#         car = []
#         with open(fileurl, 'r+', encoding="utf-8") as f:
#             while True:
#                 line = f.readline()
#                 if not line:  # 到 EOF，返回空字符串，则终止循环
#                     break
#                 car.append(json.loads(line))
#         print(filename)
#         result = base_algorithm({filename: car})
#         # 统计结果车道上车辆总数
#         lane_sum = result.get('1')+result.get('2')+result.get('3',0)
#         # 统计结果转向与直行车辆总数
#         turn_sum = result['left']+result['straight']+result['right']
#         print("MyCode: ",result," lane_sum: ",lane_sum," turn_sum: ",turn_sum)
#         # 打印标签数据
#         video_id = filename.split('.')[0]
#         f_label = open("../label/"+video_id+".json",'r',encoding='utf-8')
#         label = json.load(f_label)[video_id]
#         #计算标签总车数
#         sum_label = label.get('1')+label.get('2')+label.get('3',0)
#         print("Label:  ",label," sum_car: ",sum_label)

