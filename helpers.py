from jinja2 import Environment, FileSystemLoader

CONFIG_OPTIONS = ["features", "vpc", "vlans", "stp", "portchannels", "l2interfaces", "l3interfaces"]

def render_config_data(data,template_name):
	env = Environment(
        loader=FileSystemLoader("./jinja-templates"), trim_blocks=True, lstrip_blocks=True
    )
	template = env.get_template(template_name)
	rendered = template.render(data)

	return rendered


def write_config_data(data, filepath, filename):

	with open(f"{filepath}/{filename}", "w+") as f:
		f.write(data)


def keypair(dictionary, key, value):
	if dictionary.get(key):
		if isinstance(dictionary[key], list):
			if not value in dictionary[key]:
				dictionary[key].append(value)
		else:
			if dictionary[key] != value:
				dictionary[key] = [dictionary[key], value]
	else:
		dictionary[key] = value

def key_subkey_pair(dictionary,key,subkey,value):
	if dictionary.get(key):
		if dictionary[key].get(subkey):
			if isinstance(dictionary[key][subkey],list):
				if value not in dictionary[key][subkey]:
					dictionary[key][subkey].append(value)
			else:
				if dictionary[key][subkey] != value:
					dictionary[key][subkey] = [dictionary[key][subkey],value]
		else:
			dictionary[key].update({subkey:value})
	else:
		dictionary[key] = {subkey:value}


def range_parser(data):
	result = []

	for elem in data.split(","):
		if "-" in elem:
			a,b = elem.split("-")
			a,b = int(a), int(b)
			result.extend(range(a,b+1))
		else:
			result.append(int(elem))

	return sorted(result)