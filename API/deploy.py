import subprocess
import json
import shutil
import os.path
from colorama import init, Fore

with open('../config/cloudformation_config.json') as config_file:
    config = json.load(config_file)

init()

print(Fore.CYAN + "Copying CloudFormation template file to deployment directory")

cfnTemplatePath = os.path.join('.', config['CloudFormationTemplateDir'],
                               config['CloudFormationTemplateFilename'])

cfnTemplateDeployPath = os.path.join('.', "deploy_" + config['CloudFormationTemplateFilename'])

outputTemplatePath = os.path.join('.', "deploy_" + config['OutputTemplateFilename'])

shutil.copy(cfnTemplatePath, cfnTemplateDeployPath)

try:
    subprocess.run(["deploymentScripts\package.bat",
                    cfnTemplateDeployPath,
                    outputTemplatePath,
                    config["DeploymentBucketName"]], shell=True, check=True)

    subprocess.run(["deploymentScripts\deploy.bat",
                    outputTemplatePath,
                    config["StackName"],
                    config["YetiTransactionsTableName"]], shell=True, check=True)
    # subprocess.run(["deploymentScripts\clean.bat",
    #                 config["DeploymentBucketName"]], shell=True, check=True)

    print(Fore.GREEN + "Serverless Deployment completed")

    print(Fore.CYAN + "Removing CloudFormation and SAM template file from deployment directory")

    if os.path.exists(cfnTemplateDeployPath):
        os.remove(cfnTemplateDeployPath)
    if os.path.exists(outputTemplatePath):
        os.remove(outputTemplatePath)
except subprocess.CalledProcessError as e:
    out_bytes = e.output  # Output generated before error
    code = e.returncode  # Return code
    print(out_bytes)
    print(code)
    print(Fore.RED + "Deployment Failed")
    exit(0)

print(Fore.GREEN + "Deployment Succeeded")
