from google.cloud import compute_v1
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service-account.json"

def create_vm(project, zone, instance_name):
    compute = compute_v1.InstancesClient()
    instance = {
        "name": instance_name,
        "machineType": f"zones/{zone}/machineTypes/n1-standard-1",
        "disks": [
            {
                "boot": True,
                "initializeParams": {
                    "sourceImage": "projects/debian-cloud/global/images/debian-10-buster-v20210916"
                }
            }
        ],
        "networkInterfaces": [
            {
                "network": "global/networks/default",
                "accessConfigs": [
                    {
                        "type": "ONE_TO_ONE_NAT",
                        "name": "External NAT"
                    }
                ]
            }
        ]
    }

    request = compute.insert(project=project, zone=zone, body=instance)
    response = request.execute()
    print(response)