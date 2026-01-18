# -*- coding: UTF-8 -*-
import math
import time
import matatalab # 引入官方硬件库，必须连接 Nous/VinciBot 才能运行

# ==============================================================================
#      0. 硬件环境安全加载 (SAFETY LOAD)
#      [原理]: 防止因为在软件里选错设备（例如选成了不带IMU的普通玛塔小车）
#      导致代码直接报错无法下载。这里会自动检测硬件是否存在。
# ==============================================================================
try:
    # [关键]: 尝试连接陀螺仪(IMU)
    try:
        GYRO_OBJECT = imu 
    except NameError:
        try:
            GYRO_OBJECT = matatalab.imu
        except:
            GYRO_OBJECT = None # 标记为无陀螺仪模式
            
    # [关键]: 尝试连接巡线传感器
    try:
        OFFSET_SENSOR = line_following_sensor
    except NameError:
        try:
            OFFSET_SENSOR = matatalab.line_following_sensor
        except:
            pass      
except ImportError:
    pass

# ==============================================================================
#      1. 用户配置区 (USER CONFIG) 
#      ⚠️ 比赛现场核心区：所有需要调整的参数都在这里
# ==============================================================================

# --- 地图路径指令 (Map String) ---
# [原理]: 机器人像读乐谱一样读取这个字符串，依次执行动作。
# [修改]: 根据实际地图修改数字。
# 1: 前进入格子 (强行穿越虚线/路口)
# 2: 前进走路左侧扫描 (PID巡线，检测到路口停)
# 3: 黑线左转 (IMU 90度)
# 4: 黑线右转 (IMU 90度)
# 5: 掉头 (IMU 180度)
# 6: 前进出格子 (倒车找线出库)
# 7: 前进走路右侧扫描 (特殊巡线)
# 8: 白区左转 (盲转 90度)
# 9: 白区右转 (盲转 90度)
# 0: 识别1次 (显示任务)

#6323224741061061063232222474106106106474722222224741k

# --- 测试地图：走正方形 ---
# 出库 -> 直行 -> 左转 -> 直行 -> 左转 -> 直行 -> 左转 -> 直行 -> 结束
MAP_DATA_STRING = "62323232k"

# --- 测试地图：直线往返 ---
# 出库 -> 直行 -> 掉头 -> 直行 -> 掉头 -> 直行 -> 结束
# MAP_DATA_STRING = "625252k"

# --- 测试地图：全功能综合测试 ---
# 6: 出库 (倒车)
# 2: 巡线 (走到路口停)
# 3: 左转 (90度)
# 2: 巡线
# 1: 穿越路口 (冲过去不停车)
# 2: 巡线
# 5: 掉头 (180度)
# 0: 显示任务
# k: 结束
# MAP_DATA_STRING = "62321250k"


#正式地图
# MAP_DATA_STRING = "6323224741061061063232222474106106106474722222224741k"

# --- 传感器校准 (Sensor Calibration) ---
# [调试]: 现场把车放在黑线上，进入调试页P2查看数值。
# 公式: 设定值 = (黑线读数 + 白地读数) / 2。
# 典型值: 黑线20, 白地90 -> 建议设为 50-55。
THRESHOLD_BLACK = 50    
SENSOR_CENTER   = 3     # 核心传感器ID (3号为中间，用于判断路口停止信号)

# --- 竞速参数 (Speed Params) ---
# [调试]: 如果车容易冲出跑道或打滑，请整体降低这些数值。
SPEED_NORMAL    = 90    # [基础] 标准巡线速度
SPEED_SLOW      = 70    # [稳健] 用于减速或特殊路段

# --- 陀螺仪转弯参数 (Gyro Turn) ---
# [逻辑]: 采用“匀速转弯 + 停车 + 误差修正”策略。
TURN_SPEED_CONST = 50   # [主速] 匀速转弯的速度 (建议40-50。太快刹不住，太慢推不动)
TURN_SPEED_FIX   = 35   # [修速] 误差修正时的点动速度 (越小越准，建议20-30)
TURN_TOLERANCE   = 1    # [容差] 允许的误差范围 (±1度。太小会导致车身左右震荡)

