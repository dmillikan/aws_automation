# -*- code utf-8 -*-

"""Classes for S3 Buckets"""
import boto3
from botocore.exceptions import ClientError
import mimetypes
from pathlib import Path
from hashlib import md5
import io
import util
from functools import reduce


class BucketManager:
    """Manage an S3 Bucket"""

    CHUNK_SIZE = 8388608

    def __init__(self, session):
        """Creates a BucketManger objcet"""
        self.session = session
        self.s3 = self.session.resource('s3')
        self.manifest = {}
        self.local_manifest = {}
        self.delete_manifest = {}
        self.transfer_config = boto3.s3.transfer.TransferConfig(
            multipart_chunksize=self.CHUNK_SIZE,
            multipart_threshold=self.CHUNK_SIZE
        )

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

    def find_bucket(self, bucket_name, pattern_match, region=None):
        """Get all buckets that match pattern"""
        buckets = []
        for bucket in self.all_buckets(region=region):
            if (pattern_match and bucket.name.startswith(bucket_name)) \
                    or (bucket.name == bucket_name):
                buckets.append(bucket)

        return buckets

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
        
        return self.get_bucket_url(bucket)

    def get_local_path(self, path, root, s3_bucket):
        """Get List of Local Objects and Hash"""
        for p in path.iterdir():
            if p.is_dir():
                self.get_local_path(p, root, s3_bucket.name)
            if p and p.is_file():
                self.local_manifest[str(p.relative_to(root))] = {
                    "Path": str(p), "ETag": self.calculate_etag(p)}
        return

    @staticmethod
    def hash_data(data):
        """Generate MD5 Hash on Data"""
        hash = md5()

        # if str(type(data)) == "<class 'str'>":
        #     print('here')
        #     hash.update(bytes(data,encoding='utf-8'))
        # else:
        #     hash.update(data)

        hash.update(data)
        return hash

    def calculate_etag(self, path):
        """For a given path, calculate the etag"""
        hashes = []

        with open(path, 'rb') as p:
            while True:
                data = p.read(self.CHUNK_SIZE)
                if not data:
                    break
                hashes.append(self.hash_data(data))

        if not hashes:
            return
        elif len(hashes) == 1:
            return hashes[0].hexdigest()
        else:
            # print("\n\tFile {0} has more than 1 part".format(path))
            red = reduce(lambda x, y: x + y, (h.digest() for h in hashes))
            hash = "{0}-{1}".format(self.hash_data(red).hexdigest(),
                                    len(hashes))
            return hash

    def load_manifest(self, s3_bucket):
        """Load Paginator Manifest for Caching Purposes"""
        paginator = self.s3.meta.client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=s3_bucket.name):
            for obj in page.get('Contents', []):
                self.manifest[obj['Key']] = str(obj['ETag']).replace('"', '')
        return

    def upload_file(self, s3_bucket, path, key):
        print('\tUploading {0} with key {1} to {2}'.format(
            path, key, s3_bucket))
        content_type = mimetypes.guess_type(key)[0] or 'text/plain'
        s3_bucket.upload_file(
            path,
            key,
            ExtraArgs={'ContentType': content_type},
            Config=self.transfer_config
        )
        return

    def sync_path(self, pathname, bucket_name, delete):
        """Synchronize Local Path to S3 Bucket"""
        path = Path(pathname).expanduser().resolve()
        s3_bucket = self.init_bucket(bucket_name)
        self.load_manifest(s3_bucket)
        self.get_local_path(path, path, s3_bucket)

        # print(self.manifest)
        # print(self.local_manifest)

        for f in self.local_manifest.items():
            do_upload = False
            if f[0] in self.manifest:
                if self.manifest[f[0]] != f[1]["ETag"]:
                    do_upload = True
            else:
                do_upload = True

            if do_upload:
                self.upload_file(s3_bucket, f[1]["Path"], f[0])
        if delete:
            del_obj = []
            for f in self.manifest.items():
                if f[0] not in self.local_manifest:
                    print("\tWe will delete {0}".format(f[0]))
                    del_obj.append({"Key": f[0]})

            if del_obj:
                self.delete_manifest = {"Objects": del_obj}
                s3_bucket.delete_objects(Delete=self.delete_manifest)

    def delete_bucket(self, bucket_name, domain_manager, pattern_match=False):
        """Empties Bucket and Deletes It"""
        buckets = []
       
        buckets = self.find_bucket(bucket_name, pattern_match)
        if not buckets:
            print("\t\tNo Buckets found to delete")
        for b in buckets:
            if b.name in util.protected_buckets:
                print("\t\t{0}\n\t\t💀  Will not delete protected bucket {1} 💀\n\t\t{2}".format('='*(len(b.name)+39),
                                                                                          b.name, '='*(len(b.name)+39)))
            else:
                hasObj = bool(len(list(b.objects.all().limit(1))))
                if hasObj:
                    print(
                        "\t\tWe will empty all objects from bucket {0}".format(b.name))
                    for o in b.objects.all():
                        if o.key:
                            print("\t\t\tWe will delete {0} from bucket {1}".format(
                                o.key, b.name))
                            b.delete_objects(
                                Delete={'Objects': [{'Key':  o.key}], 'Quiet': True})
                print("\t\tWe will delete bucket {0}".format(b.name))
                ws = b.Website()
                try:
                    ws.load()
                    print('\t\tWe need to delete the DNS')
                    zone = domain_manager.get_hosted_zone(
                        ".".join(b.name.split('.')[-2:]))
                    
                    print(domain_manager.delete_s3_domain_record(b,zone))

                    

                except ClientError as e:
                    if e.response['Error']['Code'] == "NoSuchWebsiteConfiguration":
                        pass
                    else:
                        raise e

                b.delete()
