#!/usr/bin/env python3

import rospy
import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal

def move_to_goal(x, y):
    # move_base sunucusuna bağlanıyoruz
    client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
    client.wait_for_server()

    goal = MoveBaseGoal()
    goal.target_pose.header.frame_id = "map"
    goal.target_pose.header.stamp = rospy.Time.now()

    # Hedef koordinatları
    goal.target_pose.pose.position.x = x
    goal.target_pose.pose.position.y = y
    goal.target_pose.pose.orientation.w = 1.0

    rospy.loginfo(f"Hedefe gidiliyor: x={x}, y={y}")
    client.send_goal(goal)
    
    # Robotun hedefe varmasını bekle
    wait = client.wait_for_result()
    if not wait:
        rospy.logerr("Sunucu hatası!")
    else:
        return client.get_result()

if __name__ == '__main__':
    try:
        rospy.init_node('follow_waypoints')

        # GİTMEK İSTEDİĞİN 5 NOKTANIN KOORDİNATLARI
        # Buradaki x ve y değerlerini RViz'deki haritana göre değiştirebilirsin
        waypoints = [
            (-2.0, 1.71),
            (-3.02, -0.30),
            (-1.72, -1.32),
            (0.95, -1.34),
            (-0.01, 1.00)
        ]

        for i, point in enumerate(waypoints):
            rospy.loginfo(f"{i+1}. hedefe hareket başlatıldı.")
            move_to_goal(point[0], point[1])
            rospy.loginfo(f"{i+1}. hedefe ulaşıldı!")

        rospy.loginfo("Tüm hedeflere başarıyla gidildi.")
    except rospy.ROSInterruptException:
        pass