# --- PID 算法参数 (PID Tuning) ---
# [调试]: 巡线效果的核心。
# P (比例): 反应灵敏度。
#    - 现象: 车身画龙(左右剧烈摆动) -> 调小 P (0.2)
#    - 现象: 反应迟钝，冲出弯道 -> 调大 P (0.35)
PID_KP          = 0.25  
# D (微分): 稳定性。
#    - 现象: 走直线不平滑，或者车身有高频抖动(滋滋响) -> 调大 D
PID_KD          = 0.8   

# ==============================================================================
#      2. 全局变量 (Global Variables)
# ==============================================================================
Last_Error = 0          # 记录上一次的巡线误差，用于计算D项
Mission_List = [0]*6    # 存储开机录入的6个任务ID
Current_Mission_ID = 0  # 当前执行到第几个任务
# 任务名称索引表 (录入时显示英文名，防输错)
TASK_NAMES = {
    1:'Sailing', 2:'Cycling', 3:'Gymnastics',
    4:'Weightlift', 5:'Swimming', 6:'Archery',
    7:'Badminton', 8:'Tennis', 9:'Basketball'
}

# ==============================================================================
#      3. 核心算法层 (Core Algorithms) - [机器人的大脑]
# ==============================================================================

def Logic_PID_Line_Follow(run_speed, stop_sensor_position):
    """
    [算法] PID巡线 (带路口检测)
    参数: run_speed(速度), stop_sensor_position(检测哪个传感器停:1左/5右)
    """
    global Last_Error, PID_KP, PID_KD
    stop_sensor_id = 1 if stop_sensor_position == 1 else 5
    
    # [硬件保护]: 防止传感器未连接导致报错死机
    try:
        current_val = line_following_sensor.get_reflection_light(1, stop_sensor_id)
    except: return 

    # [主循环]: 只要没检测到黑线(路口)，就一直根据PID算法调整方向
    # THRESHOLD_BLACK + 5 是为了留一点抗干扰余量，防止影子导致误停
    while current_val >= (THRESHOLD_BLACK + 5):
        # 1. 采集左右传感器数据
        val_left = line_following_sensor.get_reflection_light(1, 2)
        val_right = line_following_sensor.get_reflection_light(1, 4)
        
        # 2. 计算误差 (Error): 左白右黑 -> error>0 -> 需要右转
        error = val_left - val_right
        
        # 3. PID计算: 输出 = P项(当前误差) + D项(误差变化趋势)
        output = (error * PID_KP) + ((error - Last_Error) * PID_KD)
        
        # 4. 限幅保护: 防止计算出极端值 (-60 到 60)，保护电机和机械结构
        output = max(min(output, 60), -60)

        # 5. 执行差速: 左加右减
        speed_l = math.floor(run_speed + output) 
        speed_r = math.floor(run_speed - output)
        servo.set_servo_pwm('1,2', "{},{}".format(speed_l, speed_r))
        
        # 6. 迭代更新: 记录误差供下一次循环使用
        Last_Error = error
        current_val = line_following_sensor.get_reflection_light(1, stop_sensor_id)

