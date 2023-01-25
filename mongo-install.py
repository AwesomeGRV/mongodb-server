#!/usr/bin/python3

import sys
import os
import json
import shutil
import logging

logging.basicConfig(filename='/var/log/mongo-install.log', format='%(asctime)s, %(msecs)d %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S', level=logging.INFO)

def load_config (config_file_path):
    config_data = {}
    with open(config_file_path) as config_file:
        config_data = json.load(config_file)
    return config_data

def download_binary(url, mongo_home):
    try:
        shutil.rmtree(mongo_home)
    except:
        pass
    os.makedirs(mongo_home)
    cmd = "sudo apt update -y  \nsudo apt-get install -y libcurl4 openssl liblzma5  \ncurl -o "+mongo_home+"/mongodb-6.0.3.tgz "+url
    os.system(cmd)
    logging.info("System updated & mongo binary downloaded.")

def mongo_config(mongo_home):
    cmd = "tar -xvf "+mongo_home+"/mongodb-6.0.3.tgz -C "+mongo_home+" \nmv "+mongo_home+"/mongodb-linux-x86_64-ubuntu2004-6.0.3 "+mongo_home+"/mongodb  \nsudo cp -R "+mongo_home+"/mongodb/bin/mongod /usr/local/bin/mongod  \nsudo chmod +x /usr/local/bin/mongod"
    os.system(cmd)
    logging.info("Mongo binary configured.")
    
def mongo_client_and_mongoConfig_setup(client, mongo_home):
    cmd = "sudo apt-get install -y "+client
    os.system(cmd)
    shutil.copyfile("/home/ubuntu/mongo-setup/mongodb.conf", mongo_home+"/mongodb.conf")
    
def start_script(data_path, service_name, mongo_home):
    try:
        shutil.rmtree(data_path)
    except:
        pass
    os.makedirs(data_path)
    with open("/etc/systemd/system/mongodb.service", "w") as file:
        lines = ["[Unit]\n", "Description=MongoDB Service\n", "Documentation=https://www.mongodb.com/\n\n", "[Service]\n","ExecStart=mongod --config "+mongo_home+"/mongodb.conf --dbpath "+data_path+"\n\n", "[Install]\n", "WantedBy=multi-user.target\n", "Alias=mongodb.service\n"]
        file.writelines(lines)
        file.close()
    cmd = "sudo systemctl start "+service_name
    os.system(cmd)
    logging.info("Mongodb started...")
    
config_data = {}

try:
    config_data = load_config(sys.argv[1])
    download_binary(config_data['url'], config_data['mongo_home']) 
    mongo_config(config_data['mongo_home'])
    mongo_client_and_mongoConfig_setup(config_data['client_name'], config_data['mongo_home'])
    start_script(config_data['data_path'], config_data['service_name'], config_data['mongo_home'])
    
except Exception as exp:
    logging.exception("Mongo installation failed.")
