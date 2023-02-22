
# MaxGetter使用说明

## 准备工作
从仓库拷贝如下文件到当前文件：
- dist文件夹的wheel文件
- instance文件夹下的settings.toml

在当前该文件夹下新建文件secrets.toml。该文件包括mysql数据登录密码，以及POP3邮件登录密码。内容如下：

	# mysql
	MYSQL_PASSWORD = 'yourpassword'
	# mail
	MAIL_SENDER_PASSWORD = 'yourpassword'

按实际需求配置setting.toml文件。

## venv安装和使用
创建venv环境安装。

	python -m venv venv
	.\venv\Scripts\activate
	pip install .\getmax-0.1.3-py3-none-any.whl

验证程序入口文件运行是否正常? 正常输出结果下：

	(venv) PS D:\CodeWork\ptest> runmax --help
	Usage: runmax [OPTIONS]

	Options:
	--workdir TEXT  work directory for this app.
	--initdb        Init database and data.
	-r, --retrieve  Retrieve product and image information, and update to
					database.
	-d, --download  Downlaod the pending images in database.
	-s, --stream    Stream output for log.
	--help          Show this message and exit.

之后可初始化数据库，并开始拉取网站图片。

	runmax --workdir {your_folder}\ --initdb
	runmax --workdir {your_folder}\ --rds


## Docker安装和使用
在当前文件夹下创建Dockfile文件，文件内容如下：

	FROM python:3
	WORKDIR /app
	ENV WORK_DIR /app
	COPY dailyrun-0.1.0-py3-none-any.whl ./
	COPY getmax-0.1.3-py3-none-any.whl ./
	RUN pip install getmax-0.1.3-py3-none-any.whl -i https://mirrors.aliyun.com/pypi/simple/
	CMD ["bash"]

安装Docker镜像。
	
	docker build -t maxgetter .
	docker run -itd --name maxapp -v /share/fs/max_downlaod:/app -v /etc/localtime:/etc/localtime maxgetter

验证程序入口文件运行是否正常? 正常输出结果下：
	
	[~] # docker exec -it maxtest runmax --help
	Usage: runmax [OPTIONS]

	Options:
	--workdir TEXT  work directory for this app.
	--initdb        Init database and data.
	-r, --retrieve  Retrieve product and image information, and update to
					database.
	-d, --download  Downlaod the pending images in database.
	-s, --stream    Stream output for log.
	--help          Show this message and exit.

之后可初始化数据库，并开始拉取网站图片。
	
	docker exec -it maxapp runmax --initdb
	docker exec -it maxapp runmax --rds