def Logic_Gyro_Turn(direction, target_angle):
    """
    [算法] IMU 匀速转弯 + 回正修正 (核心技术)
    逻辑: 1.归零 -> 2.匀速转 -> 3.完全静止 -> 4.检测误差并点动回正
    """
    # [关键步骤1]: 每次转弯前，必须将当前角度归零，消除之前的积累误差
    try:
        imu.set_yaw_to_zero()
        time.sleep(0.05) 
    except: return 
    
    # --- 阶段 1: 匀速主转弯 ---
    if direction == 'left':
        servo.set_servo_pwm('1,2', "{},{}".format(TURN_SPEED_CONST, TURN_SPEED_CONST))
    else:
        servo.set_servo_pwm('1,2', "-{},-{}".format(TURN_SPEED_CONST, TURN_SPEED_CONST))
        
    while True:
        try: current_angle = abs(imu.get_yaw())
        except: break
        # [退出条件]: 转够了角度就立刻停
        if current_angle >= target_angle:
            break 
            
    # --- 阶段 2: 刹车与静止 ---
    # [原理]: 必须让车完全停稳(0.2s)，否则惯性会让陀螺仪读数漂移，导致下面的修正阶段误判
    servo.set_servo_pwm('1,2', "0,0") 
    time.sleep(0.2) 
    
    # --- 阶段 3: 误差修正 (回摆逻辑) ---
    # 最多尝试修正 3 次，防止死循环震荡
    for _ in range(3):
        try: real_angle = abs(imu.get_yaw()) # 再次确认停车后的真实角度
        except: break
        
        diff = real_angle - target_angle # 计算偏差 (正数=过冲，负数=没到位)
        
        # 1. 误差合格(±2度) -> 完美，结束
        if abs(diff) <= TURN_TOLERANCE:
            break
            
        # 2. 判断修正方向
        # 逻辑: 如果过冲了(转多了)就反向回退，如果没到位(转少了)就正向补刀
        if direction == 'left':
            if diff > 0: pwm_str = "-{},-{}".format(TURN_SPEED_FIX, TURN_SPEED_FIX) # 过冲->向右回
            else:        pwm_str = "{},{}".format(TURN_SPEED_FIX, TURN_SPEED_FIX)   # 没到->向左补
        else: # right
            if diff > 0: pwm_str = "{},{}".format(TURN_SPEED_FIX, TURN_SPEED_FIX) # 过冲->向左回
            else:        pwm_str = "-{},-{}".format(TURN_SPEED_FIX, TURN_SPEED_FIX)   # 没到->向右补
                
        # 3. 执行修正 (点动)
        servo.set_servo_pwm('1,2', pwm_str)
        time.sleep(0.1)  # 点动时间极短
        servo.set_servo_pwm('1,2', "0,0")
        time.sleep(0.15) # 等待静止
            
    servo.stop_motor_servo('1,2')

# ==============================================================================
#      4. 动作指令层 (Actions) - [具体招式]
# ==============================================================================

def Action_Line_Follow(mode, next_move):
    """ 
    [动作] 巡线 ('2'/'7') - 带惯性处理
    [逻辑]: 如果下一步还是直行，就不刹车；如果下一步要转弯，就刹车对齐。
    """
    Logic_PID_Line_Follow(SPEED_NORMAL, mode)
    
    # 如果下一步是 '2' 或 '7' (直行)，不刹车，保持动作连贯
    if next_move in ['2', '7']:
        pass 
    else:
        # 下一步是转弯，必须刹车对齐路口
        servo.set_servo_pwm('1,2', '-40,40') # 微调/刹车
        time.sleep(0.13)
        servo.stop_motor_servo('1,2')
        
    global Last_Error
    Last_Error = 0 # 每次重新巡线前，清除历史误差

def Action_Leave_Grid():
    """ 
    [动作] 精准倒车出库 ('6')
    逻辑: 倒车 -> 撞线(车尾) -> 继续倒 -> 摆正(车身)
    """
    servo.set_servo_pwm('1,2', '-80,80') # 开始倒车
    try:
        # 步骤1: 车尾入线 (中间任意传感器变黑)
        while True: 
            s2 = line_following_sensor.get_reflection_light(1, 2)
            s3 = line_following_sensor.get_reflection_light(1, 3)
            s4 = line_following_sensor.get_reflection_light(1, 4)
            if (s2 < THRESHOLD_BLACK) or (s3 < THRESHOLD_BLACK) or (s4 < THRESHOLD_BLACK): break 
        # 步骤2: 车身摆正 (最外侧传感器变黑)
        while True: 
            s1 = line_following_sensor.get_reflection_light(1, 1)
            s5 = line_following_sensor.get_reflection_light(1, 5)
            # 用更严格的阈值(-10)确保踩实
            if (s1 < THRESHOLD_BLACK - 10) or (s5 < THRESHOLD_BLACK - 10): break
    except: pass
    
    # 步骤3: 微调位置
    servo.set_servo_pwm('1,2', '-40,40')
    time.sleep(0.13)
    servo.stop_motor_servo('1,2')

