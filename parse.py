type Status = str
type Id = str
type Rule = str
type InfraState = dict[Rule, list[dict[str, Id|Status]]] 

# JSON PARSING
def parse(data: dict) -> InfraState:
    parsed: InfraState = {}
    rules = data["data"]["groups"][0]["rules"]
    keys = ["uptime", "proxmox", "aps", "temps"]
    for key in keys:
        parsed[key] = []
    for rule in rules:
        alerts = rule["alerts"]
        alertname = rule["name"]
        # TODO: sort lists by id
        build_item = lambda alert, id_builder: {
                "id": id_builder(alert),
                "state": "ok" if alert["state"] == "Normal" else "error",
            }
        for alert in alerts:
            build = lambda id_builder: build_item(alert, id_builder)
            ap_id = lambda ap_id: "0" + ap_id if int(ap_id) < 10 else ap_id 
            match alertname:
                case "ping_exporter_rule":
                    parsed["uptime"].append(build(lambda a: a["labels"]["alias"]))
                case "proxmox_exporter_cpu":
                    parsed["proxmox"].append(build(lambda a: a["labels"]["id"]))
                case "snmp_rule":
                    parsed["aps"].append(build(lambda a: "AP-" + ap_id(a["labels"]["mwApTableIndex"])))
                # temperaturi
                case _ if alertname.startswith("temperature_alert_"):
                    parsed["temps"].append(build(lambda a: alertname[len("temperature_alert_"):]))
    for key in keys:
        parsed[key].sort(key=lambda e: e["id"])
    return parsed