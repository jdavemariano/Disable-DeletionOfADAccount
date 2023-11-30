import boto3
import time
import os
import sys
import json

domain = sys.argv[1]

with open("domain_accounts.json") as json_file:
    config = json.load(json_file)
    instance_info = config.get(domain,{})

print(f"Instance Info: {instance_info}")

if not instance_info:
    print(f"Domain '{domain}' not found in configuration.")
    sys.exit(1)

target_instance = instance_info.get("target_instance", "")
sourceou = instance_info.get("sourceou", "")
destinationou = instance_info.get("destinationou", "")

print(f"Target Instance: {target_instance}")
print(f"Source OU: {sourceou}")
print(f"Destination OU: {destinationou}")

if not target_instance or not sourceou or not destinationou:
    print(f"Missing required parameters for domain '{domain}'.")
    sys.exit(1)

ssm_file = open("disable_account.json")
ssm_json = ssm_file.read()

ssm_doc_name = 'disable_account'
ssm_client = boto3.client('ssm', region_name="us-east-1")

ssm_create_response = ssm_client.create_document(Content = ssm_json, Name = ssm_doc_name, DocumentType = 'Command', DocumentFormat = 'JSON', TargetType =  "/AWS::EC2::Instance")

ssm_run_response = ssm_client.send_command(InstanceIds = [target_instance], DocumentName=ssm_doc_name, DocumentVersion="$DEFAULT", TimeoutSeconds=120,  Parameters={'destinationOU':[destinationou],'sourceOU':[sourceou],})
print(f'{ssm_run_response}\n')
cmd_id = ssm_run_response['Command']['CommandId']

time.sleep(5)
ssm_status_response = ssm_client.get_command_invocation(CommandId=cmd_id, InstanceId=target_instance)
while ssm_status_response['StatusDetails'] == 'InProgress':
	time.sleep(5)
	ssm_status_response = ssm_client.get_command_invocation(CommandId=cmd_id, InstanceId=target_instance)

if ssm_status_response['StatusDetails'] == 'Success':
	print('Powershell script for Disabling Expired Accounts has been executed in {domain}\n')

cmd_output = ssm_status_response.get('StandardOutputContent','')
print(f'{cmd_output}\n')

with open('Disabled_AD_Account.txt', 'w') as outfile:
	outfile.write(cmd_output)

ssm_delete_response = ssm_client.delete_document(Name=ssm_doc_name)
