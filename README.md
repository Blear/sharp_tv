# sharp_tv
Home Assistant Components Sharp TV Remote 

夏普电视遥控app抓包写的HomeAssistant组件,电视关机后无法通信控制,所以采用HDMI CEC来控制电视的开机。

使用前提：
1.你的树莓派必须使用hdmi连接电视
2.电视支持HDMI CEC (需要在电视设置中打开)
3.已安装LIBCEC

HDMI CEC组件官方文档：
https://www.home-assistant.io/components/hdmi_cec/

如何查看是否支持HDMI CEC：
在命令行中输入：echo scan | cec-client -s -d 1 
前提是已安装LIBCEC,具体安装方法看上面的官方文档
如果你和我一样是docker安装的hassio的话,那么不需要自己安装LIBCEC,因为hassio已经帮你安装好了,执行这个命令需要进入hassio容器内部。
$ docker ps  #查看容器
$ docker exec -it 775c7c9ee1e1 /bin/bash #进入容器 775c7c9ee1e1是你的home-assistant的容器id
$ echo scan | cec-client -s -d 1
执行返回：
opening a connection to the CEC adapter...
requesting CEC bus information ...
CEC bus information
===================
device #0: TV
address:       0.0.0.0
active source: no
vendor:        Unknown
osd string:    TV
CEC version:   1.4
power status:  on	#电源状态
language:      ???


device #1: Recorder 1
address:       1.0.0.0
active source: no
vendor:        Pulse Eight
osd string:    CECTester
CEC version:   1.4
power status:  on
language:      eng

修改configuration.yaml添加以下代码

media_player:
  - platform: sharp_tv
    host: 192.168.8.109
    port: 9688
hdmi_cec:
  devices:
    TV: 0.0.0.0
    Pi: 1.0.0.0

电视的电源状态开关通过检测电视的端口是否打开来判断的，电视开机启动后，需要初始化一段时间，才会开放端口，关闭电视同理，关机也需要时间。所以开关机操作有一小段时间的延迟。
