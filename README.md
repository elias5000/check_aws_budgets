# check_aws_budgets

Icinga/Nagios check to check budgets in an AWS account


## Required Modules
* boto3


## Installation
    # Checkout source
    git clone https://github.com/elias5000/check_aws_budgets.git
    
    # Install boto3 Python module
    pip install boto3

    # Copy check script
    cp check_aws_budgets.py /usr/lib/nagios/plugins/check_aws_budgets.py
    
    # Copy director config
    cp check_aws_budgets.conf /etc/icinga2/conf.d/check_aws_budgets.conf
    

## Authentication
Authentication is identical to awscli. Use either instance role EC2 or pod role on K8S
with kube2iam (preferred) or ~/.aws/config profile. The check will use the default profile.


## Usage
The check does not take any arguments in the current version.
It fetches all budgets of the caller account and checks if their forecast exceeds their configured limit.