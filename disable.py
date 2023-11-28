import boto3
import time
import os
import sys 

domain = sys.argv[1]
sourceou = sys.argv[2]
destinationou = sys.argv[3]

ssm_file = open("disable_account.json")
ssm_json = ssm_file.read()

instance_ids = {
	"deltekdev":"i-04d0e953afe07b3a3",
	"costpoint":"i-0e82a12d1ef934425",
        "DCO":"i-0fe3ff3ff41c18b17",
	"Flexplus":"i-0f2717bceb18eea6f",
	"GlobalOSS":"i-04b225ae477c52288",
	"Engdeltek":"i-0667aa10a44eafc7c",
}

target_domain = instance_ids[domain]

ssm_doc_name = 'disable_account'
ssm_client = boto3.client('ssm', region_name="us-east-1")

ssm_create_response = ssm_client.create_document(Content = ssm_json, Name = ssm_doc_name, DocumentType = 'Command', DocumentFormat = 'JSON', TargetType =  "/AWS::EC2::Instance")

ssm_run_response = ssm_client.send_command(InstanceIds = [target_domain], DocumentName=ssm_doc_name, DocumentVersion="$DEFAULT", TimeoutSeconds=120,  Parameters={'destinationOU':[destinationou],'sourceOU':[sourceou],})
print(f'{ssm_run_response}\n')
cmd_id = ssm_run_response['Command']['CommandId']

time.sleep(5)
ssm_status_response = ssm_client.get_command_invocation(CommandId=cmd_id, InstanceId=target_domain)
while ssm_status_response['StatusDetails'] == 'InProgress':
	time.sleep(5)
	ssm_status_response = ssm_client.get_command_invocation(CommandId=cmd_id, InstanceId=target_domain)

if ssm_status_response['StatusDetails'] == 'Success':
	print('Powershell script for Disabling Expired Accounts has been executed in {target_domain}\n')

cmd_output = ssm_status_response.get('StandardOutputContent','')
print(f'{cmd_output}\n')

with open('Disabled_AD_Account.txt', 'w') as outfile:
	outfile.write(cmd_output)

ssm_delete_response = ssm_client.delete_document(Name=ssm_doc_name)
