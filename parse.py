from collections.abc import Callable
from typing import TypedDict, Any
from datetime import datetime

type Status = str
type Id = str
type Timestamp = float # in ISO-8601 format
class Alert(TypedDict):
    id: Id
    status: Status
    ts: Timestamp | None
class Category(TypedDict):
    alerts: list[Alert]
    timestamp: Timestamp | None
type InfraState = dict[Id, Category]

# Specify how to map rule names from the json to the internal view
def rule_mapping(rn: str) -> Id | None:
    match rn:
        case "ping_exporter_rule":
            return "uptime"
        case "proxmox_exporter_cpu":
            return "proxmox"
        case "snmp_rule":
            return "aps"
        case _ if rn.startswith("temperature_alert_"):
            return "temps"

def unix_from_iso(date: str) -> float:
    return datetime.fromisoformat(date).timestamp()

def parse(data: dict) -> InfraState:
    keys = ['uptime', 'proxmox', 'aps', 'temps']
    parsed: InfraState = { k:{'alerts': [], 'timestamp': None} for k in keys }
    for rule in data['data']['groups'][0]['rules']:
        rulename = rule['name']
        rule_id = rule_mapping(rulename)
        if rule_id == None:
            continue

        # Temps needs special attention, because the json has all
        # the temp alarms in the form of 'rules'. This, of course,
        # we correct
        if rule_id != 'temps':
            parsed[rule_id]['timestamp'] = unix_from_iso(rule['lastEvaluation'])
        # Make the alert builders
        def build_alert_id(a: Any) -> Id:
            match rule_id:
                case 'uptime':
                    return a['labels']['alias']
                case 'proxmox':
                    return a['labels']['id']
                case 'aps':
                    pad_ap_id = lambda ap_id: "0" + ap_id if int(ap_id) < 10 else ap_id
                    return "AP-" + pad_ap_id(a['labels']['mwApTableIndex'])
                case 'temps':
                    return rulename[len("temperature_alert_"):]
                case _:
                    return ""
        def build_alert(a: Any) -> Alert:
            return {
                'id': build_alert_id(a),
                'status': "ok" if alert['state'] == "Normal" else "error",
                'ts': unix_from_iso(rule['lastEvaluation']) if rule_id == 'temps' else None,
            }
        for alert in rule['alerts']:
            parsed[rule_id]['alerts'].append(build_alert(alert))
    for key in keys:
        parsed[key]['alerts'].sort(key=lambda e: e['id'])
    return parsed
