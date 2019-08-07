import boto3
import click
import botocore

session = boto3.Session(profile_name='automation')
s3 = session.resource('s3')

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
#@click.option('--project', default=None, help ='Only instances of a given project')
def list_buckets():
    """List all s3 buckets"""
    for b in s3.buckets.all():
        print(b.name)

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
        print("An error occured of type {0}".format(e))#
    except TypeError as e:
        print("An error occured of type {0}".format(e))
