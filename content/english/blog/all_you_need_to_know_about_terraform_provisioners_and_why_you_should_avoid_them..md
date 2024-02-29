
---
title: "All you need to know about Terraform provisioners and why you should avoid them."
image: "/images/image-placeholder.png"
categories: ["AWS", "Terraform"]
tags: ["AWS", "Terraform"]
date: 2024-02-29T14:16:32Z
author: "Unknown Author"
---

![](/assets/images/medium/0*9Min-Ja3wAmWHp3l)Photo by [Danist
Soh](https://unsplash.com/@danist07?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText)
on
[Unsplash](https://unsplash.com/s/photos/infrastructure?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText)

As defined in the Terraform documentation,
[provisioners](https://www.terraform.io/language/resources/provisioners/syntax)
can be used to model specific actions on the local machine running the
Terraform Core or on a remote machine to prepare servers or other
infrastructure objects. But HashiCorp clearly states in its documentation that
they should be used as the last solution ! which I will explain in this
article.

Provisioners are the feature to use when what’s needed is not clearly
addressed by Terraform. You can copy data with to the newly created resources,
run scripts or specific tasks like installing or upgrading modules.

There are 3 types of provisioners :

#### File Provisioner :

Used to copy files or directories to the newly created resources and
underneath it’s using ssh or winrm. Does the job of an scp.

In this [article](https://awstip.com/i-deployed-my-static-website-with-
kubernetes-on-azure-using-terraform-because-why-not-2cdfe8807ca4) I used this
provisioner inside a null resource to copy my kubernetes configuration files
to a newly created VM where I installed minikube. You can define it inside the
vm resources as well but i prefer to use them in a separate module as they
shouldn't be mixed with the resources objects. And this is how I did it :

<https://medium.com/media/bcf1a10ce5b77ae8377ca50bc4b9ef39/href>

**Note that** you will need to add the ssh connection details since it’s using
it behind the scenes.

#### remote-exec Provisioner:

This provisioner invokes a script on the newly created resource. it’s similar
to connecting to the resource and running a bash or a command in the terminal.

It can be used inside the Terraform resource object and in that case it will
be invoked once the resource is created, or it can be used inside a null
resource which is my prefered approche as it separates this non terraform
behavior from the real terraform behavior.

<https://medium.com/media/47dd8e18232805592d498c79e67bc679/href>

> **Note that** you can not pass any arguments to the script or command, so
> the best way is to use file provisioner to copy the files to the resources
> and then invoke them with the remote-exec provisioner like I did above for
> my script that installs minikube on the azure-vm.

> **An other thing** to pay attention to is that by default, provisioners that
> fail will also cause the Terraform apply to fail. To avoid that, the
> [**on_failure**](https://www.terraform.io/language/resources/provisioners/syntax#failure-
> behavior)**** can be used.

<https://medium.com/media/6417741b0dd6ce5a5b53a58fab23d042/href>

In this example, I am using **inline** which is a series of command, the
on_failure will apply only to the final command in the list !

#### local-exec Provisioner:

Technically this one is very similar to the one before in terms of behavior or
use but it works in the local machine ruining Terraform. It invokes a script
or a command on local once the resource it’s declared in is created.

<https://medium.com/media/920825d50aded45dfa78ba7fbe9efccb/href>

It’s the only provisioner that doesn’t need any ssh or winrm connection
details as it runs locally.

#### Why you should avoid provisioner or use them only as a last resort ?

First, Terraform cannot model the actions of provisioners as part of a plan,
as they can in principle take any action (the possible commands is
“limitless”) which means you won’t get anything about the provisioners in your
tfstate. Even if you have them in null resources like I did.

Second, as you I mentioned above file and remote-exec provisioners require
connection credentials to function and that adds unnecessary complexity to the
Terraform configuration (Mixing day 1 and day 2 tasks).

So as HashiCorp recommends in the docs try using other techniques first, and
use provisioners only if there is no other option but you should know them
especially if you are planning to pass the [Terraform certification
exam](https://www.hashicorp.com/certification/terraform-associate).

[HashiCorp Certified: Terraform Associate was issued by HashiCorp to Zakaria
EL BAZI.](https://www.credly.com/badges/34394920-8cdf-47f8-a190-52ab447e3e0f)

![](/assets/images/medium/stat?event=post.clientViewed&referrerSource=full_rss&postId=22b5ef8d2db2)

* * *

[All you need to know about Terraform provisioners and why you should avoid
them.](https://awsmorocco.com/all-you-need-to-know-about-terraform-
provisioners-and-why-you-should-avoid-them-22b5ef8d2db2) was originally
published in [AWS Morocco](https://awsmorocco.com) on Medium, where people are
continuing the conversation by highlighting and responding to this story.

