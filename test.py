from nornir import InitNornir
from nornir.core.filter import F


def get_inventory(target_hosts):
    nr = InitNornir("config.yaml")
    if target_hosts:
        return nr.filter(F(name__any=target_hosts)).inventory.dict()["hosts"].values()
    else:
        return nr.inventory.dict()["hosts"].values()


hosts = get_inventory(target_hosts=["N9K1", "N9K10"])

print(hosts)