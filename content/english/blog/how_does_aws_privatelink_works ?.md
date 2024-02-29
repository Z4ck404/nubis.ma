
---
title: "How Does AWS PrivateLink Works ?"
image: "/images/image-placeholder.png"
categories: ["AWS", "Terraform"]
tags: ["AWS", "Terraform"]
date: 2024-02-29T14:16:43Z
author: "Unknown Author"
---

### How Does AWS PrivateLink Work ?

![](/assets/images/medium/1*NbGHK8-z-7hG_aZoO3Xv5g.png)

In the world of cloud networks, security and confidentiality are crucial. [AWS
PrivateLink](https://docs.aws.amazon.com/vpc/latest/privatelink/what-is-
privatelink.html) is an essential service that bridges the gap between service
exposure and network security in an elegant way. By providing a private
connection to services hosted on AWS, PrivateLink ensures that traffic between
your VPC and the services you consume does not traverse the public internet.
This not only increases security, but also reduces exposure to potential
threats and improves network latency.

The aim of this article is twofold. **First** , we’ll break down how AWS
PrivateLink works, highlighting its underlying mechanisms and explaining why
it’s becoming an essential part of the AWS secure architecture. **Next** ,
we’ll demonstrate a practical configuration: deploying a simple Flask
application endpoint securely using AWS PrivateLink. By the end of this read,
you’ll have a complete understanding of PrivateLink and a step-by-step guide
to leveraging its capabilities for your own services.

