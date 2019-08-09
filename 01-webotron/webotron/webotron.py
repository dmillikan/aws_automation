import boto3
import click
import botocore
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
@buckets.command("list")
@click.option("--region", "region", default=None, help ='Bucket Region')
def list_buckets(region):
    """List all s3 buckets"""
    if not region:
    #    print('\n \n \n \n \t \t \t \t here\n \n \n ')
        for b in s3.buckets.all():
            print(b.name)
    else:
        print('Showing buckets in region {0} \n \n'.format(region))
        for b in s3.buckets.filter(Filter=[{'name':'LocationConstraint','value':region}]):
            print('\t {0} is in {1}'.format(b.name,client.get_bucket_location(Bucket=b.name)['LocationConstraint'] or 'us-east-1' ))

    return
#######################################################################################################
@buckets.command("create")
@click.argument("name")
@click.option("--region", "region", default='us-east-1', help ='Bucket Region')
@click.option("--public", "public", default=False, is_flag=True, help ='Make Bucket Public')
def create_bucket(name,public,region):
    """Create new s3 bucket"""
    b = None

    try:
        if region.lower() != 'us-east-1':
            b = s3.create_bucket(
                Bucket = name,
                CreateBucketConfiguration={"LocationConstraint":region}
            )
        else:
            b = s3.create_bucket(Bucket = name)

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
