# -*- code utf-8 -*-

import uuid 

"""Classes for Route 53 Domains"""

class DomainManager:
    """Manage a Route 53 Domain"""

    def __init__(self,session):
        """Create a DomainManager Object"""
    
        self.session = session
        self.client = self.session.client('route53')

    def get_hosted_zone(self,domain_name):
        """Find a Hosted Zone that Matches Domain Name"""
        
        r53_paginator = self.client.get_paginator('list_hosted_zones')
        for page in r53_paginator.paginate():
            for zone in page['HostedZones']:
                if domain_name.endswith(zone['Name'][:-1]):
                    return zone
        
        return None   

    def create_hosted_zone(self,domain_name):
        """Create a Hosted Zone"""
        zone_name = '.'.join(domain_name.split('.')[-2:]) + '.'
        return self.client.create_hosted_zone(
            Name = zone_name,
            CallerReference = str(uuid.uuid4())
        )

    def create_s3_domain_record(self,bucket,zone):
        """Create S3 Domain Record"""

        return self.client.change_resource_record_setsclient.change_resource_record_sets(
            HostedZoneId=zone['Id'],
            ChangeBatch={
                'Comment': 'Added by Webotron',
                'Changes': [
                    {
                        'Action': 'CREATE',
                        'ResourceRecordSet': {
                            'Name': 'string',
                            'Type': 'A',
                            'AliasTarget': {
                                'HostedZoneId': 'string',
                                'DNSName': 'string',
                          
                            },
                           
                        }
                    },
                ]
            }
        )