![](/assets/images/medium/1*lEF0q6qrXzjJVe5blYV0Gg.png)[AWS PrivateLink
concepts](https://docs.aws.amazon.com/vpc/latest/privatelink/concepts.html)

#### What’s AWS PrivateLink ?

AWS PrivateLink is a network service provided by AWS that enables customers to
access services across the AWS network in a secure and scalable manner.
PrivateLink is built around the concept of service endpoints. These are
provisioned in your VPC and act as a secure entry point to services hosted on
AWS or on-premises. Using AWS PrivateLink, services are exposed via the AWS
network backbone, rather than the public internet, increasing security and
reducing exposure to common threats such as DDoS attacks.

PrivateLink addresses several of the most critical issues in cloud networking:

  * **Security** : it secures network traffic by ensuring it never leaves the Amazon network, significantly reducing the risk of interception or exposure.
  * **Data exposure** : By avoiding the public Internet, PrivateLink limits data exposure, providing a more controlled environment and reducing the attack surface.
  * **Network complexity** : PrivateLink simplifies networking architecture by eliminating the need for Internet gateways, NAT devices and VPN connections for access to private services.
  * **Scalability** : PrivateLink is designed to be highly scalable and manage the throughput and connections required without customers having to manage the underlying infrastructure.

Compared to standard public endpoints, PrivateLink offers a number of
advantages:

  * **Low latency** : Because traffic is routed within the AWS network, latency is often lower than if data were routed over the public internet.
  * **Consistency** : Network performance is more consistent because it is not subject to the variable conditions of the public Internet.
  * **Simplicity** : With PrivateLink, you only need to manage your VPC and not the public aspects of your services, which simplifies network management.
  * **Compliance** : For regulated industries with strict data handling requirements, PrivateLink helps maintain compliance by keeping traffic off the public internet.

#### How does it work ?

![](/assets/images/medium/1*eLQ1trCPnw1ipP3W0RGFkQ.png)[What is AWS
PrivateLink?](https://docs.aws.amazon.com/vpc/latest/privatelink/what-is-
privatelink.html)

AWS PrivateLink components mainly include VPC service endpoints, endpoint
services and network load balancers (NLBs).

Service endpoints are the PrivateLink-powered interfaces that live in your
VPC, allowing you to connect to supported AWS services or your own services
privately. These endpoints are highly resilient and scalable interfaces that
provide a consistent network experience. Endpoint services, on the other hand,
are the services you create or subscribe to that are accessible via
PrivateLink. These can be AWS services such as S3, DynamoDB, or your own
services, such as a Flask application, that you want to expose securely.

The Network Load Balancer plays an important role in the PrivateLink
architecture. When you create an endpoint service, an NLB is used to
distribute incoming traffic across multiple targets, such as EC2 instances,
containers or IP addresses, in one or more availability zones. The NLB acts as
a bridge between your VPC and the endpoint service, ensuring high availability
and automatic scaling of incoming traffic.

![](/assets/images/medium/1*Yzpuv03LmC_fnwPqYt9T5g.png)Simplified AWS
PrivateLink

In a typical PrivateLink configuration, the owner of an AWS account creates an
endpoint service and specifies the NLB to be associated with that service.
Consumers of other VPCs can then connect to this service by creating an
interface VPC endpoint (also known as an interface endpoint) in their own VPC.
This interface endpoint acts as an elastic network interface (ENI) with
private IP addresses that act as an entry point for traffic destined for the
service.

PrivateLink securely routes traffic from the consumer’s VPC to the service by
encapsulating it in the AWS network, without ever exposing it to the public
internet. Network traffic is directed to the NLB via the interface endpoints,
which then routes the traffic to the service.

### **[Service Provider] Expose a Flask application through PrivateLink**

#### Step 1: Deploy a Flask Application

The Flask application we will be deploying is pretty simple :

    
    
    from flask import Flask  
    app = Flask(__name__)  
      
    @app.route('/')  
    def hello_world():  
        return 'Hello, PrivateLink World!'  
      
    if __name__ == '__main__':  
        app.run(host='0.0.0.0', port=5000)

First create a private EC2 instance with the following user data script that
installs Python, Flask and deploys our application :

    
    
    #!/bin/bash  
      
    # Update the instance  
    sudo yum update -y  # For Amazon Linux 2  
    # sudo apt-get update -y && sudo apt-get upgrade -y  # For Ubuntu  
      
    # Install Python 3 and pip  
    sudo yum install python3 python3-pip -y  # For Amazon Linux 2  
    # sudo apt-get install python3 python3-pip -y  # For Ubuntu  
      
    # Upgrade pip and setuptools using sudo to ensure system-wide effect  
    sudo pip3 install --upgrade pip setuptools  
      
    # Create a Python virtual environment in our app directory  
    mkdir -p /opt/myflaskapp  
    cd /opt/myflaskapp  
    python3 -m venv venv  
    source venv/bin/activate  
      
    # Install Flask inside the virtual environment  
    pip install Flask  
      
    # Write the Flask app to a file  
    cat > app.py << EOF  
    from flask import Flask  
    app = Flask(__name__)  
      
    @app.route('/')  
    def hello_world():  
        return 'Hello, PrivateLink World!'  
      
    if __name__ == '__main__':  
        app.run(host='0.0.0.0', port=5000)  
    EOF  
      
      
    # Run the app with the virtual environment activated  
    FLASK_APP=app.py flask run --host=0.0.0.0 --port=5000

When creating the EC2 instance, make sure to allow inbound traffic in port
**5000** from the VPC CIDR.

![](/assets/images/medium/1*taeV7_Im_2EyDmdzxK3a7A.png)Launching an EC2
instance

#### Step 2: Configure Network Load Balancer (NLB)

Now create the NLB with a listener on port 5000 that forwards traffic to a
Target Group where you register the EC2 instance created above as a target:

![](/assets/images/medium/1*Krtb5WBi8t403fwsfMDDpg.png)Target Group with the
EC2 instance as Target

⚠️ If the targets are unhealthy, make sure you allow the traffic on port 5000
from the VPC CIDR in the EC2 Security group.

![](/assets/images/medium/1*C2BDV-6iqO1jAH44SeFg3w.png)Creating the NLB for
the Privatelink
setup![](/assets/images/medium/1*jLC6F-8J_v1lwUupRDSyog.png)Add a listener on
port 5000 and associate it with a target group

#### Step 3: Set Up an AWS PrivateLink Endpoint Service

Create the VPC Endpoint Service (Network) and choose the NLB from above:

![](/assets/images/medium/1*CS6MSlRwsrfmCX24CxTw6w.png)Creating Endpoint
Service and associate it with the NLB

Once created, copy the Service name (you will need it later) and allow the
consumer principal (arn:aws:iam::378918992955:root which is same account in
this case but it can be a different account):

![](/assets/images/medium/1*pB_2Hv-WY6QuiJdk6twsHA.png)Allow [Consumer
account] principal

### [Service Consumer] Access the Flask application through PrivateLink

#### Step 1: Create a VPC Endpoint for the AWS PrivateLink Service

On service consumer side, create a VPC endpoint (interface endpoint) and
specify the Service Name from the Endpoint Service above:

![](/assets/images/medium/1*sNjOGMZ_GA6ZMvJRyi-rhQ.png)Creating a VPC Endpoint
in the consumer VPC

Once it’s created, it will remain in**pending state** until the Endpoint
Service accepts the Endpoint connection (This is required sine acceptance
required setting is enabled for the Endpoint Service):

![](/assets/images/medium/1*lSeZpakZTNZDFP9xUSrVbQ.png)Endpoint in pending
state

The Endpoint Service should accept the connection:

![](/assets/images/medium/1*l6TdS26FD5KNqdu_Wqqj7g.png)Endpoint Service
accepting the Endpoint connection

⚠️ One last setting to do is to allow the traffic from the consumer VPC on
port 5000 in the Network load balancer security group and do the same in the
endpoint security group as well (allow resource within the consumer vpc to use
the endpoint):

![](/assets/images/medium/1*1vV1Iaf6mC_uE_eNp0vEoQ.png)Allowing traffic from
consumer VPC on the NLB Security group

#### Step 2: Verifying Your AWS PrivateLink Setup

To test the setup,create a public EC2 instance that you can SSH into and see
if you can access the Flask application through the PrivateLink Endpoint:

![](/assets/images/medium/1*ZApEAKpQLASqHBJSIKg2Cw.png)Public [consumer] EC2
instance

Testing the connection through the PrivateLink using the endpoint DNS Name and
the Flask application port :

    
    
    curl -v  vpce-0b0f658879e545d48-kxrvnws3.vpce-svc-0bcf29ae4e736df34.us-east-1.vpce.amazonaws.com:5000

![](/assets/images/medium/1*dylvI-AkjJIYdKA4LfDimQ.png)

#### **Conclusion:**

AWS PrivateLink is widely used by service providers to ensure direct and
secure communication with customer accounts, minimising exposure to the public
internet. Its ability to provide private connectivity has made it an
indispensable feature for organisations that prioritise network security and
efficiency.

I encourage you to take advantage of PrivateLink, as it offers a path to a
more secure and controlled cloud environment. Experiment with its offerings
and integrate it into your service architecture to discover its full potential
for securing communications within the AWS ecosystem.

#### Read more:

[AWS Inter-Region PrivateLink using Terraform](https://awsmorocco.com/inter-
region-aws-privatelink-337c5115fbb9)

![](/assets/images/medium/stat?event=post.clientViewed&referrerSource=full_rss&postId=faddc730ed73)

* * *

[How Does AWS PrivateLink Works ?](https://awsmorocco.com/how-does-aws-
privatelink-works-faddc730ed73) was originally published in [AWS
Morocco](https://awsmorocco.com) on Medium, where people are continuing the
conversation by highlighting and responding to this story.

