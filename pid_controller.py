#!/usr/bin/env python3
import rospy
import math
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

class SmartRobotVacuum:
    def __init__(self):
        rospy.init_node('pid_vacuum_node', anonymous=True)
        self.pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        self.sub = rospy.Subscriber('/scan', LaserScan, self.scan_callback)
        self.vel_msg = Twist()

        # PID Katsayıları (Bu sefer DİREKSİYON/Dönüş için kullanıyoruz)
        self.kp = 1.5  # Direksiyonu kırma hassasiyeti
        self.ki = 0.0  # Sürekli akan sistemde integrale pek ihtiyaç yok
        self.kd = 0.5  # Direksiyonu hızlı toplayıp yalpalamayı önleyen fren

        self.target_distance = 0.6 # Engele bu mesafede direksiyon kırmaya başla
        
        # Sensörden gelecek en yakın mesafeler
        self.min_front = 10.0
        self.min_left = 10.0
        self.min_right = 10.0

        self.prev_error = 0.0
        self.integral = 0.0
        self.prev_time = 0.0
        self.rate = rospy.Rate(10)

    def scan_callback(self, msg):
        # Lidar'ı 3 farklı göz gibi kullanıyoruz: Ön, Sol ve Sağ bölgeler
        front_ranges = msg.ranges[0:30] + msg.ranges[330:359]
        left_ranges = msg.ranges[30:90]
        right_ranges = msg.ranges[270:330]

        # NaN ve Inf hatalarını süzen yardımcı fonksiyon
        def get_min_dist(ranges_array):
            valid = [r for r in ranges_array if not math.isnan(r) and not math.isinf(r) and r > 0.01]
            return min(valid) if valid else 10.0

        self.min_front = get_min_dist(front_ranges)
        self.min_left = get_min_dist(left_ranges)
        self.min_right = get_min_dist(right_ranges)

    def run(self):
        rospy.loginfo("Akilli Robot Supurge (PID Engel Asma) Basladi!")
        rospy.sleep(1)
        self.prev_time = rospy.Time.now().to_sec()

        while not rospy.is_shutdown():
            current_time = rospy.Time.now().to_sec()
            dt = current_time - self.prev_time
            if dt <= 0.0: 
                dt = 0.01

            # Standart Robot Süpürge Davranışı: Sürekli ileri git
            self.vel_msg.linear.x = 0.2
            
            # Eğer önde bir engel varsa PID Direksiyonu devreye girer
            if self.min_front < self.target_distance:
                # Engeli gördük, peki ne tarafa kaçacağız?
                # Sol taraf sağ taraftan daha boşsa direksiyonu sola (pozitif) kır
                if self.min_left > self.min_right:
                    error = self.target_distance - self.min_front 
                else:
                    # Sağ taraf daha boşsa direksiyonu sağa (negatif) kır
                    error = -(self.target_distance - self.min_front) 

                # --- PID DİREKSİYON HESAPLAMASI ---
                proportional = self.kp * error
                self.integral += error * dt
                derivative = self.kd * ((error - self.prev_error) / dt)
                
                angular_speed = proportional + (self.ki * self.integral) + derivative
                
                # Keskin dönüşleri sınırla ki robot devrilmesin
                if angular_speed > 1.5: 
                    angular_speed = 1.5
                elif angular_speed < -1.5: 
                    angular_speed = -1.5
                
                self.vel_msg.angular.z = angular_speed
                
                # Eğer engele çarpmak üzereysek (0.3m'den yakın) direksiyonu kırarken hızı da kes
                if self.min_front < 0.3:
                    self.vel_msg.linear.x = 0.05
                    
                rospy.loginfo(f"Engel! Direksiyon kiriliyor. Donus Hizi: {angular_speed:.2f}")
                
            else:
                # Önümüz tamamen boşsa direksiyonu düz tut
                error = 0.0
                self.integral = 0.0
                self.vel_msg.angular.z = 0.0

            # Komutları motora gönder
            self.pub.publish(self.vel_msg)
            self.prev_error = error
            self.prev_time = current_time
            self.rate.sleep()

if __name__ == '__main__':
    try:
        robot = SmartRobotVacuum()
        robot.run()
    except rospy.ROSInterruptException:
        pass
