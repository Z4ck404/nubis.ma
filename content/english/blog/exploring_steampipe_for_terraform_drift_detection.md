
---
title: "Exploring Steampipe for Terraform Drift Detection"
image: "/images/medium/1*4Ki5MyUXEDKNTt0p-v37zQ.png"
categories: ["AWS", "Terraform"]
tags: ["AWS", "Terraform","steampipe"]
date: 2024-02-29T14:48:09Z
author: "awsmorocco"
---

In Terraform, drift detection helps spot any mismatches between the
infrastructure you’ve outlined in your code and what’s actually out there
running in your cloud accounts. This is super important for keeping your
Infrastructure as Code (IaC) practices on point, making sure everything is
consistent, efficient, and secure. [Steampipe, which is an open-source
tool](https://medium.com/aws-morocco/get-to-know-steampipe-a-new-way-to-talk-to-aws-e946708017b4), takes this a step further by letting you run real-time
SQL queries on your infrastructure data. When you bring Steampipe into the
mix, you get a clearer picture and more control over your setup, making it
easier to keep your code and infrastructure in sync and strengthening your IaC
game.

#### Understanding drift in Terraform


Drift is essentially the divergence between the state of your infrastructure
as described in your code and its actual, real-world condition.

This can happen for a variety of reasons:

  * Sometimes, someone might go in and manually tweak a setting on a server, bypassing the code entirely.
  * Other times, changes might be made using tools other than Terraform, creating a mismatch.
  * And then there are cases where the Terraform state file itself doesn’t accurately reflect what’s really going on with your infrastructure.

When drift goes unnoticed, it can lead to a host of problems. You might think
you’re deploying to an environment that’s configured one way, when it’s
actually set up differently. This can result in failed deployments, security
vulnerabilities, or even downtime, making it crucial to catch and address
drift as quickly as possible.

### Setting Up Steampipe for Drift Detection

![](/assets/images/medium/0*qyBFesXGflSZrusH.png)<https://hub.steampipe.io/>

#### **Installation**

The installation of Steampipe and the setup and usage of the AWS plugin have
been covered in a previous article. You can refer to [this
article](https://awsmorocco.com/get-to-know-steampipe-a-new-way-to-talk-to-aws-e946708017b4) for a detailed step-by-step guide on the same.

[Get to know Steampipe: A New Way to Talk to AWS!](https://awsmorocco.com/get-to-know-steampipe-a-new-way-to-talk-to-aws-e946708017b4)

#### Configuration

  * Install the [Steampipe Terraform plugin](https://hub.steampipe.io/plugins/turbot/terraform):
    
    ```cmd
    steampipe plugin install terraform
    ```

  * Once the terraform plugin is installed it should create a config file ~/.steampipe/config/aws.spc open the file and configure your terraform connection where you specify the state file(s) path(s). The state files can be in local or in remote back-end like s3:

    ```cmd
    connection "terraform" {  
      plugin = "terraform"  
      
      # configuration_file_paths = [  
      #  "github.com/Z4ck404/aws-morocco-samples//getting-started-with-tf-on-aws",  
      # ]  
        
      state_file_paths = [  
        "s3::https://awsmorocco-terraform-states.s3.us-east-1.amazonaws.com/awsmorcco/network",  
      ]  
    }
    ```

#### Querying Infrastructure

  * Extract data for the desired resource from the Terraform state and save the output:

    
    ```cmd
    steampipe query "  
    SELECT  
      attributes_std ->> 'id' AS vpc_id,  
      attributes_std ->> 'arn' AS arn,  
      attributes_std ->> 'cidr_block' AS cidr_block,  
      attributes_std ->> 'dhcp_options_id' AS dhcp_options_id,  
      attributes_std ->> 'instance_tenancy' AS instance_tenancy,  
      attributes_std ->> 'owner_id' AS owner_id,  
      attributes_std ->> 'tags' AS tags  
    FROM  
      terraform_resource  
    WHERE  
      type = 'aws_vpc';" --output csv > tf_output.csv
    
    ```
    * Extract cloud resources metadata:
    ```cmd
      steampipe query "  
      SELECT  
        vpc_id,  
        arn,  
        cidr_block,  
        dhcp_options_id,  
        instance_tenancy,  
        owner_id,  
        tags  
      FROM  
        aws_morocco.aws_vpc  
      WHERE is_default = false;" --output csv > aws_output.csv
    
    ```

  * Compare the saved outputs :
    
    ```cmd
    diff -i -w aws_output.csv tf_output.csv
    ```

  * You can automate everything in one script (here in bash):

    
  ```bash
    #!/bin/bash  
      
    # 1. Fetch data from AWS plugin  
    steampipe query "  
    SELECT  
      vpc_id,  
      arn,  
      cidr_block,  
      dhcp_options_id,  
      instance_tenancy,  
      owner_id,  
      tags  
    FROM  
      aws_morocco.aws_vpc  
    WHERE is_default = false;" --output csv > aws_output.csv  
 
    steampipe query "  
    SELECT  
      attributes_std ->> 'id' AS vpc_id,  
      attributes_std ->> 'arn' AS arn,  
      attributes_std ->> 'cidr_block' AS cidr_block,  
      attributes_std ->> 'dhcp_options_id' AS dhcp_options_id,  
      attributes_std ->> 'instance_tenancy' AS instance_tenancy,  
      attributes_std ->> 'owner_id' AS owner_id,  
      attributes_std ->> 'tags' AS tags  
    FROM  
      terraform_resource  
    WHERE  
      type = 'aws_vpc';" --output csv > tf_output.csv  
  
  ```
  ```bash 
    # 3. Compare the two CSV files using diff  
    diff -i -w aws_output.csv tf_output.csv > differences.txt  
      
    # 4. Check if there are differences  
    if [ -s differences.txt ]; then  
        echo "Differences found! Check the differences.txt file."  
    else  
        echo "No differences found!"  
        rm differences.txt  
    fi  
  ```
  ```bash    
    # Clean up  
    rm aws_output.csv tf_output.csv  
  ```

This approach essentially compares the Terraform state files with the actual
cloud resources, eliminating the need for manual Terraform plans or resource
inspections. Tools like [Driftctl](https://docs.driftctl.com/0.39.0) employ a
similar strategy (**note** : Driftctl entered maintenance mode in June 2023).

#### Limitations:

  * Extensive SQL queries: For each resource, you must create and update SQL queries.
  * Dependency on Steampipe’s functionality and tables, especially for Terraform and cloud plugins.

A potential roadmap could involve developing a CLI wrapper for Steampipe. This
would shoulder the responsibility of generating and updating SQL queries,
further extending support to a broader range of resources, cloud providers,
and SaaS platforms, akin to Driftctl’s initial objectives.

[aws-morocco-samples/setting-steampipe-for-drift-detection at main ·
Z4ck404/aws-morocco-samples](https://github.com/Z4ck404/aws-morocco-samples/tree/main/setting-steampipe-for-drift-detection)


* * *

[Exploring Steampipe for Terraform Drift
Detection](https://awsmorocco.com/exploring-steampipe-for-terraform-drift-detection-4cc4536f6cb5) was originally published in [AWS
Morocco](https://awsmorocco.com) on Medium, where people are continuing the
conversation by highlighting and responding to this story.

