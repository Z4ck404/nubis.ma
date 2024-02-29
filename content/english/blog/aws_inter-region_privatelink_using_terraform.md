
---
title: "AWS Inter-Region PrivateLink using Terraform"
image: "/images/image-placeholder.png"
categories: ["AWS", "Terraform"]
tags: ["AWS", "Terraform"]
date: 2024-02-29T14:16:39Z
author: "Unknown Author"
---

![](/assets/images/medium/0*tGFRJlprmRQaeCuN)Photo by [Taylor
Vick](https://unsplash.com/@tvick?utm_source=medium&utm_medium=referral) on
[Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)

AWS PrivateLink provides a secure and reliable way to connect VPCs within the
same region, but it doesn’t directly support connections between VPCs in
different regions. To address this limitation, inter-Region VPC peering offers
a viable solution.

#### Inter-Region VPC Peering x PrivateLink:

Inter-Region VPC peering enables private connectivity between VPCs in
different AWS regions ( have a look into [this previous
article](https://awsmorocco.com/aws-multi-region-vpc-peering-using-
terraform-a0b8aabf084b) for a deep dive into AWS VPC peering).

#### **How it works:**

![](/assets/images/medium/1*5m6JrsNSOYEaALxgjr91vg.png) VPC Peering x
PrivateLink

1 — The Service Provider VPC hangs out in region A (let’s say us-east-1). Now,
the Service Consumer VPC wants a local interface VPC endpoint, but in a
different spot, region B (like us-west-2).

2 — If you’re not keen on directly connecting the Consumer VPC and the main
Service Provider VPC (not the best idea, they say), you can birth another VPC
in the same region as the consumer (us-west-2). Connect this new kid (let’s
call it Outpost VPC) in the same region as the customer to the main Service
Provider VPC.

3 — Time to play matchmaker! Enable PrivateLink between the Outpost VPC (us-
west-2) and the Consumer VPC (also us-west-2). Create a VPC endpoint Service
in the Outpost VPC with the NLB that gets its targets from the Service
Provider VPC (reachable through the peering).

This whole shebang makes even more sense when the Consumer VPC and the Service
Provider VPCs are in different accounts or when a direct connection between
them is a no-go for security or compliance reasons.

![](/assets/images/medium/1*ncCpQmXAT8nRq-b58dyBGw.png)Cross-account inter-
region PrivateLink

#### Let’s Set it Up:

**1 —** Create VPCs to emulate the Service provider, Service Provider Outpost
and the Consumer VPC:

    
    
    module "vpc_service_provider" {  
      source = "terraform-aws-modules/vpc/aws"  
      name   = "awsmorocco_service_provider_vpc"  
      cidr   = "10.10.0.0/16"  
      
      azs             = ["us-east-1a"]  
      private_subnets = ["10.10.1.0/24"]  
      public_subnets  = ["10.10.2.0/24"]  
      
      enable_nat_gateway = true  
      single_nat_gateway = true  
      
      enable_dns_hostnames = true  
      enable_dns_support   = true  
      
      providers = {  
        aws = aws.service_provider  
      }  
    }  
      
    module "vpc_service_provider_outpost" {  
      source = "terraform-aws-modules/vpc/aws"  
      name   = "awsmorocco_service_provider_outpost"  
      cidr   = "10.11.0.0/16"  
      
      azs             = ["us-west-2a"]  
      private_subnets = ["10.11.1.0/24"]  
      public_subnets  = ["10.11.2.0/24"]  
      
      enable_nat_gateway = true  
      single_nat_gateway = true  
      
      enable_dns_hostnames = true  
      enable_dns_support   = true  
      
      providers = {  
        aws = aws.service_provider_outpost  
      }  
    }  
      
    module "vpc_service_consumer" {  
      source = "terraform-aws-modules/vpc/aws"  
      name   = "awsmorocco_service_consumer"  
      cidr   = "10.2.0.0/16"  
      
      azs                = ["us-west-2a"]  
      private_subnets    = ["10.12.1.0/24"]  
      public_subnets     = ["10.12.2.0/24"]  
      enable_nat_gateway = true  
      single_nat_gateway = true  
      
      enable_dns_hostnames = true  
      enable_dns_support   = true  
      
      providers = {  
        aws = aws.consumer  
      }  
    }

The providers configuration looks like this:

    
    
    provider "aws" {  
      alias  = "consumer"  
      region = "us-east-1"  
    }  
      
    provider "aws" {  
      alias  = "service_provider"  
      region = "us-west-2"  
    }  
      
    provider "aws" {  
      alias  = "service_provider_outpost"  
      region = "us-west-2"  
    }

**2 —** Once the VPCs are created, enable the peering between the Service
provider VPC and the Outpost PVC:

    
    
    resource "aws_vpc_peering_connection" "this" {  
      vpc_id      = module.vpc_service_provider_outpost.vpc_id  
      peer_vpc_id = module.vpc_service_provider.vpc_id  
      peer_region = "us-east-1"  
      auto_accept = false  
      
      provider = aws.service_provider_outpost  
    }  
      
    resource "aws_vpc_peering_connection_accepter" "this" {  
      provider                  = aws.service_provider  
      vpc_peering_connection_id = aws_vpc_peering_connection.this.id  
      auto_accept               = true  
    }  
      
    resource "aws_vpc_peering_connection_options" "this" {  
      vpc_peering_connection_id = aws_vpc_peering_connection.this.id  
      accepter {  
        allow_remote_vpc_dns_resolution = true  
      }  
      
      provider = aws.service_provider  
    }  
      
    locals {  
      requester_route_tables_ids = concat(module.vpc_service_provider_outpost.public_route_table_ids, module.vpc_service_provider_outpost.private_route_table_ids)  
      accepter_route_tables_ids  = concat(module.vpc_service_provider.public_route_table_ids, module.vpc_service_provider.private_route_table_ids)  
    }  
      
    resource "aws_route" "requester" {  
      count                     = length(local.requester_route_tables_ids)  
      route_table_id            = local.requester_route_tables_ids[count.index]  
      destination_cidr_block    = module.vpc_service_provider.vpc_cidr_block  
      vpc_peering_connection_id = aws_vpc_peering_connection.this.id  
      
      provider = aws.service_provider_outpost  
    }  
      
    resource "aws_route" "accepter" {  
      count                     = length(local.accepter_route_tables_ids)  
      route_table_id            = local.accepter_route_tables_ids[count.index]  
      destination_cidr_block    = module.vpc_service_provider_outpost.vpc_cidr_block  
      vpc_peering_connection_id = aws_vpc_peering_connection.this.id  
      
      provider = aws.service_provider  
    }

**3 —** Once the VPCs are created and the peering is established, you can
proceed and enable/create the PrivateLink setup between the Service Consumer
VPC and the Service Provider VPC:

    
    
    data "aws_caller_identity" "current" {}  
      
    resource "aws_lb" "nlb" {  
      name               = "service-provider-nlb"  
      internal           = true  
      load_balancer_type = "network"  
      subnets            = module.vpc_service_provider.private_subnets  
      
      enable_deletion_protection = false  
      
      provider = aws.service_provider_outpost  
    }  
      
    resource "aws_vpc_endpoint_service" "this" {  
      acceptance_required        = false  
      network_load_balancer_arns = [aws_lb.nlb.arn]  
      
      provider = aws.service_provider_outpost  
    }  
      
    resource "aws_vpc_endpoint_service_allowed_principal" "this" {  
      vpc_endpoint_service_id = aws_vpc_endpoint_service.this.id  
      principal_arn           = data.aws_caller_identity.current.arn  
      
      provider = aws.service_provider_outpost  
    }  
      
    resource "aws_vpc_endpoint" "this" {  
      service_name      = aws_vpc_endpoint_service.this.service_name  
      subnet_ids        = module.vpc_service_consumer.private_subnets  
      vpc_endpoint_type = "Interface"  
      vpc_id            = module.vpc_service_consumer.vpc_id  
      
      provider = aws.consumer  
    }

4 — Finally, deploy EC2 instances within the Service Provider VPCs, each
running a straightforward Flask API. Register these instances as targets in
the Network Load Balancer (NLB), [as elaborated in a prior article explaining
the intricacies of PrivateLink](https://awsmorocco.com/how-does-aws-
privatelink-works-faddc730ed73). Additionally, instantiate a public instance
within the Consumer VPC and attempt to access the service — specifically, the
Flask application — exposed by the deployed instances, following the
guidelines outlined in [the aforementioned
article](https://awsmorocco.com/how-does-aws-privatelink-works-faddc730ed73).

#### The Benefits of this setup:

  * **Security** : Traffic remains private within AWS’s private fiber network
  * **Scalability** : Connect VPCs across different AWS regions
  * **Agility** : Provide local access without immediate service deployment.

#### The Limitations to Consider:

  * **Latency** : Increased latency due to inter-region communication
  * **Costs** : Data transfer costs for inter-Region VPC peering

#### Conclusion

In conclusion, the implementation of Inter-Region VPC peering, coupled with
AWS PrivateLink, offers a robust and flexible solution for SaaS providers
expanding their services across diverse regions. This architectural approach
ensures secure and private connectivity within AWS’s infrastructure, allowing
for scalability and local access without immediate service deployment.

#### Read More:

  * [aws-morocco-samples/inter-region-privatelink at main · Z4ck404/aws-morocco-samples](https://github.com/Z4ck404/aws-morocco-samples/tree/main/inter-region-privatelink)
  * [Use-case examples](https://docs.aws.amazon.com/whitepapers/latest/aws-privatelink/use-case-examples.html#inter-region-endpoint-services)
  * [How Does AWS PrivateLink Works ?](https://awsmorocco.com/how-does-aws-privatelink-works-faddc730ed73)

![](/assets/images/medium/stat?event=post.clientViewed&referrerSource=full_rss&postId=337c5115fbb9)

* * *

[AWS Inter-Region PrivateLink using Terraform](https://awsmorocco.com/inter-
region-aws-privatelink-337c5115fbb9) was originally published in [AWS
Morocco](https://awsmorocco.com) on Medium, where people are continuing the
conversation by highlighting and responding to this story.

