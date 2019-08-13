#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Deploy Websites with AWS 

    Webotron automates the process of deploying static websites to AWS S3
    - Configure S3
        - Create them
        - Set them up for static website hosting
        - Deploy local files to them
"""

import mimetypes
from pathlib import Path

import boto3
import botocore
import click
from botocore.exceptions import ClientError

session = boto3.Session(profile_name='automation')
s3 = session.resource('s3')
client = boto3.client('s3')

#######################################################################################################
def bucket_give_public_access(name,region):
    """Give s3 bucket pubic access"""
    b = s3.Bucket(name)
    pol = b.Policy()
    polstr = """{
  "Version":"2012-10-17",
  "Statement":[
    {
      "Sid":"AddPerm",
      "Effect":"Allow",
      "Principal": "*",
      "Action":["s3:GetObject"],
      "Resource":["arn:aws:s3:::%s/*"]
    }
  ]
}""" % name
    pol.put(Policy=polstr)
    bucket_make_website(name,region)
    return
#######################################################################################################
def bucket_make_website(name,region):
    """Give s3 bucket pubic access"""
    b = s3.Bucket(name)
    ws = b.Website()
    ws.put(WebsiteConfiguration={
        'ErrorDocument': {
            'Key': 'error.html'
        },
        'IndexDocument': {
            'Suffix': 'index.html'
        }})
    url = "http://{0}.s3-website-{1}.amazonaws.com".format(name , region)
    print(url)
    return
#######################################################################################################
def get_local_path(path,root,bucket_name=None):
    for p in path.iterdir():
        if p.is_dir() : get_local_path(p,root,bucket_name)
        if p.is_file() : 
            if not bucket_name: 
                print('File {0} has a key of {1}'.format(p,p.relative_to(root)))
            else : 
                print('Uploading {0} with key {1} to {2}'.format(p,p.relative_to(root),s3.Bucket(bucket_name)))
                upload_file(s3.Bucket(bucket_name),str(p),str(p.relative_to(root)))
        #if p.is_file() :
    return
#######################################################################################################
def upload_file(s3_bucket,path,key):
    content_type = mimetypes.guess_type(key)[0] or 'text/plain'
    s3_bucket.upload_file(
        path,
        key,
        ExtraArgs={'ContentType':content_type}
    )
    return   
#######################################################################################################
#######################################################################################################
#######################################################################################################
@click.group()
def cli():
    """Webotron Synchronizes Local Directories with S3"""
#######################################################################################################
@cli.group("buckets")
def buckets():
    """Commands for Buckets"""
#######################################################################################################
@buckets.command("sync")
@click.argument("pathname",type=click.Path(exists=True))
@click.option("--bucket", "bucket", default=None)
def sync_path(pathname,bucket):
    """Synchronize Local Path to S3 Bucket"""
    path = Path(pathname).expanduser().resolve()
    get_local_path(path,path,bucket)
    
    return

#######################################################################################################
@buckets.command("create")
@click.argument("name")
@click.option("--region", "region", default='us-east-1', help ='Bucket Region')
@click.option("--public", "public", default=False, is_flag=True, help ='Make Bucket Public')
def create_bucket(name,public,region):
    """Create new s3 bucket"""

    try:
        if region.lower() != 'us-east-1':
            s3.create_bucket(
                Bucket = name,
                CreateBucketConfiguration={"LocationConstraint":region}
            )
        else:
            s3.create_bucket(Bucket = name)

        print('\n \tBucket {0} created successfully in region {1}\n'.format(name,region))

    except ClientError as e:
        if e.response['Error']['Code'] == "BucketAlreadyOwnedByYou":
            print('\n \tBucket {0} already created in region {1}\n'.format(name,region))
            pass
        else:
            raise e

    if public:
        bucket_give_public_access(name,region)

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
    for okey in s3.Bucket(bucket).objects.all():
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
