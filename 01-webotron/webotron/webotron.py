#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Deploy Websites with AWS 

    Webotron automates the process of deploying static websites to AWS S3
    - Configure S3
        - Create them
        - Set them up for static website hosting
        - Deploy local files to them
"""

import boto3
import botocore
import click
from botocore.exceptions import ClientError

from bucket import BucketManager
from domain import DomainManager
import util

session = None
bucket_manager = None
domain_manager = None
client = None

#######################################################################################################
#######################################################################################################
#######################################################################################################
@click.group()
@click.option('--profile', default=None, help="Use a given AWS profile")
def cli(profile):
    """Webotron Synchronizes Local Directories with S3"""
    global session, bucket_manager, client, domain_manager
    session_cfg = {}

    if profile:
        session_cfg['profile_name'] = profile

    session = boto3.Session(**session_cfg)
    bucket_manager = BucketManager(session)
    domain_manager = DomainManager(session)

    client = boto3.client('s3')
#######################################################################################################
#######################################################################################################
#######################################################################################################
@cli.group("domains")
def domains():
    """Commands for Domains"""
#######################################################################################################
@domains.command("setup-domain")
@click.argument("domain")
@click.argument("bucket")
def setup_domain(domain, bucket):
    """Configure Domain to Bucket Mapping"""
    zone = domain_manager.get_hosted_zone(domain) \
        or domain_manager.create_hosted_zone(domain)
    print(zone['Id'])

    bucket_url = bucket_manager.get_bucket_url(bucket_manager.init_bucket(bucket))

    print(bucket_url)


    return
#######################################################################################################
#######################################################################################################
#######################################################################################################
@cli.group("buckets")
def buckets():
    """Commands for Buckets"""
#######################################################################################################
@buckets.command("sync")
@click.argument("pathname", type=click.Path(exists=True))
@click.option("--delete", default=False, is_flag=True, help="Will remove files from bucket that do not exist locally")
@click.argument("bucketname")
def sync_path(pathname, bucketname, delete):
    """Synchronize Local Path to S3 Bucket"""
    bucket_manager.sync_path(pathname, bucketname, delete)
    print("\n\tYou can find your webpage at \n \t \t{0}".format(
        bucket_manager.get_bucket_url(bucket_manager.s3.Bucket(bucketname))))
    return
#######################################################################################################
@buckets.command("list")
@click.option("--pattern", default=None, help="Will filter buckets starting with pattern")
def list_buckets(pattern):
    """List all s3 buckets \n
    Will filter buckets with pattern is provided"""
  
    buckets = []

    if pattern:
        for b in bucket_manager.find_bucket(pattern, True):
            buckets.append(b)
    else:
        buckets = bucket_manager.all_buckets()
    for b in buckets:
        print(b.name)
    return
#######################################################################################################
@buckets.command("create")
@click.argument("name")
@click.option("--region", "region", default='us-east-1', help='Bucket Region')
@click.option("--public", "public", default=False, is_flag=True, help='Make Bucket Public')
@click.option("--website", "website", default=False, is_flag=True, help='Host Static Website from Bucket')
def create_bucket(name, public, region, website):
    """Create new s3 bucket"""

    s3_bucket = bucket_manager.init_bucket(name, region)

    if website:
        public = False
        bucket_manager.give_public_access(s3_bucket)
        bucket_manager.host_website(s3_bucket, region)

    if public:
        bucket_manager.give_public_access(s3_bucket)

    return
#######################################################################################################
@buckets.command("delete")
@click.argument("name")
@click.option("--pattern_match", "pattern_match", default=False, is_flag=True, help = "Will filter buckets starting with pattern")
def delete_bucket(name, pattern_match):
    """Will empty and delete s3 bucket"""
    
    if name in util.protected_buckets:
        print("\tCannot delete protected bucket {0}".format(name))
    
    else:
        if pattern_match:
            msg = "You are attempting to delete all buckets with name starting wtih {0}\n \tAre you sure (YES)\t: ".format(name)
        else:
            msg = "You are attempting to delete bucket named {0}\n \tAre you sure (YES)\t: ".format(
                name)
        
        confirm = input(msg)

        if confirm == 'YES':
            if not name == "dmillikan-synology" and confirm == 'YES':
                print("\tI am deleting it all now")
                bucket_manager.delete_bucket(name,pattern_match=pattern_match)
        else:
            print("\tInvalid confirmation\n\t\tYou entered\t: {0}\n\tWill not delete bucket {1}".format(confirm,name))
    return
#######################################################################################################
@buckets.group("objects")
def objects():
    """Commands for Bucket Objects"""
#######################################################################################################
@objects.command("list")
@click.argument('bucket')
def list_bucket_objects(bucket):
    """List objects within s3 bucket"""
    for okey in bucket_manager.all_objects(bucket):
        print(okey.key)

    return
#######################################################################################################
#######################################################################################################
#######################################################################################################


if __name__ == '__main__':
    try:
        print("🔥  "*40)
        cli()
        
    except ClientError as e:
        print("An error occured of type {0}".format(e))
    except TypeError as e:
        print("An error occured of type {0}".format(e))
     
