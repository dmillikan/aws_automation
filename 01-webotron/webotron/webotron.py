import boto3
import click
import botocore

session = boto3.Session(profile_name='automation')
s3 = session.resource('s3')
client = boto3.client('s3')

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
        print('\n \n \n \n \t \t \t \t here\n \n \n ')
        for b in s3.buckets.all():
            print(b.name)
    else:
        print('Showing buckets in region {0} \n \n'.format(region))
        for b in s3.buckets.filter(Filter=[{'Name':'LocationConstraint','Values':[region]}]):
            print('\t {0} is in {1}'.format(b.name,client.get_bucket_location(Bucket=b.name)['LocationConstraint'] or 'us-east-1' ))

    return
#######################################################################################################
@buckets.command("create")
@click.argument("name")
@click.option("--region", "region", default='us-east-1', help ='Bucket Region')
@click.option("--public", "public", default=False, is_flag=True, help ='Make Bucket Public')
def create_bucket(name,public,region):
    """Create new s3 bucket"""
    b = s3.Bucket(name)
    try:
        if region.lower() != 'us-east-1':
            b.create(CreateBucketConfiguration={"LocationConstraint":region})
        else:
            b.create()
        print('\n \t \tBucket {0} created successfully in region {1}\n'.format(name,region))
    except botocore.exceptions.ClientError as e:
        #if e.response['Error']['Code'] == "InvalidLocationConstraint":
        #    print("Please enter a valid region \n \tYou entered {0}\n \tValid options are 'EU'|'eu-west-1'|'us-west-1'|'us-west-2'|'ap-south-1'|'ap-southeast-1'|'ap-southeast-2'|'ap-northeast-1'|'sa-east-1'|'cn-north-1'|'eu-central-1'".format(region))
        #else:
    #        print("An error occured of type {0}".format(e))
        print(e.response['Error']['Message'] )
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
    except botocore.exceptions.ClientError as e:
        print("An error occured of type {0}".format(e))
    except TypeError as e:
        print("An error occured of type {0}".format(e))
