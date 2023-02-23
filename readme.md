
# MaxGetter User Manual
## Main Functions
The main function of MaxGetter is to download high-definition images from the maxmara website.

## Installation and Usage

### Preparation
Copy the following files from the repository to the current file:
- The wheel file in the dist folder (or download the source code build).
- settings.toml in the instance folder.

Create a new file secrets.toml in the current folder. The file includes the login password for the MySQL database and the login password for the POP3 email. The contents are as follows:

	# mysql
	MYSQL_PASSWORD = 'yourpassword'
	# mail
	MAIL_SENDER_PASSWORD = 'yourpassword'

Configure the setting.toml file according to the actual needs.

### venv Installation and Usage
Create a venv environment installation.

	python -m venv venv
	.\venv\Scripts\activate
	pip install .\getmax-0.1.3-py3-none-any.whl

check the program entry file if running normally? The result should be:

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

After that, you can initialize the database and start fetching website images.

	runmax --workdir {your_folder} --initdb
	runmax --workdir {your_folder} --rds

### Docker Installation and Usage

Create a Dockfile file in the current folder. The file contents are as follows:

	FROM python:3
	WORKDIR /app
	ENV WORK_DIR /app
	COPY getmax-0.1.3-py3-none-any.whl ./
	RUN pip install getmax-0.1.3-py3-none-any.whl
	CMD ["bash"]

Install the Docker image.

	docker build -t maxgetter .
	docker run -itd --name maxapp -v {your_folder}:/app -v /etc/localtime:/etc/localtime maxgetter
check the program if running normally? The result should be:

	[~] # docker exec -it maxapp runmax --help
	Usage: runmax [OPTIONS]

	Options:
	--workdir TEXT  work directory for this app.
	--initdb        Init database and data.
	-r, --retrieve  Retrieve product and image information, and update to
					database.
	-d, --download  Downlaod the pending images in database.
	-s, --stream    Stream output for log.
	--help          Show this message and exit.
After that, you can initialize the database and start fetching website images.

	docker exec -it maxapp runmax --initdb
	docker exec -it maxapp runmax --rds

### Database
The program supports MySQL and SQLite databases. The parameter DATABASE_TYPE in setting.toml can specify the type of database, such as MySQL or SQLite. 
Before start to retrieve images, following command needs to be executed to initialize the database.
	
	# docker 
	docker exec -it maxapp runmax --initdb
	# env
	runmax --initdb --workdir {your_folder}


### Downloading Images
the command of downloading images is:
	
	# docker 
	docker exec -it maxapp runmax --rds
	# env
	runmax --rds --workdir {your_folder}
