# -*- code utf-8 -*-

"""Classes for CloudFront"""
import boto3
from botocore.exceptions import ClientError
from pprint import pprint
from math import floor
from math import ceil
import uuid
from cert import CertManager
from bucket import BucketManager
from domain import DomainManager


class CloudFrontManager:
    """Manage CloudFront"""

    def __init__(self, session):
        """Creates a CertManager object"""
        self.session = session
        self.client = self.session.client('cloudfront')



    def get_distribution(self, website):
        """Find a CloudFront Distribution that Matches Domain Name"""

        cf_paginator = self.client.get_paginator('list_distributions')

        for page in cf_paginator.paginate():
            for dist in page['DistributionList']['Items']:
                for origin in dist['Origins']['Items']:
                    if origin['DomainName'] == website:
                        return dist

        return None

    def setup_distribution(self, website, bucket, certificate, dns):
        """Create a CloudFront Distribution for a Domain Name"""


        if not self.get_distribution(website):
            print("\t" + ("⛅️    " * 21)+"\n")
            print(
                '\t⛅️    We need to configure CloudFront for {0}'.format(website)+"\n")
            print("\t⛅️    Bucket         : " + bucket.name+"\n")
            print("\t⛅️    Certificate    : " + certificate+"\n")
            zone = dns['AliasTarget']['HostedZoneId']
            print("\t⛅️    Zone           : " + zone+"\n")
       
            origin_id = 'S3-' + website
            response = self.client.create_distribution(
                DistributionConfig={
                    'CallerReference': str(uuid.uuid4()),
                    'Aliases': {
                        'Quantity': 1,
                        'Items': [bucket.name]
                    },
                    'DefaultRootObject': 'index.html',
                    'Comment': 'Created by Webotron',
                    'Enabled': True,
                    'Origins': {
                        'Quantity': 1,
                        'Items': [
                            {
                                'Id': origin_id,
                                'DomainName': '{}.s3.amazonaws.com'.format(bucket.name),
                                'S3OriginConfig': {
                                    'OriginAccessIdentity': ''
                                }
                               
                            }
                        ]
                    },
                    'DefaultCacheBehavior': {
                        'TargetOriginId': origin_id,
                        'ForwardedValues': {
                            'QueryString': True | False,
                            'Cookies': {'Forward': 'all'},
                            'Headers': {'Quantity': 0},
                            'QueryStringCacheKeys': {'Quantity' : 0}
                        },
                        'TrustedSigners': {
                            'Enabled': False,
                            'Quantity': 0
                        },
                        'ViewerProtocolPolicy': 'redirect-to-https',
                        'SmoothStreaming': False,
                        'MinTTL': 3600,
                        'DefaultTTL': 86400,
                        'MaxTTL': 86400,
                        'Compress': False,
                    },
                    'ViewerCertificate': {
                        'CloudFrontDefaultCertificate': False,
                        'ACMCertificateArn': certificate,
                        'SSLSupportMethod': 'sni-only' ,
                        'MinimumProtocolVersion': 'TLSv1.1_2016' ,
                    }
                }
            )
           
            print("\t⛅️    CloudFront URL : " +
                  response['Distribution']['DomainName']+"\n")
            print("\t" + ("⛅️    " * 21)+"\n")
            return(response)
        else:
            print("\t" + ("⛅️    " * 21)+"\n")
            msg = "CloudFront Already Configured for {0}".format(website)
            padding = 99 - len(msg)
            print("\t⛅️" + (" " * floor(padding/2)) +
                  msg + (" " * ceil(padding/2)) + "⛅️\n")

            print("\t" + ("⛅️    " * 21)+"\n")
