import os

# You can set AWS Keys here or in ENV
os.environ['AWS_ACCESS_KEY_ID'] = "AKIAJWN6UYSF2NVV2IJA"
os.environ['AWS_SECRET_ACCESS_KEY'] = "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"

# Location for cerebro logs
log_location = "/mnt/data/clustersitter"

# Keys used to login to machines
# TODO -- should define this again inside provider_config
keys = ["/opt/wifast/keys/WiFastAWSdev-us-west-2.pem"]

# The user to login as in machines created by providers
# TODO -- this should be inside provider_config
login_user = "ubuntu"

# Define configuration for machine providers
provider_config = {
    'aws': {
        'us-west-2a': {
            '32b_image_id': 'ami-d862efe8',
            '64b_image_id': 'ami-6c15985c',
            'key_name': 'wifast-dev-uswest-2',
            'security_groups': ['clustersitter'],
            },
        },
    }

# DNS Provider configuration
dns_provider_config = {
    'class': 'dynect:Dynect',
    'customername': 'wifast',
    'username': 'apiuser',
    'password': 'qwe123',
    'default_domain': 'wifastdev.com'
    }