def Action_Crossroad():
    """ 
    [动作] 强行穿越路口 ('1') 
    原理: 巡线传感器遇到十字路口会误停，所以这段必须盲走避开干扰。
    """
    servo.set_servo_pwm('1,2', '-50,50')
    time.sleep(0.1) # 启动
    try:
        # 直走到看到白地 (越过当前的横黑线)
        while not (line_following_sensor.get_reflection_light(1, SENSOR_CENTER) > 80): continue
    except: pass
    # 加速冲过虚线空白区
    servo.set_servo_pwm('1,2', '-90,90')
    time.sleep(0.52) 
    servo.stop_motor_servo('1,2')

def Action_Turn_Left():
    time.sleep(0.05) # 转弯前停顿，消除惯性
    Logic_Gyro_Turn('left', 90)
    time.sleep(0.05)

def Action_Turn_Right():
    time.sleep(0.05)
    Logic_Gyro_Turn('right', 90)
    time.sleep(0.05)

def Action_U_Turn():
    time.sleep(0.05)
    Logic_Gyro_Turn('left', 180)
    time.sleep(0.05)

def Action_Mission_Display():
    """ [动作] 显示任务图标 ('0') """
    global Current_Mission_ID
    if Current_Mission_ID < 6:
        task_code = Mission_List[Current_Mission_ID]
        name = TASK_NAMES.get(task_code, '0000')
        # 逐行显示，方便确认是否正确
        lcd.draw_text(name, 0, 10+(Current_Mission_ID*22), 6, 0x02501d, Current_Mission_ID+1)
        Current_Mission_ID += 1
        time.sleep(1)

# ==============================================================================
#      5. 主程序与UI逻辑 (Main Logic)
# ==============================================================================

def Run_Auto_Mission():
    """ 
    自动跑图主循环 
    包含：指令解析 + 屏幕可视化调试
    """
    map_len = len(MAP_DATA_STRING)
    for i in range(map_len):
        char = MAP_DATA_STRING[i]
        if char == 'k': break 
        
        # [原理]: 偷看一眼下一个动作，决定是否需要刹车衔接
        next_char = MAP_DATA_STRING[i+1] if (i + 1 < map_len) else 'k'
        
        # --- 屏幕可视化调试 (新增) ---
        # 实时显示: 进度 / 当前指令 / 下一个指令
        lcd.clear_screen()
        lcd.draw_text("Step: " + str(i+1) + "/" + str(map_len), 5, 5, 1, 0xffffff, 1)
        lcd.draw_text("NOW: " + str(char), 5, 35, 6, 0x00ff00, 2) 
        lcd.draw_text("NXT: " + str(next_char), 60, 35, 6, 0xffff00, 3) 
        # ---------------------------
        
        if   char == '1': Action_Crossroad()
        elif char == '2': Action_Line_Follow(0, next_char)
        elif char == '7': Action_Line_Follow(1, next_char)
        elif char == '3': Action_Turn_Left()
        elif char == '4': Action_Turn_Right()
        elif char == '5': Action_U_Turn()
        elif char == '6': Action_Leave_Grid() 
        elif char == '0': Action_Mission_Display()
        elif char == '8': Logic_Gyro_Turn('left', 90)
        elif char == '9': Logic_Gyro_Turn('right', 90)

def UI_Select_Missions():
    """ 
    [UI] 任务录入界面 
    包含：数字选择 + 英文名提示，方便对照
    """
    lcd.clear_screen()
    sel = 1
    for i in range(6):
        lcd.clear_screen()
        time.sleep(0.1)
        while not button.is_pressed('right'):
            if button.is_pressed('up'): 
                sel = 1 if sel >= 9 else sel + 1; time.sleep(0.15)
            if button.is_pressed('down'): 
                sel = 9 if sel <= 1 else sel - 1; time.sleep(0.15)
            
            lcd.draw_text("Task " + str(i+1), 5, 5, 6, 0x000000, 1)
            lcd.draw_text("ID: " + str(sel), 40, 25, 6, 0x2793a2, 2)
            # 显示任务名称
            task_name = TASK_NAMES.get(sel, "Unknown")
            lcd.draw_text(task_name, 5, 50, 1, 0x000000, 3)
            time.sleep(0.05)
        
        Mission_List[i] = sel
        lcd.draw_text("Saved!", 85, 5, 6, 0xff0000, 4)
        time.sleep(0.3)
        sel = 1 
    lcd.clear_screen()

