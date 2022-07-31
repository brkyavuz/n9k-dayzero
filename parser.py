import pandas as pd
from helpers import keypair, key_subkey_pair, range_parser


class Parser:
	def __init__ (self, excel_file):
		self.df = pd.read_excel(excel_file, sheet_name=None)


	def cfg_parser(self, sheet_name):
		data = self.df[sheet_name]
		cfg = {}
		for node in data['node'].unique():
			cfg_data = data[data['node'] == node]
			cfg_data = cfg_data.drop('node', axis=1).fillna("N/A").to_dict('records')
			cfg[node] = {sheet_name: cfg_data}

		return cfg

	def vpc_parser(self):

		data = self.df["vpc"].fillna('N/A')
		cfg = {}
		for domain in data['vpc-domain'].unique():
			cfg_data = data[data['vpc-domain'] == domain].fillna("N/A").to_dict("records")
			node1values, node2values = cfg_data
			node1values["dest-addr"] = node2values["address"]
			node2values["dest-addr"] = node1values["address"]
			cfg[node1values["node"]] = {"vpc":node1values}
			cfg[node2values["node"]] = {"vpc":node2values}

		return cfg


	def vlan_parser(self):
		vlans_data = self.df["vlans"].to_dict(orient="records")
		vlan_names = self.df["vlan-names"].set_index("id").to_dict(orient="index")

		cfg = {}
		temp_mapping = {}

		for v in vlans_data:
			node = v["node"]
			vlans = range_parser(v["vlans"])
			temp_mapping[node] = vlans

		for node,vlans in temp_mapping.items():
			for vlan in vlans:
				if vlan_names.get(vlan):
					vlan_name = vlan_names[vlan]["name"]
					value = f"{vlan}:{vlan_name}"
					key_subkey_pair(cfg, node, "vlans_with_name", value)

		for node in vlans_data:
			cfg[node["node"]]["vlans"] = node["vlans"]

		return cfg

	def stp_parser(self,):
		data = self.df["stp"].fillna('N/A')
		cfg = {}
		for node in data['node'].unique():
			temp_dict = {}
			cfg_data = data[data['node'] == node].fillna("N/A").to_dict("records")
			
			for node in cfg_data:
				if not temp_dict.get("mode"):
					temp_dict["mode"] = node["mode"]
				if not temp_dict.get("name(mst)"):
					temp_dict["name"] = node["name(mst)"]
				if not temp_dict.get("revision(mst)"):
					temp_dict["revision"] = node["revision(mst)"]

				if node["mode"] == "mst":
					keypair (temp_dict, "mst", f'{node["instance"]}:{node["vlans"]}:{node["priority"]}')
				else:
					keypair (temp_dict, "pvst", f'{node["vlans"]}:{node["priority"]}')
			
			if temp_dict.get("mst"):
				temp_dict["mst"] = temp_dict["mst"] if isinstance(temp_dict["mst"], list) else [temp_dict["mst"]]
			else:
				temp_dict["pvst"] = temp_dict["pvst"] if isinstance(temp_dict["pvst"], list) else [temp_dict["pvst"]]

			cfg[node["node"]] = {"stp": temp_dict}

		return cfg

	def feature_parser(self,):
		cfg = {}
		vpc_data = self.df["vpc"]
		l3interface_data = self.df["l3interfaces"]
		is_vpc_empty = vpc_data.empty
		is_l3interfaces_empty = l3interface_data.empty


		if not is_vpc_empty:
			for node in vpc_data['node'].unique():
				if cfg.get(node):
					cfg[node]["features"].extend(["vpc", "lacp"])
				else:
					cfg[node] = {"features": ["vpc","lacp"]}

		if not is_l3interfaces_empty:
			for node in l3interface_data['node'].unique():
				cfg_data = l3interface_data[l3interface_data['node'] == node].fillna("N/A").to_dict('records')
				fhrp_type = list(set([cfg["fhrp-type"] for cfg in cfg_data if cfg["node"]== node and cfg["fhrp-type"] != "N/A"]))
				l3features = ["interface-vlan"]
				if cfg.get(node):
					l3features.extend(fhrp_type)
					cfg[node]["features"].extend(l3features)
				else:
					l3features.extend(fhrp_type)
					cfg[node] = {"features": l3features}

		return cfg