import os
import random
from google.cloud import compute_v1

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service-account.json"

def create_vm(project, instance_name):
    regions = ["us-central1", "europe-west1"]
    zones = {
        "us-central1": ["us-central1-a", "us-central1-b", "us-central1-c"],
        "europe-west1": ["europe-west1-b", "europe-west1-c", "europe-west1-d"]
    }
    region = random.choice(regions)
    zone = random.choice(zones[region])

    compute = compute_v1.InstancesClient()
    instance = {
        "name": instance_name,
        "machineType": f"zones/{zone}/machineTypes/n1-standard-1",
        "disks": [
            {
                "boot": True,
                "initializeParams": {
                    "sourceImage": "projects/ubuntu-os-cloud/global/images/ubuntu-2004-focal-v20240426",
                    "diskSizeGb": "10",
                    "diskType": f"projects/{project}/zones/{zone}/diskTypes/pd-ssd",
                    "labels": {}
                }
            }
        ],
        "networkInterfaces": [
            {
                "network": "global/networks/default",
                "accessConfigs": [
                    {
                        "name": "External NAT",
                        "networkTier": "PREMIUM"
                    }
                ]
            }
        ],
        "scheduling": {
            "automaticRestart": False,
            "instanceTerminationAction": "STOP",
            "onHostMaintenance": "TERMINATE",
            "provisioningModel": "SPOT"
        },
        "tags": {
            "items": [
                "http-server",
                "https-server",
                "lb-health-check"
            ]
        },
    }

    request = compute.insert(project=project, zone=zone, body=instance)
    response = request.execute()
    print(response)
