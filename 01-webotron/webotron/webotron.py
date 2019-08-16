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

session = None
bucket_manager = None
client = None

#######################################################################################################
#######################################################################################################
#######################################################################################################
@click.group()
@click.option('--profile', default=None, help="Use a given AWS profile")
def cli(profile):
    """Webotron Synchronizes Local Directories with S3"""
    global session, bucket_manager, client
    session_cfg = {}
    

    if profile:
        session_cfg['profile_name'] = profile

    session = boto3.Session(**session_cfg)
    bucket_manager = BucketManager(session)

    client = boto3.client('s3')

#######################################################################################################
@cli.group("buckets")
def buckets():
    """Commands for Buckets"""
#######################################################################################################
@buckets.command("sync")
@click.argument("pathname", type=click.Path(exists=True))
@click.argument("bucketname")
def sync_path(pathname, bucketname):
    """Synchronize Local Path to S3 Bucket"""
    bucket_manager.sync_path(pathname, bucketname)

    return
#######################################################################################################
@buckets.command("list")
def list_buckets():
    """List all s3 buckets"""

    for b in bucket_manager.all_buckets():
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
        public = True
        bucket_manager.host_website(s3_bucket, region)

    if public:
        bucket_manager.give_public_access(s3_bucket)

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
        cli()
    except ClientError as e:
        print("An error occured of type {0}".format(e))
    except TypeError as e:
        print("An error occured of type {0}".format(e))
