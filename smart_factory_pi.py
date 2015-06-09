from src.flask_server import *

# create log file if it doesn't exist
logs = open('log_file.txt', "a")
logs.close()


if __name__ == "__main__":
	app.run(port = 5000, host='0.0.0.0')