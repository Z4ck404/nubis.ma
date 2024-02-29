
---
title: "CSI Drivers (EBS, EFS, S3) on EKS And How To Use Them"
image: "/images/image-placeholder.png"
categories: ["AWS", "Terraform"]
tags: ["AWS", "Terraform"]
date: 2024-02-29T14:48:03Z
author: "Unknown Author"
---

![](/assets/images/medium/0*_WvCpAlKQZOfRg0m)Photo by [frank
mckenna](https://unsplash.com/@frankiefoto?utm_source=medium&utm_medium=referral)
on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)

Container Storage Interface (CSI) drivers play a crucial role in managing
persistent storage for containerized applications. When working with Amazon
Elastic Kubernetes Service (EKS), integrating CSI drivers becomes essential
for efficient storage management. In this guide, we will delve into the
details of CSI drivers on Amazon EKS and explore how to install and use them
seamlessly with file systems.

#### Understanding CSI Drivers:

![](/assets/images/medium/0*953JJ655M6dcjEQG.png)[Container Storage Interface
(CSI) for Kubernetes GA](https://kubernetes.io/blog/2019/01/15/container-
storage-interface-ga/)

CSI is a standardized interface that allows storage vendors to develop plugins
that can be used across various container orchestration platforms. With EKS,
these drivers help manage the lifecycle of storage resources, enabling dynamic
provisioning, attaching, and detaching volumes to and from pods

#### AWS EBS CSI Driver:

**1 — Overview:**  
The AWS EBS CSI Driver allows Kubernetes clusters to use Amazon Elastic Block
Store (EBS) volumes as persistent storage. It supports dynamic provisioning of
EBS volumes, attaching/detaching volumes to pods, and snapshot creation.

**2 — Installation:**

