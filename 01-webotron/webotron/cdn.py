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
            print("\t⛅️    " + bucket.name+"\n")
            print("\t⛅️    " + certificate+"\n")
            zone = dns['AliasTarget']['HostedZoneId']
            print("\t⛅️    " + zone+"\n")
            print("\t" + ("⛅️    " * 21)+"\n")
        else:
            print("\t" + ("⛅️    " * 21)+"\n")
            msg = "CloudFront Already Configured for {0}".format(website)
            padding = 99 - len(msg)
            print("\t⛅️" + (" " * floor(padding/2)) +
                  msg + (" " * ceil(padding/2)) + "⛅️\n")
            
            print("\t" + ("⛅️    " * 21)+"\n")
            


                    
#   
#       check if there is a dist already
#       get certificate
#       get the dns record
#       
# 
#
#
"""
        response = self.client.create_distribution(
            DistributionConfig={
                'CallerReference': str(uuid.uuid4()),
                # 'Aliases': {
                #     'Quantity': 123,
                #     'Items': [
                #         'string',
                #     ]
                # },
                # 'DefaultRootObject': 'string',
                'Origins': {
                    'Quantity': 1,
                    'Items': [
                        {
                            'Id': 'custom-'+website,
                            'DomainName': website,
                            # 'OriginPath': '',
                            # 'CustomHeaders': {
                            #     'Quantity': 123,
                            #     'Items': [
                            #         {
                            #             'HeaderName': 'string',
                            #             'HeaderValue': 'string'
                            #         },
                            #     ]
                            # },
                            # 'S3OriginConfig': {
                            #     'OriginAccessIdentity': 'string'
                            # },
                            'CustomOriginConfig': {
                                'HTTPPort': 80,
                                'HTTPSPort': 443,
                                'OriginProtocolPolicy': 'http-only'
                                'OriginSslProtocols': {
                                    'Quantity': 1,
                                    'Items': ['TLSv1']
                                },
                                'OriginReadTimeout': 30,
                                'OriginKeepaliveTimeout': 5
                            }
                        },
                    ]
                },
                # 'OriginGroups': {
                #     'Quantity': 123,
                #     'Items': [
                #         {
                #             'Id': 'string',
                #             'FailoverCriteria': {
                #                 'StatusCodes': {
                #                     'Quantity': 123,
                #                     'Items': [
                #                         123,
                #                     ]
                #                 }
                #             },
                #             'Members': {
                #                 'Quantity': 123,
                #                 'Items': [
                #                     {
                #                         'OriginId': 'string'
                #                     },
                #                 ]
                #             }
                #         },
                #     ]
                # },
                'DefaultCacheBehavior': {
                    'TargetOriginId': 'custom-'+website,
                    'ForwardedValues': {
                        'QueryString': True | False,
                        'Cookies': {
                            'Forward': 'none' | 'whitelist' | 'all',
                            'WhitelistedNames': {
                                'Quantity': 123,
                                'Items': [
                                    'string',
                                ]
                            }
                        },
                        'Headers': {
                            'Quantity': 123,
                            'Items': [
                                'string',
                            ]
                        },
                        'QueryStringCacheKeys': {
                            'Quantity': 123,
                            'Items': [
                                'string',
                            ]
                        }
                    },
                    'TrustedSigners': {
                        'Enabled': True | False,
                        'Quantity': 123,
                        'Items': [
                            'string',
                        ]
                    },
                    'ViewerProtocolPolicy': 'redirect-to-https',
                    'MinTTL': 123,
                    'AllowedMethods': {
                        'Quantity': 123,
                        'Items': [
                            'GET' | 'HEAD' | 'POST' | 'PUT' | 'PATCH' | 'OPTIONS' | 'DELETE',
                        ],
                        'CachedMethods': {
                            'Quantity': 123,
                            'Items': [
                                'GET' | 'HEAD' | 'POST' | 'PUT' | 'PATCH' | 'OPTIONS' | 'DELETE',
                            ]
                        }
                    },
                    'SmoothStreaming': False,
                    'DefaultTTL': 123,
                    'MaxTTL': 123,
                    'Compress': False,
                    # 'LambdaFunctionAssociations': {
                    #     'Quantity': 123,
                    #     'Items': [
                    #         {
                    #             'LambdaFunctionARN': 'string',
                    #             'EventType': 'viewer-request' | 'viewer-response' | 'origin-request' | 'origin-response',
                    #             'IncludeBody': True | False
                    #         },
                    #     ]
                    # },
                    'FieldLevelEncryptionId': 'string'
                },
                'CacheBehaviors': {
                    'Quantity': 123,
                    'Items': [
                        {
                            'PathPattern': '*',
                            'TargetOriginId': 'string',
                            'ForwardedValues': {
                                'QueryString': True | False,
                                'Cookies': {
                                    'Forward': 'none' | 'whitelist' | 'all',
                                    'WhitelistedNames': {
                                        'Quantity': 123,
                                        'Items': [
                                            'string',
                                        ]
                                    }
                                },
                                'Headers': {
                                    'Quantity': 123,
                                    'Items': [
                                        'string',
                                    ]
                                },
                                'QueryStringCacheKeys': {
                                    'Quantity': 123,
                                    'Items': [
                                        'string',
                                    ]
                                }
                            },
                            'TrustedSigners': {
                                'Enabled': True | False,
                                'Quantity': 123,
                                'Items': [
                                    'string',
                                ]
                            },
                            'ViewerProtocolPolicy': 'redirect-to-https',
                            'MinTTL': 123,
                            'AllowedMethods': {
                                'Quantity': 123,
                                'Items': [
                                    'GET' | 'HEAD' ,
                                ],
                                'CachedMethods': {
                                    'Quantity': 123,
                                    'Items': [
                                        'GET' | 'HEAD' | 'POST' | 'PUT' | 'PATCH' | 'OPTIONS' | 'DELETE',
                                    ]
                                }
                            },
                            'SmoothStreaming': True | False,
                            'DefaultTTL': 123,
                            'MaxTTL': 123,
                            'Compress': True | False,
                            'LambdaFunctionAssociations': {
                                'Quantity': 123,
                                'Items': [
                                    {
                                        'LambdaFunctionARN': 'string',
                                        'EventType': 'viewer-request' | 'viewer-response' | 'origin-request' | 'origin-response',
                                        'IncludeBody': True | False
                                    },
                                ]
                            },
                            'FieldLevelEncryptionId': 'string'
                        },
                    ]
                },
                'CustomErrorResponses': {
                    'Quantity': 123,
                    'Items': [
                        {
                            'ErrorCode': 123,
                            'ResponsePagePath': 'string',
                            'ResponseCode': 'string',
                            'ErrorCachingMinTTL': 123
                        },
                    ]
                },
                'Comment': 'string',
                'Logging': {
                    'Enabled': True | False,
                    'IncludeCookies': True | False,
                    'Bucket': 'string',
                    'Prefix': 'string'
                },
                'PriceClass': 'PriceClass_100' | 'PriceClass_200' | 'PriceClass_All',
                'Enabled': True | False,
                'ViewerCertificate': {
                    'CloudFrontDefaultCertificate': True | False,
                    'IAMCertificateId': 'string',
                    'ACMCertificateArn': 'string',
                    'SSLSupportMethod': 'sni-only' | 'vip',
                    'MinimumProtocolVersion': 'SSLv3' | 'TLSv1' | 'TLSv1_2016' | 'TLSv1.1_2016' | 'TLSv1.2_2018',
                    'Certificate': 'string',
                    'CertificateSource': 'cloudfront' | 'iam' | 'acm'
                },
                'Restrictions': {
                    'GeoRestriction': {
                        'RestrictionType': 'blacklist' | 'whitelist' | 'none',
                        'Quantity': 123,
                        'Items': [
                            'string',
                        ]
                    }
                },
                'WebACLId': 'string',
                'HttpVersion': 'http1.1' | 'http2',
                'IsIPV6Enabled': True | False
            }
        )
        
  """      
        
