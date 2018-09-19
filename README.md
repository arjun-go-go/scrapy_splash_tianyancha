# scrapy_splash天眼查爬虫
通过Docker安装splash
#从docker hub下载相关镜像文件
sudo docker pull scrapinghub/splash

启动splash服务
使用docker启动服务命令启动Splash服务
#启动splash服务，并通过http，https，telnet提供服务
#通常一般使用http模式 ，可以只启动一个8050就好
sudo docker run -p 8050:8050 scrapinghub/splash