@event.start
def on_event_start():
    # --- 1. 任务录入 (开机第一件事) ---
    UI_Select_Missions()
    
    # --- 2. 陀螺仪校准 (提示松手) ---
    lcd.clear_screen()
    lcd.draw_text("Hands Off!", 5, 20, 1, 0xff0000, 1)
    time.sleep(1) 
    try:
        # [关键]: 此时必须保持静止，否则后续所有转弯都会歪
        imu.sensor_calibrate()
        time.sleep(1)
        lcd.draw_text("IMU OK!", 5, 40, 1, 0x00ff00, 1)
        time.sleep(0.5)
    except:
        lcd.draw_text("IMU Error", 5, 40, 1, 0xff0000, 1)
        time.sleep(1)

    # --- 3. 待机与调试 (Ready) ---
    lcd.clear_screen()
    lcd.draw_text("Ready", 5, 5, 6, 0x000000, 1)
    lcd.draw_text("A: Debug", 5, 25, 6, 0xffffff, 2)
    lcd.draw_text("B: Run", 5, 45, 6, 0x00ff00, 3)
    
    while True:
        # B键: 开始比赛
        if button.is_pressed('B'):
            Run_Auto_Mission()
            return 

        # A键: 进入调试模式 (双页菜单)
        if button.is_pressed('A'):
            Debug_Page = 1
            lcd.clear_screen()
            time.sleep(0.5)
            
            while True:
                lcd.clear_screen()
                title = "P" + str(Debug_Page)
                if Debug_Page == 1: title += " Action"
                elif Debug_Page == 2: title += " Sensor"
                lcd.draw_text(title, 2, 2, 6, 0xffffff, 1)

                # B键退出调试
                if button.is_pressed('B'):
                    lcd.clear_screen()
                    lcd.draw_text("Ready", 5, 5, 6, 0x000000, 1)
                    time.sleep(0.5)
                    break 
                
                # A键翻页
                if button.is_pressed('A'):
                    Debug_Page = 1 if Debug_Page >= 2 else Debug_Page + 1
                    time.sleep(0.3)
                
                # --- P1: 动作调试 (用于测试机械和陀螺仪) ---
                if Debug_Page == 1:
                    lcd.draw_text("^Cross vOut", 5, 20, 6, 0xffffff, 2)
                    lcd.draw_text("<L90  >R90", 5, 35, 6, 0xffffff, 3) # 右键已更新为R90
                    try: yaw = imu.get_yaw()
                    except: yaw = "Err"
                    lcd.draw_text("Yaw: " + str(yaw), 5, 50, 6, 0x2793a2, 4)
                    
                    if button.is_pressed('up'):    Action_Crossroad()  # 直冲
                    if button.is_pressed('down'):  Action_Line_Follow(0, '2') # 寻线
                    if button.is_pressed('left'):  Action_Turn_Left()  # 左转
                    if button.is_pressed('right'): Action_Turn_Right() # 右转 (对称测试)
                
                # --- P2: 传感器调试 (用于校准黑线阈值) ---
                elif Debug_Page == 2:
                    try:
                        s1 = line_following_sensor.get_reflection_light(1, 1)
                        s2 = line_following_sensor.get_reflection_light(1, 2)
                        s3 = line_following_sensor.get_reflection_light(1, 3)
                        s4 = line_following_sensor.get_reflection_light(1, 4)
                        s5 = line_following_sensor.get_reflection_light(1, 5)
                        
                        lcd.draw_text("L: " + str(s1) + " " + str(s2), 5, 20, 6, 0xffffff, 2)
                        # 中间数值变绿 = 检测到黑线
                        col = 0x00ff00 if s3 < THRESHOLD_BLACK else 0xffffff
                        lcd.draw_text("M: " + str(s3), 5, 35, 6, col, 3)
                        lcd.draw_text("R: " + str(s4) + " " + str(s5), 5, 50, 6, 0xffffff, 4)
                    except: pass
                    
                time.sleep(0.1)