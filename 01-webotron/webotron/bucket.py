# -*- code utf-8 -*-

"""Classes for S3 Buckets"""

from botocore.exceptions import ClientError
import mimetypes
from pathlib import Path

import util


class BucketManager:
    """Manage an S3 Bucket"""

    def __init__(self, session):
        """Creates a BucketManger objcet"""
        self.session = session
        self.s3 = self.session.resource('s3')

    def get_bucket_region(self, bucket):
        """Get the region for a bucket"""
        bucket_region = self.s3.meta.client.get_bucket_location(
            Bucket=bucket.name)

        return bucket_region["LocationConstraint"] or 'us-east-1'

    def get_bucket_url(self, bucket):
        """Get the website URL for bucket"""
        return "http://{0}.{1}".format(bucket.name, util.get_region(self.get_bucket_region(bucket)).url)

    def all_buckets(self, region=None):
        """Get an iterator of all buckets"""
        return self.s3.buckets.all()

    def all_objects(self, bucket):
        """Get an iterator of all objects within a bucket"""
        return self.s3.Bucket(bucket).objects.all()

    def init_bucket(self, bucket_name, region=None):
        """Initialzie S3 Bucket"""

        s3_bucket = self.s3.Bucket(bucket_name)
        # print(s3_bucket)
        try:
            # print('will attempt to create bucket {0} in region {1}'.format(bucket_name,region))
            if region and region.lower() != 'us-east-1':
                # print('\tbucket does not exist and region is no us-east-1')
                s3_bucket = self.s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={
                        "LocationConstraint": region}
                )
            else:
                s3_bucket = self.s3.create_bucket(Bucket=bucket_name)

        except ClientError as e:
            if e.response['Error']['Code'] == "BucketAlreadyOwnedByYou":
                s3_bucket = self.s3.Bucket(bucket_name)
            else:
                raise e

        return s3_bucket

    def give_public_access(self, bucket):
        """Give S3 bucket public access"""

        pol = bucket.Policy()
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
            }""" % bucket.name
        pol.put(Policy=polstr)

        return

    def host_website(self, bucket, region=None):
        """Host Website from Bucket"""
        if not region:
            region = 'us-east-1'
        ws = bucket.Website()
        ws.put(WebsiteConfiguration={
            'ErrorDocument': {
                'Key': 'error.html'
            },
            'IndexDocument': {
                'Suffix': 'index.html'
            }})
        # url = "http://{0}.s3-website-{1}.amazonaws.com".format(
        #     bucket.name, region)
        # print(url)
        print(self.get_bucket_url(bucket))
        return

    def get_local_path(self, path, root, bucket_name=None):

        s3_bucket = self.init_bucket(bucket_name)

        for p in path.iterdir():
            if p.is_dir():
                self.get_local_path(p, root, bucket_name)
            if p.is_file():
                if not bucket_name:
                    print('File {0} has a key of {1}'.format(
                        p, p.relative_to(root)))
                else:
                    print('Uploading {0} with key {1} to {2}'.format(
                        p, p.relative_to(root), s3_bucket))
                    self.upload_file(s3_bucket,
                                     str(p), str(p.relative_to(root)))
            # if p.is_file() :
        return

    def upload_file(self, bucket, path, key):
        content_type = mimetypes.guess_type(key)[0] or 'text/plain'
        bucket.upload_file(
            path,
            key,
            ExtraArgs={'ContentType': content_type}
        )
        return

    def sync_path(self, pathname, bucket_name):
        """Synchronize Local Path to S3 Bucket"""
        path = Path(pathname).expanduser().resolve()
        self.get_local_path(path, path, bucket_name)
