import os
from google.cloud import compute_v1

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service-account.json"

def delete_vm(project, zone, instance_name):
    compute = compute_v1.InstancesClient()
    request = compute.delete(project=project, zone=zone, instance=instance_name)
    response = request.execute()
    print(response)


