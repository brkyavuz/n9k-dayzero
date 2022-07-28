from nornir import InitNornir
from nornir_scrapli.tasks import send_configs
from nornir_utils.plugins.functions import print_result
from generate_hosts_from_excel import generate_inventory
import generate_n9k_configs
from colorama import init, Fore
import os

clear = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')
init()

OPTIONS = {
	"start": [
		"Select the operation code to proceed:\n ",
		"[1] Generate Nornir Inventory from Excel file. ",
		"[2] Generate Nexus 9K configurations from Excel file. ",
		"[3] Configuration Automation.",
		f"{Fore.RED}[0] Exit the menu\n"
	],
	"automation": [
		f"{Fore.YELLOW}Note: This operation requires to generate nexus configurations first (main menu option 2).\n",
		"Select the operation code to proceed with configuration:\n ",
		"[1] Configure Features ",
		"[2] Configure Vpc ",
		"[3] Configure Stp ",
		"[4] Configure Vlans ",
		"[5] Configure Portchannels ",
		"[6] Configure Interfaces ",
		"[7] Configure SVI interfaces ",
		f"{Fore.RED}[0] Back the previous menu"
	],
	"selection": f"{Fore.BLUE}Selection: ",
	"invalid": [f"{Fore.RED}Invalid input", f"{Fore.RED}File not found"]
	}



def file_menu(user_input):
	clear()
	while True:
		filename = input(f"{Fore.BLUE}Provide the Excel filename or 'back' for previous menu : ")
		if filename == "back":
			clear()
			break
		else:
			if os.path.exists(filename):
				if user_input == "1":
					generate_inventory(filename)
				else:
					generate_n9k_configs(filename)
			else:
				print(OPTIONS["invalid"][1])


def outer_menu():
	while True:
		for msg in OPTIONS["start"]:
			print(msg)
		main_menu_input = input(OPTIONS["selection"])
		if main_menu_input not in ["0","1","2","3"]:
			clear()
			print(OPTIONS["invalid"][0])
		else:
			if main_menu_input == "0":
				break

			elif main_menu_input == "1":
				file_menu(main_menu_input)

			elif main_menu_input == "2":
				file_menu(main_menu_input)

# def user_menu():

# 	while True:
# 		for msg in OPTIONS["start"]:
# 			print(msg)

# 		main_menu_input = input(OPTIONS["selection"])

# 		if main_menu_input == "0":
# 			break

# 		elif main_menu_input == "1":
# 			clear()
# 			filename = input("Provide the inventory Excel filename or 'back' for previous menu : ")
# 			if filename == "back":
# 				clear()
# 				continue
# 			else:
# 				if os.path.exists(filename):
# 					generate_hosts_from_excel(filename)
# 				else:
# 					print(OPTIONS["invalid"][1])

# 		elif main_menu_input == "2":
# 			clear()
# 			filename = input("Type 'back' for previous menu\nProvide the Configuration Excel filename : ")
# 			if filename == "back":
# 				clear()
# 				continue
# 			else:
# 				generate_n9k_configs(filename)

# 		elif main_menu_input == "3":
# 			clear()
# 			for msg in OPTIONS["automation"]:
# 				print(msg)

# 			config_input = input(OPTIONS["selection"])


def send_configs(task, filename):
	config_dir = f"n9k-configs/{task.host.name}/{filename}"

	with open(config_dir) as f:
		data = f.read()
		commands = data.split('\n')
		commands = [command.lstrip() for command in commands if command != "!" ]


	task.run(task=send_configs, configs=commands)


def main():
	nr = InitNornir(config_file="config.yaml")
	outer_menu()

	# vpc_results = nr.run(task=send_configs, filename="vpc-config.txt")
	# print_result(vpc_results)

if __name__ == "__main__":
	main()