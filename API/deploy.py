import subprocess
import json
import shutil
import os.path
from colorama import init, Fore
from cloudformation_config import config
from secret_config import outlook_credentials

init()

print(Fore.CYAN + "Copying CloudFormation template file to deployment directory")

swaggerSrcPath = os.path.join('.', config['SwaggerDir'],
                              config['SwaggerFilename'])

swaggerDeployPath = os.path.join('./src', config['SwaggerFilename'])

shutil.copy(swaggerSrcPath, swaggerDeployPath)

cfnTemplatePath = os.path.join('.', config['CloudFormationTemplateDir'],
                               config['CloudFormationTemplateFilename'])

cfnTemplateDeployPath = os.path.join('./src', "deploy_" + config['CloudFormationTemplateFilename'])

outputTemplatePath = os.path.join('./src', "deploy_" + config['OutputTemplateFilename'])

shutil.copy(cfnTemplatePath, cfnTemplateDeployPath)

try:
    subprocess.run(["deploymentScripts\package.bat",
                    cfnTemplateDeployPath,
                    outputTemplatePath,
                    config["DeploymentBucketName"]], shell=True, check=True)

    subprocess.run(["deploymentScripts\deploy.bat",
                    outputTemplatePath,
                    config["StackName"],
                    config["YetiTransactionsTableName"],
                    config["YetiLoginsTableName"],
                    config["YetiTokensTableName"],
                    outlook_credentials["OutlookOAuthClientId"],
                    outlook_credentials["OutlookOAuthClientSecret"]
                    ],
                   shell=True, check=True)
    # subprocess.run(["deploymentScripts\clean.bat",
    #                 config["DeploymentBucketName"]], shell=True, check=True)

    print(Fore.GREEN + "Serverless Deployment completed")

    print(Fore.CYAN + "Removing CloudFormation and SAM template file from deployment directory")

    if os.path.exists(cfnTemplateDeployPath):
        os.remove(cfnTemplateDeployPath)
    if os.path.exists(outputTemplatePath):
        os.remove(outputTemplatePath)
    if os.path.exists(swaggerDeployPath):
        os.remove(swaggerDeployPath)
except subprocess.CalledProcessError as e:
    out_bytes = e.output  # Output generated before error
    code = e.returncode  # Return code
    print(out_bytes)
    print(code)
    print(Fore.RED + "Deployment Failed")
    exit(0)

print(Fore.GREEN + "Deployment Succeeded")
