
# MaxmaraGetter说明

## 1、代码修改和维护
### 1.1 建立ven环境，并安装依赖软件包
	
	PS D:\app\getmax>> python -m venv ven
	PS D:\app\getmax>> .\ven\Scripts\activate
	(ven) PS D:\app\getmax>> pip list
	Package    Version
	---------- -------
	pip        22.0.4
	setuptools 58.1.0
	(ven) PS D:\app\getmax>> pip install requests sqlalchemy pymysql Click
	(ven) PS D:\app\getmax>> pip install -e .
	(ven) PS D:\app\getmax>> pip list
	Package            Version   Editable project location
	------------------ --------- -------------------------
	certifi            2022.12.7
	charset-normalizer 2.1.1
	click              8.1.3
	colorama           0.4.6
	getmax             0.1.0     d:\app\getmax
	greenlet           2.0.1
	idna               3.4
	pip                22.0.4
	PyMySQL            1.0.2
	requests           2.28.1
	setuptools         58.1.0
	SQLAlchemy         1.4.45
	urllib3            1.26.13
	(ven) PS D:\app\getmax>>

### 1.2 验证入口程序
验证runmax是否运行正常。需要验证runmax,以及runmax.py都正常运行。
	
	(ven) PS D:\app\getmax>> runmax --help
	Usage: runmax [OPTIONS]

	Options:
	  --env [DEV|TST|PRO]             Envrionment of app.  [required]
	  --initdb                        Init database and data.
	  -d, --download                  Downlaod the pending images in database.
	  -r, --retrieve                  Retrieve product and image information, and
									  update to database.
	  --logfile                       Where log file to save.
	  --loglevel [DEBUG|INFO|WARNING|ERROR]
									  log levels
	  -s, --stream                    Stream output for log.
	  --sendto                        Send email when error occured.
	  --help                          Show this message and exit.
	(ven) PS D:\app\getmax>> python .\getmax\scripts\runmax.py --help
	Usage: runmax.py [OPTIONS]

	Options:
	  --env [DEV|TST|PRO]             Envrionment of app.  [required]
	  --initdb                        Init database and data.
	  -d, --download                  Downlaod the pending images in database.
	  -r, --retrieve                  Retrieve product and image information, and
									  update to database.
	  --logfile                       Where log file to save.
	  --loglevel [DEBUG|INFO|WARNING|ERROR]
									  log levels
	  -s, --stream                    Stream output for log.
	  --sendto                        Send email when error occured.
	  --help                          Show this message and exit.

### 1.3 代码维护
源码位于子目录getmax下。
生产环境需要环境变量支持，设置方法如下（PowerShell）：
	
	$env:DB_USER="root"
	$env:DB_PASSWORD="**"
	$env:DB_HOST="**"
	$env:DB_PORT="3306"
	$env:DB_DATABASE="**"
	$env:FOLDER_SAVE="**"
	
	$env:MAIL_SENDER_SMTP="smtp.qq.com"
	$env:MAIL_SENDER_ADDR="**@qq.com"
	$env:MAIL_SENDER_PASSWORD="**"
	


## 2、单元测试

安装pytest

	pip install pytest coverage
	
运行pytest,如有问题，逐个排查。

	pytest .

对测试覆盖率验证,使用coverage来验证。

	coverage run -m pytest
	coverage report
	coverage html

## 3、程序打包
执行如下命令进行打包

	(ven) PS D:\app\getmax>> pip install build
	(ven) PS D:\app\getmax>> python -m build
	
打包完成之后，可以在dist目录找到打包文件

## 4、在其他机器安装
### 4.1 venv安装
首先安装python,然后将打包的whl文件拷贝过来。之后执行如下命令。

	PS D:\app\tst>> dir
	目录: D:\app\tst
	Mode                 LastWriteTime         Length Name
	----                 -------------         ------ ----
	-a----        2022-12-26     21:59          12215 getmax-0.1.0-py3-none-any.whl

	PS D:\app\tst>> python -m venv venv
	PS D:\app\tst>> .\venv\Scripts\activate
	(venv) PS D:\app\tst>> pip install .\getmax-0.1.0-py3-none-any.whl