First Ensure that the necessary IAM roles and policies are in place to allow
EKS to interact with the storage service. This involves creating a role with
the appropriate permissions for your chosen driver as detailed in the [AWS
Docs.](https://docs.aws.amazon.com/eks/latest/userguide/ebs-csi.html)

To Deploy the EBS CSI Driver Utilize the provided Helm charts or YAML
manifests to deploy the CSI driver on your EKS cluster or You can install it
as an EKS Add-on and specify the IAM role you.

![](/assets/images/medium/0*Mj7tUcGmGUn93AN8.png)EBS CSI Driver add-on

Or you can use my Terraform Module to setup the appropriate policy, and roles
and install the add-on on the cluster.

[GitHub - Z4ck404/terraform-aws-eks-ebs-csi-driver: A terraform module install
ebs csi driver on an eks cluster](https://github.com/Z4ck404/terraform-aws-
eks-ebs-csi-driver)

    
    
    module "eks-ebs-csi-driver" {  
      source           = "Z4ck404/eks-ebs-csi-driver/aws"  
      version          = "0.1.0"  
      
      aws_profile      = "zack-aws-profile"  
      aws_region       = "us-west-1"  
      eks_cluster_name = "zack-eks"  
    }

**3 — Usage:**

Create a storage class that provisions volumes using the EBS driver, then
define a PVC to be used by your workloads.

    
    
    kind: StorageClass  
    apiVersion: storage.k8s.io/v1  
    metadata:  
     name: ebs-sc  
    provisioner: ebs.csi.aws.com  
    --  
    kind: PersistentVolumeClaim  
    apiVersion: v1  
    metadata:  
     name: ebs-pvc  
     spec:  
    storageClassName: ebs-sc  
     accessModes:  
       - ReadWriteOnce  
     resources:  
       requests:  
         storage: 5Gi

#### Amazon EFS CSI Driver

**1 — Overview:**

Enables the use of Amazon Elastic File System (EFS) as a persistent storage
solution for Kubernetes pods. It allows Dynamic provisioning of EFS
filesystems, mount targets per pod, and support for ReadWriteMany access mode.

**2 — Installation:**  
Same as the EBS CSI Driver you will need to setup IAM resources, then install
the driver using helm charts, yaml manifests, or as an EKS Add-on as explained
in the AWS Docs.

**3 — Usage:**

Create a storage class that provisions volumes using the efs driver, then
define a PVC to be used by your workloads.

    
    
    kind: StorageClass  
    apiVersion: storage.k8s.io/v1  
    metadata:  
      name: efs-sc  
    provisioner: efs.csi.aws.com  
    --  
    kind: PersistentVolumeClaim  
    apiVersion: v1  
    metadata:  
      name: efs-pvc  
    spec:  
      storageClassName: efs-sc  
      accessModes:  
        - ReadWriteMany  
      resources:  
        requests:  
          storage: 5Gi

#### S3 CSI Driver (mounting S3 as a filesystem):

**1 — Overview:**  
The S3 CSI Driver allows Kubernetes pods to use Amazon S3 buckets as if they
were mounted file systems. It enables transparent access to S3 data, and
supports for ReadWriteOnce access mode.

**2 — Installation:**

Same as the EBS CSI Driver you will need to setup IAM resources, then install
the driver using helm charts, yaml manifests or as an EKS Add-on as explained
in the [AWS
Docs](https://docs.aws.amazon.com/eks/latest/userguide/s3-csi.html).

Or you can use my Terraform Module to setup the appropriate policy, and role
and install the add-on on your cluster.

[GitHub - Z4ck404/terraform-aws-eks-s3-csi-driver: A terraform module install
s3 csi driver on an eks cluster and mount s3 as
volume](https://github.com/Z4ck404/terraform-aws-eks-s3-csi-driver)

    
    
    module "eks-s3-csi-driver" {  
      source  = "Z4ck404/eks-s3-csi-driver/aws"  
      
      aws_profile      = "zack-labs"  
      aws_region       = "us-west-2"  
      eks_cluster_name = "zack-demo-0"  
      
      s3_bucket_name = "zack-s3-mount--usw2-az1--x-s3"  
    }

**3 — Usage:**

You can have a look into the examples in the official repository of the
[mountpoint-s3-csi-driver](https://github.com/awslabs/mountpoint-s3-csi-
driver). Static provisioning can be achieved as follows:

    
    
    apiVersion: v1  
    kind: PersistentVolume  
    metadata:  
      name: s3-pv  
    spec:  
      capacity:  
        storage: 1200Gi # ignored, required  
      accessModes:  
        - ReadWriteMany # supported options: ReadWriteMany / ReadOnlyMany  
      mountOptions:  
        - allow-delete  
        - region us-west-2  
      csi:  
        driver: s3.csi.aws.com # required  
        volumeHandle: s3-csi-driver-volume  
        volumeAttributes:  
          bucketName: s3-csi-driver  
    ---  
    apiVersion: v1  
    kind: PersistentVolumeClaim  
    metadata:  
      name: s3-claim  
    spec:  
      accessModes:  
        - ReadWriteMany # supported options: ReadWriteMany / ReadOnlyMany  
      storageClassName: "" # required for static provisioning  
      resources:  
        requests:  
          storage: 1200Gi # ignored, required  
      volumeName: s3-pv  
    ---  
    apiVersion: v1  
    kind: Pod  
    metadata:  
      name: s3-app  
    spec:  
      containers:  
        - name: app  
          image: centos  
          command: ["/bin/sh"]  
          args: ["-c", "echo 'Hello from the container!' >> /data/$(date -u).txt; tail -f /dev/null"]  
          volumeMounts:  
            - name: persistent-storage  
              mountPath: /data  
      volumes:  
        - name: persistent-storage  
          persistentVolumeClaim:  
            claimName: s3-claim

#### Conclusion:

These examples offer a basis for integrating and using different CSI drivers
on Amazon EKS, addressing different storage needs, from block storage with EBS
to file storage with EFS and even object storage with S3. There is also an
Amazon FSx for Lustre CSI driver for FSx for Lustre.  
Third-party CSI drivers exist to support other file systems available on AWS
such as [NetApp Trident](https://docs.netapp.com/fr-fr/trident-2107/trident-
concepts/intro.html) which allow [FSxONTAP
](https://aws.amazon.com/fsx/netapp-ontap/)to be used.

![](/assets/images/medium/stat?event=post.clientViewed&referrerSource=full_rss&postId=0aa369ec1c03)

* * *

[CSI Drivers (EBS, EFS, S3) on EKS And How To Use
Them](https://awsmorocco.com/csi-drivers-ebs-efs-s3-on-eks-and-how-to-use-
them-0aa369ec1c03) was originally published in [AWS
Morocco](https://awsmorocco.com) on Medium, where people are continuing the
conversation by highlighting and responding to this story.

