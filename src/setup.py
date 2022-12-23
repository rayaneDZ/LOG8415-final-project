import boto3
import time
import json

AWS_REGION = 'us-east-1'
INSTANCE_TYPE = "t2.micro"
KEY_PAIR_NAME = "vockey"
AMI_ID = "ami-061dbd1209944525c"
# AT LEAST 4 (1 stand-alone, 1 proxy, 1 managment node, 3 data nodes)
NBR_OF_INSTANCES = 5

ec2_client = boto3.client("ec2", region_name=AWS_REGION)
ec2_resource = boto3.resource('ec2', region_name=AWS_REGION)


def get_vpc_id_and_subnet_id():
    """
    This function returns the id of the default vpc and of the first subnet.
    Returns vpc_id, subnet_id.
    """
    response = ec2_client.describe_vpcs()
    vpc_id = response['Vpcs'][0]['VpcId']
    response = ec2_client.describe_subnets(
        Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
    )
    subnet_id = response['Subnets'][0]['SubnetId']
    return vpc_id, subnet_id


def create_sg(vpcID):
    """
    This function creates a new security group for the VPC.
    vpcID : is the ID of the concerned VPC.
    Returns the security group ID.
    """
    response = ec2_client.create_security_group(GroupName="MySQL Security Group",
                                                Description='security group for MySQL instances',
                                                VpcId=vpcID)
    security_group_id = response['GroupId']
    ipPermissionsList = [
        {'IpProtocol': 'tcp',
         'FromPort': 80,
         'ToPort': 80,
         'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
        {'IpProtocol': 'tcp',
         'FromPort': 22,
         'ToPort': 22,
         'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
        {'IpProtocol': 'tcp',
         'FromPort': 443,
         'ToPort': 443,
         'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
        {'IpProtocol': '-1',
         'FromPort': -1,
         'ToPort': -1,
         'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
    ]
    ec2_client.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=ipPermissionsList)
    return security_group_id


def create_ec2_instances(nbr, type, sg_id, subnet_id):
    """
    This function creates EC2 instances.
    nbr : is the desired number of instances to be created.
    type : the instance type. m4.large for example.
    sg_id : is the ID of the security group that you wish your instaces to follow.
    subnet_id : is the subnet where you instances will reside.
    """
    response = ec2_client.run_instances(
        MinCount=nbr,
        MaxCount=nbr,
        ImageId=AMI_ID,
        InstanceType=type,
        KeyName=KEY_PAIR_NAME,
        NetworkInterfaces=[{
            "DeviceIndex": 0,
            "Groups": [sg_id],
            "AssociatePublicIpAddress": True,
            "SubnetId": subnet_id
        }]
    )
    return response['Instances']


def wait_until_running():
    """
    This function waits for the newly created instances.
    It gets the instances by filtering by the security goupe name.
    It returns a dictionary containing the id, private ip, public ip of each instance
    """
    # waiting 1 minute to make sure the instances are running.
    time.sleep(60)

    data = {}
    count = 0
    instances = ec2_resource.instances.filter(
        Filters=[{'Name': 'instance.group-name', 'Values': ['MySQL Security Group']}])

    for instance in instances:
        count += 1
        if count == 1:
            data["stand-alone_node"] = {"InstanceId": instance.id,
                                        "PrivateIpAddress": instance.private_ip_address,
                                        "PublicIpAddress": instance.public_ip_address}
        elif count == 2:
            data["mgmt_node"] = {"InstanceId": instance.id,
                                 "PrivateIpAddress": instance.private_ip_address,
                                 "PublicIpAddress": instance.public_ip_address}
        else:
            data["data_node_"+str(count - 3)] = {"InstanceId": instance.id,
                                                 "PrivateIpAddress": instance.private_ip_address,
                                                 "PublicIpAddress": instance.public_ip_address}
    return data

 # Start
print("\n############### SETTING UP THE ARCHITECTURE ###############\n")

print("Getting the vpc and the subnet IDs...")
vpcID, subnet_id = get_vpc_id_and_subnet_id()
print("IDs obtained!")

print("Creating the security group...")
sg_id = create_sg(vpcID)
print("Security group created!\n")

print("Creating 6 EC2 instances...")
instances = create_ec2_instances(
    NBR_OF_INSTANCES, INSTANCE_TYPE, sg_id, subnet_id)
print("EC2 instances created!\n")

print("Waiting 1 minute for the instances to become in the running state")
data = wait_until_running()
print("All instances are running!")

# Serializing json
json_object = json.dumps(data, indent=4)

# Writing to collected_data.json
with open("collected_data.json", "w") as outfile:
    outfile.write(json_object)
print("collected_data.json file created!")


print("\n############### DONE SETTING UP THE ARCHITECTURE ###############\n")