之后需确认runmax命令是否可以正常运行。若可以，表示已成功安装。

	(venv) PS D:\app\tst>> runmax --help
	Usage: runmax [OPTIONS]

	Options:
	  --env [DEV|TST|PRO]             Envrionment of app.  [required]
	  --initdb                        Init database and data.
	  -d, --download                  Downlaod the pending images in database.
	  -r, --retrieve                  Retrieve product and image information, and
									  update to database.
	  --logfile                       Where log file to save.
	  --loglevel [DEBUG|INFO|WARNING|ERROR]
									  log levels
	  -s, --stream                    Stream output for log.
	  --sendto                        Send email when error occured.
	  --help                          Show this message and exit.
生产环境的运行，需要设置环境变量，变量设置参考1.3。

### 4.2 Container安装
Dockfile文件：

	FROM python:3
	WORKDIR /app
	COPY getmax-0.1.0-py3-none-any.whl ./
	COPY looprun.py ./
	RUN pip install getmax-0.1.0-py3-none-any.whl -i https://mirrors.aliyun.com/pypi/simple/
	CMD ["/bin/sh"]
安装Docker镜像
	
	[/share/fs/App/maxgeter] # docker build -t maxgetter .
	[/share/fs/App/maxgeter] # docker run -itd --name maxapp -v /share/fs/max_downlaod:/download -v /etc/localtime:/etc/localtime --env-file ./env.list maxgetter python /app/looprun.py --cmd='runmax --env=pro -rds' --times=02:00%11:00%16:00%22:00
	
	
	
### 4.3 指定container的IP地址
	
	docker network create --driver=bridge --subnet=192.168.0.0/24 --ip-range=192.168.0.0/25 --gateway=192.168.0.2 br0
	docker run --name mysql80 -itd --network qnet-static-eth0-0fa2ce --ip 192.168.0.88 -p 3306:3306 -e MYSQL_ROOT_PASSWORD=password mysql:8.0
	docker run --name mydatabase -itd --network bridge--ip 192.168.0.100 -e MYSQL_ROOT_PASSWORD=password mysql:latest
	podman run --name mydatabase -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=password mysql
	podman run --name mypress -d -p 80:80 wrdpress
	# docker run --name mysql80 -itd -p 3306:3306 -v /share/fs/App/MySQL/conf:/etc/mysql/conf.d -v /share/fs/App/MySQL/data:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=password mysql:8.0
	# 需要等约2分钟，容器mysql服务启动完成之后才可以登录使用
	docker exec -it mysql80 bash
	# 设置root用户可以远程登录
	mysql -uroot -ppassword
	mysql> grant all on *.* to 'root'@'%';
	mysql>FLUSH PRIVILEGES;
	mysql>exit
	docker exec -it mysql80 mysql -uroot -ppassword
	
	
### 4.4 定制Container里的系统
Contain里面的系统一般为Ddbain,首先需要更新apt的安装源。安装源文件位于/etc/apt/sources.list. 需替换成如下内容；

	deb http://mirrors.aliyun.com/ubuntu/ bionic main restricted universe multiverse
	deb http://mirrors.aliyun.com/ubuntu/ bionic-security main restricted universe multiverse
	deb http://mirrors.aliyun.com/ubuntu/ bionic-updates main restricted universe multiverse
	deb http://mirrors.aliyun.com/ubuntu/ bionic-proposed main restricted universe multiverse
	deb http://mirrors.aliyun.com/ubuntu/ bionic-backports main restricted universe multiverse
	deb-src http://mirrors.aliyun.com/ubuntu/ bionic main restricted universe multiverse
	deb-src http://mirrors.aliyun.com/ubuntu/ bionic-security main restricted universe multiverse
	deb-src http://mirrors.aliyun.com/ubuntu/ bionic-updates main restricted universe multiverse
	deb-src http://mirrors.aliyun.com/ubuntu/ bionic-proposed main restricted universe multiverse
	deb-src http://mirrors.aliyun.com/ubuntu/ bionic-backports main restricted universe multiverse

然后执行apt update, 会遇到签名的错误提示： The following signatures couldn't be verified because the public key is not available: NO_PUBKEY 3B4FE6ACC0B21F32
需要执行如下命令进行修复.

	gpg --keyserver keyserver.ubuntu.com --recv-keys 3B4FE6ACC0B21F32
	gpg --export --armor 3B4FE6ACC0B21F32 | apt-key add -
	apt update
	
	添加系统定时任务
	apt-get install -y cron vim libsystemd0 networkd-dispatcher libpam-systemd
	crontab -e
	



