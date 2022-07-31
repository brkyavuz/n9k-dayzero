import json
from flask import Flask, redirect, render_template, url_for, request, flash, jsonify
from werkzeug.utils import secure_filename
from nornir import InitNornir
from nornir.core.filter import F
from nornir_scrapli.tasks import send_configs
from parser import Parser
from helpers import render_config_data, write_config_data, CONFIG_OPTIONS
import pathlib
import pandas as pd
import yaml
import sys
import os
import random

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SECRET_KEY"] = "aSecretKey"
app.config["UPLOAD_FOLDER"] = BASE_DIR


def send_configs_from_file(task, filename):
	config_dir = f"n9k-configs/{task.host.name}/{filename}"

	with open(config_dir) as f:
		data = f.read()
		commands = data.split('\n')
		commands = [command.lstrip() for command in commands if command != "!" ]


	task.run(task=send_configs, configs=commands)
	

def get_inventory(target_hosts=[]):
    nr = InitNornir("config.yaml")
    if target_hosts:
        return nr.filter(F(name__any=target_hosts))
    else:
        return nr.filter()

def generate_inventory(filename):
	df = pd.read_excel(filename)

	if df[["name", "hostname", "groups"]].isnull().values.any():
		return "mandatory columns (name, hostname and groups) are can not be empty"
	else:
		hosts = {}

		rows = df.values.tolist()
		for row in rows:
			name, hostname,port, username, password, groups = row
			hosts[name] = {
				"hostname":hostname,
				"port": port if not pd.isna(port) else 22,
				"username": username if not pd.isna(username) else None,
				"password": password if not pd.isna(password) else None,
				"groups": groups.split(",")
				}
		f = open('hosts.yaml', 'w+')
		yaml.dump(hosts, f, allow_unicode=True)

def generate_configuration(filename):
	p = Parser(excel_file=filename)
	parsed_features = p.feature_parser()
	parsed_vpc = p.vpc_parser()
	parsed_vlan = p.vlan_parser()
	parsed_l3interfaces = p.cfg_parser("l3interfaces")
	parsed_pc = p.cfg_parser("portchannels")
	parsed_l2interfaces = p.cfg_parser("l2interfaces")
	parsed_stp = p.stp_parser()
	base_dir = f"n9k-configs/"
	pathlib.Path(base_dir).mkdir(parents=True, exist_ok=True)

	cfg = {}
	cfg["features"] = parsed_features
	cfg["vpc"] = parsed_vpc
	cfg["vlans"] = parsed_vlan
	cfg["l3interfaces"] = parsed_l3interfaces
	cfg["portchannels"] = parsed_pc
	cfg["l2interfaces"] = parsed_l2interfaces
	cfg["stp"] = parsed_stp

	full_config = {}

	for feature in cfg:
		node_cfg = cfg[feature]
		for node,config in node_cfg.items():
			config_dir = f"{base_dir}/{node}"
			pathlib.Path(config_dir).mkdir(parents=True, exist_ok=True)
			template_name = f"{feature}.j2"
			data = render_config_data(config, template_name)
			write_config_data(data, config_dir, f"{feature}-config")
			if full_config.get(node):
				full_config[node].update({feature:data})
			else:
				full_config[node] = {feature:data}

	for node,cfg in full_config.items():
		config_dir = f"{base_dir}/{node}"
		cfg["hostname"] = node
		data = render_config_data(cfg, "full.j2")
		write_config_data(data, config_dir, "full-config")


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/inventory", methods=['GET','POST'])
def inventory():

	if request.method == 'POST':
		file = request.files["file"]
		filename = secure_filename(file.filename)
		if filename != "inventory.xlsx":
			flash('filename should be inventory.xlsx')
		else:
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			generate_inventory(filename)

	hosts = get_inventory().inventory.dict()["hosts"].values()

	return render_template("inventory.html", hosts=hosts)

@app.route("/config/get/<filepath>")
def get_config_file(filepath):
	host,config_file = filepath.split(":")
	configpath = f"{BASE_DIR}/n9k-configs/{host}/{config_file}"
	message={}
	with open(configpath) as f:
		message["config"] =  f.read()
		message["title"] = f"{host} - {config_file}"
	return jsonify(message)

@app.route("/generate", methods=['GET','POST'])
def generate():
	if request.method == 'POST':
		file = request.files["file"]
		filename = secure_filename(file.filename)
		if filename != "day0.xlsx":
			flash('filename should be day0.xlsx')
		else:
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			generate_configuration(filename)

	mapping = {}
	try:
		dir_list = sorted(os.listdir("n9k-configs"))
	except FileNotFoundError:
		pass
	else:
		for subdir in dir_list:
			files = os.listdir(f"n9k-configs/{subdir}")
			mapping[subdir] = files

	return render_template("generate.html", config_files=mapping)


@app.route("/configure", methods=['GET','POST'])
def configure():
	hosts = get_inventory().inventory.dict()["hosts"].values()
	results = []
	if request.method == 'POST':
		devices = request.form.getlist("device")
		configs = request.form.getlist("config")
		target_hosts = get_inventory(target_hosts=devices)

		for config in CONFIG_OPTIONS:
			if config in configs:
				config_results = target_hosts.run(send_configs_from_file, filename=f"{config}-config")
				for host in config_results:
					result = config_results[host][1]
					status = "failed" if result.failed else "success"
					results.append((host, config, status, result.result))

	return render_template("configure.html", hosts=hosts, config_options=CONFIG_OPTIONS, results=results)

if __name__ == '__main__':
    app.run()