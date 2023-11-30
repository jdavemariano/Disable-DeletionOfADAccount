import boto3
import time
import os
import sys
import json

domain = sys.argv[1]

ssm_file = open("delete_account.json")
ssm_json = ssm_file.read()

with open("domain_accounts.json") as json_file:
    config = json.load(json_file)
    instance_info = config.get(domain,{})

print(f"Instance Info: {instance_info}")

if not instance_info:
    print(f"Domain '{domain}' not found in configuration.")
    sys.exit(1)

target_instance = instance_info.get("target_instance", "")
sourceou = instance_info.get("sourceou", "")

print(f"Target Instance: {target_instance}")
print(f"Source OU: {sourceou}")

if not target_instance or not sourceou or not destinationou:
    print(f"Missing required parameters for domain '{domain}'.")
    sys.exit(1)

ssm_doc_name = 'delete_account'
ssm_client = boto3.client('ssm', region_name="us-east-1")

ssm_create_response = ssm_client.create_document(Content = ssm_json, Name = ssm_doc_name, DocumentType = 'Command', DocumentFormat = 'JSON', TargetType =  "/AWS::EC2::Instance")

ssm_run_response = ssm_client.send_command(InstanceIds = [target_domain], DocumentName=ssm_doc_name, DocumentVersion="$DEFAULT", TimeoutSeconds=120,  Parameters={'sourceOU':[sourceou],})
print(f'{ssm_run_response}\n')
cmd_id = ssm_run_response['Command']['CommandId']

time.sleep(5)
ssm_status_response = ssm_client.get_command_invocation(CommandId=cmd_id, InstanceId=target_domain)
while ssm_status_response['StatusDetails'] == 'InProgress':
	time.sleep(5)
	ssm_status_response = ssm_client.get_command_invocation(CommandId=cmd_id, InstanceId=target_domain)

if ssm_status_response['StatusDetails'] == 'Success':
	print('Scipt Executed on Deleting Expired Accounts for more than 18 months in {target_domain}\n')

cmd_output = ssm_status_response.get('StandardOutputContent','')
print(f'{cmd_output}\n')

with open('Deleted_AD_Account.txt', 'w') as outfile:
	outfile.write(cmd_output)

ssm_delete_response = ssm_client.delete_document(Name=ssm_doc_name)
