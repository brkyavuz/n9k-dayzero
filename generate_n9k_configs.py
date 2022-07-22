from parser import Parser
from helpers import render_config_data, write_config_data
import sys
import pathlib


def main():
	excel_file = sys.argv[1]
	p = Parser(excel_file=excel_file)
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


if __name__ == "__main__":
	main()
