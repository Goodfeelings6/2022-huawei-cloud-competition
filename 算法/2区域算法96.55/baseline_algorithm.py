from count_config import count_config
import json

def base_algorithm(data):
    def pointInArea(vertex_set:list, test_point:tuple):
        """
        "引射线法" 判断一个点是否在给定的区域内（多边形区域）
        :param vertex_set: 多边形的顶点集合,每个顶点坐标用一个二元组表示 
        :param test_point: 待测试的点
        :return bool值，点在区域内则返回True,否则False
        """
        # 测试点坐标
        tp_x = test_point[0]
        tp_y = test_point[1]

        vertex_count = len(vertex_set) # 多边形顶点个数
        # 设想从测试点水平向左发出射线, 当坐标系原点位于左上角时，即沿x轴负方向
        count = 0   # 记录射线穿过多边形的边的次数 
        # 对多边形的每一条边测试
        j = vertex_count - 1
        for i in range(0,vertex_count):
            # 顶点1坐标
            vertice1_x = vertex_set[i][0]
            vertice1_y = vertex_set[i][1]
            # 顶点2坐标
            vertice2_x = vertex_set[j][0]
            vertice2_y = vertex_set[j][1]
    
            # 点与多边形顶点重合
            if (vertice1_x == tp_x and vertice1_y == tp_y) or (vertice2_x == tp_x and vertice2_y == tp_y):
                #print("点与多边形顶点重合")
                pass

            # 判断这条边的两端点是否在射线两侧
            if (vertice1_y < tp_y and vertice2_y >= tp_y) or (vertice1_y >= tp_y and vertice2_y < tp_y):
                # 计算边上与射线 Y 坐标相同的点的 X 坐标
                X = vertice1_x + (tp_y - vertice1_y) * (vertice1_x - vertice2_x) / (vertice1_y - vertice2_y)
         
                # 点在多边形的边上
                if(X == tp_x) :
                   #print("点在多边形的边上")
                   pass

                # 射线穿过多边形的边界
                if(X < tp_x) :
                   count+=1
            j = i

        # 射线穿过多边形边界的次数为奇数时点在多边形内
        return (True if count%2==1 else False)

    def turnCount(car_track, turn_config, ans, lane_len, lane, video_id):
        left_count,straight_count,right_count = 0,0,0
        for car_box in car_track:
            X,Y = car_box['x']+car_box['w']/2, car_box['y']+car_box['h']/2
            if pointInArea(turn_config['left'],(X,Y)):
                left_count+=1
            elif pointInArea(turn_config['straight'],(X,Y)):
                straight_count+=1
            elif pointInArea(turn_config['right'],(X,Y)):
                right_count+=1
        if lane_len==2:
            if lane=='1':
                if left_count!=0 and left_count >= straight_count and left_count >= right_count:
                    ans['left'] += 1
                elif straight_count!=0 and straight_count >= left_count and straight_count >= right_count:
                    ans['straight'] += 1
                else:
                    ans['straight'] += 1
            elif lane=='2':
                if right_count!=0 and right_count >= straight_count and right_count >= left_count:
                    ans['right'] += 1
                elif straight_count!=0 and straight_count >= left_count and straight_count >= right_count:
                    ans['straight'] += 1
                else:
                    ans['straight'] += 1
        elif lane_len==3:
            if lane=='1':
                if left_count!=0 and left_count >= straight_count and left_count >= right_count:
                    ans['left'] += 1
                elif straight_count!=0 and straight_count >= left_count and straight_count >= right_count:
                    ans['straight'] += 1   
                else:
                    ans['straight'] += 1
            elif lane=='2':
                if left_count!=0 and left_count >= straight_count and left_count >= right_count:
                    ans['left'] += 1
                elif straight_count!=0 and straight_count >= left_count and straight_count >= right_count:
                    ans['straight'] += 1
                elif right_count!=0 and right_count >= straight_count and right_count >= left_count:
                    ans['right'] += 1
                else:
                    ans['straight'] += 1
            elif lane=='3':
                # if video_id != 'video05' and video_id != 'video06':
                #     ans['right'] += 1
                # else:    
                #     if right_count!=0 and right_count >= straight_count and right_count >= left_count:
                #         ans['right'] += 1
                #     elif straight_count!=0 and straight_count >= left_count and straight_count >= right_count:
                #         ans['straight'] += 1
                #     else:
                #         ans['straight'] += 1
                if right_count!=0 and right_count >= straight_count and right_count >= left_count:
                    ans['right'] += 1
                elif straight_count!=0 and straight_count >= left_count and straight_count >= right_count:
                    ans['straight'] += 1
                else:
                    ans['straight'] += 1

    def laneCount_area(car_track: list, ans: dict, lane_config: dict, lane_line_config: dict):
        """
        统计车道流量
        :param car_track:车辆运动轨迹
        :param ans: 结果存储
        :param lane_config:车道配置信息
        :return lane_len: 返回当前车辆所在地方的总车道数
        :return lane: 返回当前车辆所属车道
        """
        lane = '0'
        end_car_box = car_track[-1]
        y = end_car_box['y'] + end_car_box['h'] / 2
        if y > (lane_line_config['2'][1] + lane_line_config['2'][3]) / 2:
            return lane
        # 统计轨迹出现在指定区域的次数
        first_count,second_count,third_count = 0,0,0
        lane_len = len(lane_config)
        if lane_len == 3:
            for car_box in car_track:
                # 计算矩形框中心点坐标
                X,Y = car_box['x']+car_box['w']/2, car_box['y']+car_box['h']/2
                # 判定点所在区域
                if pointInArea(lane_config['1'],(X,Y)): # 1
                    first_count+=1
                elif pointInArea(lane_config['2'],(X,Y)): # 2
                    second_count+=1
                elif pointInArea(lane_config['3'],(X,Y)): # 3
                    third_count+=1
        elif lane_len == 2:
            for car_box in car_track:
                # 计算矩形框中心点坐标
                X,Y = car_box['x']+car_box['w']/2, car_box['y']+car_box['h']/2
                # 判定点所在区域
                if pointInArea(lane_config['1'],(X,Y)): # 1
                    first_count+=1
                elif pointInArea(lane_config['2'],(X,Y)): # 2
                    second_count+=1
        # 比较并确定车道
        if first_count!=0 and first_count >= second_count and first_count >= third_count: # 1
            ans['1'] += 1
            lane = '1'
        elif second_count!=0 and second_count >= first_count and second_count >= third_count: # 2
            ans['2'] += 1
            lane = '2'
        elif third_count!=0 and third_count >= first_count and third_count >= second_count: # 3
            ans['3'] += 1
            lane = '3'
        return lane

    for filename, car_record in data.items():
        video_id = filename.split('.')[0]
        video_lane_line = count_config[video_id]['lane_line']
        video_lane = count_config[video_id]['lane']
        video_turn = count_config[video_id]['turn']
        video_area = count_config[video_id]['area']
        ans = {}
        for key in video_lane.keys():
            ans[key] = 0
        ans.update({'left': 0, 'straight': 0, 'right': 0})
        car_routes = {}     
        for frame in car_record:
            for car in frame['cars']:
                x = car['bounding_box']['x']
                y = car['bounding_box']['y']
                X = x + car['bounding_box']['w'] / 2     
                Y = y + car['bounding_box']['h'] / 2           
                car_id = car['id']
                if car_id in car_routes.keys():
                    car_routes[car_id]['track'].append(car['bounding_box'])
                elif Y > video_area[1] and video_area[0] < X < video_area[2]:
                    car_routes[car_id] = {'track':[]}
                    car_routes[car_id]['track'].append(car['bounding_box'])
        for car_id in car_routes.keys():
            if len(car_routes[car_id]['track']) < 6:
                continue
            lane = laneCount_area(car_routes[car_id]['track'], ans, video_lane, video_lane_line)
            lane_len = len(video_lane)
            turnCount(car_routes[car_id]['track'], video_turn, ans, lane_len, lane, video_id)
        # if video_id=="video06":
        #     ans["straight"]-=1
        return ans


if __name__ == "__main__":  
    
    #加载轨迹文件，打印流量统计结果
    filenames =["video01.position.txt","video03.position.txt","video05.position.txt","video09.position.txt"]
    for filename in filenames:
        fileurl = "./position/" + filename
        car = []
        with open(fileurl, 'r+', encoding="utf-8") as f:
            while True:
                line = f.readline()
                if not line:  # 到 EOF，返回空字符串，则终止循环
                    break
                car.append(json.loads(line))
        print(filename)
        result = base_algorithm({filename: car})
        # 统计结果车道上车辆总数
        lane_sum = result.get('1')+result.get('2')+result.get('3',0)
        # 统计结果转向与直行车辆总数
        turn_sum = result['left']+result['straight']+result['right']
        print("MyCode: ",result," lane_sum: ",lane_sum," turn_sum: ",turn_sum)
        # 打印标签数据
        video_id = filename.split('.')[0]
        f_label = open("./label/"+video_id+".json",'r',encoding='utf-8')
        label = json.load(f_label)[video_id]
        #计算标签总车数
        sum_label = label.get('1')+label.get('2')+label.get('3',0)
        print("Label:  ",label," sum_car: ",sum_label)