import pandas as pd
import yaml
import sys

df = pd.read_excel("inventory.xlsx")


if df[["name", "hostname", "groups"]].isnull().values.any():
	print("mandatory columns (name, hostname and groups) are can not be empty ")
	sys.exit()

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