#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

class ObstacleAvoidance:
    def __init__(self):
        # Düğümü başlatıyoruz
        rospy.init_node('move_stop_rotate_node', anonymous=True)
        
        # Hız komutları için Publisher ve Lidar verisi için Subscriber
        self.pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        self.sub = rospy.Subscriber('/scan', LaserScan, self.scan_callback)
        
        self.vel_msg = Twist()
        
        # Engel algılama mesafesi (Örneğin 0.5 metre)
        self.safe_limit = 0.5 
        self.front_distance = 1.0 # Başlangıçta önü açık varsayıyoruz
        
        # Robotun başlangıç durumu
        self.state = "MOVE" 
        self.rate = rospy.Rate(10) # Saniyede 10 kez çalışacak

    def scan_callback(self, msg):
        # TurtleBot3'te 'msg.ranges[0]' robotun tam ön (0 derece) hizasıdır.
        distance = msg.ranges[0]
        
        # Sensör sonsuz veya hatalı okuma yaparsa diye filtreleme
        if distance == float('inf'):
            self.front_distance = 10.0
        else:
            self.front_distance = distance

    def run(self):
        rospy.loginfo("Move-Stop-Rotate algoritmasi basladi...")
        
        while not rospy.is_shutdown():
            if self.state == "MOVE":
                if self.front_distance > self.safe_limit:
                    # Yol temizse ileri git
                    self.vel_msg.linear.x = 0.2
                    self.vel_msg.angular.z = 0.0
                else:
                    # Engele çok yaklaşıldıysa durumu STOP yap
                    self.state = "STOP"
                    
            elif self.state == "STOP":
                # Robotun tüm hızını sıfırla ve dur
                self.vel_msg.linear.x = 0.0
                self.vel_msg.angular.z = 0.0
                self.pub.publish(self.vel_msg)
                
                rospy.loginfo(f"Engel algilandi! ({self.front_distance:.2f}m) - STOP!")
                rospy.sleep(1.0) # Robotun fiziken durması için 1 saniye bekle
                
                # Durduktan sonra dönüş işlemine geç
                self.state = "ROTATE"
                
            elif self.state == "ROTATE":
                if self.front_distance <= self.safe_limit:
                    # Halen engel varsa kendi ekseninde dön
                    self.vel_msg.linear.x = 0.0
                    self.vel_msg.angular.z = 0.5
                else:
                    # Önü temizlendiği an tekrar harekete geç
                    rospy.loginfo("Yol temizlendi - MOVE!")
                    self.state = "MOVE"

            # Hesaplanmış hız komutunu robota gönder
            self.pub.publish(self.vel_msg)
            self.rate.sleep()

if __name__ == '__main__':
    try:
        robot = ObstacleAvoidance()
        robot.run()
    except rospy.ROSInterruptException:
        pass
