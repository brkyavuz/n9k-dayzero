<!-- ABOUT THE PROJECT -->
## About The Project

This tool created to help automate Cisco Nexus series switch configurations for the Greenfield deployments. Since main scope is greenfield this tool doesn't have any precheck mechanism yet but can be added later on.

<!-- PREVIEW -->
## Preview
![](https://github.com/brkyavuz/n9k-dayzero/blob/main/preview.gif)


<!-- INSTRUCTIONS -->
## Instructions
1. Create virtualenv with python and install requirements.
 ```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
 ```
2. Update the inventory.xlsx file based on your devices.
3. Update the day0.xlsx file based on your fabric setup
4. Start Flask UI and connect the Web UI from http://127.0.0.1:5000
```bash
flask run
```
5. Go to Inventory menu, select updated inventory excel file and update device list
6. Go to Configuration > Generate Configuration menu, select updated day0 excel file and generate device configurations
7. Go to Configuration > Push Configuration menu, select devices and config type that will be pushed to the devices and click Submit button
