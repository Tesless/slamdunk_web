#! /usr/bin/python2.7
import string
import rospy
from scout_msgs.msg import ScoutStatus
from geometry_msgs.msg import Point
from datetime import datetime
import pymongo
import test

myclient = pymongo.MongoClient('mongodb+srv://tesless:123@cluster0.xyeyaz7.mongodb.net/test')

mydb = myclient['slamdunk']

mycol = mydb["status"]
mycol2 = mydb["position"]

# 콜백 함수입니다. 이미지 메시지를 수신할 때마다 실행됩니다.
def status_callback(msg):
    print("Receiving Status Value. ",datetime.now().strftime('%y-%m-%d-%H:%M:%S'))
    try:
        motor_states_index = str((msg.motor_states)[0])
        motor_states_rpm = motor_states_index[(motor_states_index.index("rpm:")+5):(motor_states_index.index("temperature:"))]
        motor_states_temperature = motor_states_index[(motor_states_index.index("temperature:")+12):-1]
        # print("rpm: ",type(motor_states_rpm),motor_states_rpm,"temperature: ",type(motor_states_temperature),motor_states_temperature)
        mydict = {"TimeStamp":(datetime.now()), 
                  "header_seq": int(msg.header.seq),
                  "linear_velocity": float(msg.linear_velocity),
                  "angular_velocity": float(msg.angular_velocity),
                  "transverse_linear_velocity": float(msg.transverse_linear_velocity),
                  "base_state": int(msg.base_state),
                  "control_mode": int(msg.control_mode),
                  "fault_code": int(msg.fault_code),
                  "battery_voltage": float(msg.battery_voltage),
                  "motor_states_rpm":float(motor_states_rpm),
                  "motor_states_temperature":float(motor_states_temperature),
                  "light_control_enabled":bool(msg.light_control_enabled),
                  "front_light_state_mode":int(msg.front_light_state.mode),
                  "front_light_state_custom_value":int(msg.front_light_state.custom_value),
                  "rear_light_state_mode":int(msg.rear_light_state.mode),
                  "rear_light_state_custom_value":int(msg.rear_light_state.custom_value)
                  
                  }
    except :
        print("에러")
    else:
        print("/ScoutStatus DB 저장 성공")
        # mongodb_detect()
    

    x = mycol.insert_one(mydict)
    
def status_callback2(msg):
    print("Receiving Status Value. ",datetime.now().strftime('%y-%m-%d-%H:%M:%S'))
    try:
        mydict = {"TimeStamp":(datetime.now()), 
                  "x":float(msg.x),
                  "y":float(msg.y),
                  "z":float(msg.z)}
    except :
        print("에러")
    else:
        print("/Amcl_pose DB 저장 성공")
        # mongodb_detect()
    

    x = mycol2.insert_one(mydict)

        


def main():
    scout_status = "/scout_status"
    scout_status2 = "/amcl_pose"
    # 노드를 초기화합니다.
    rospy.init_node('status_listener')
    # 토픽을 구독합니다. (queue_size 속도 조절?)
    rospy.Subscriber(scout_status, ScoutStatus, status_callback,queue_size=1)
    
    rospy.spin()
    rospy.init_node('status_listener2')
    rospy.Subscriber(scout_status2, Point, status_callback2,queue_size=1)
    rospy.spin()



if __name__ == '__main__':
    main()
    