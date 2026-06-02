ÇALIŞTIRMA ADIMLARI:

Adım 1: Dünyayı ve Robotu Başlatmak için ilk terminalde şu komutları girin:

Bash
export TURTLEBOT3_MODEL=burger
roslaunch turtlebot3_gazebo turtlebot3_world.launch
(Gazebo açıldıktan sonra bu terminali arkada simge durumuna küçült, kapatma).

Adım 2: Yeni bir terminal açın. Önce ödev dosyalarının olduğu klasöre girin ardından yeni terminale

Bash
cd ~/bilgisayarınızda dosyanın konumu neredeyse o konumu girin.

Birinci ödevin çalıştırılması için yeni bir terminal açın ve şu kodları girin:

Bash
./move_stop_rotate.py
(Göstermeyi bitirince Ctrl+C ile durdurun).

İkinci ödevin çalıştırılması için yeni bir terminal açın ve yeni terminale şu kodları girin:

Bash
./pid_controller.py
