
---
title: "Lessons Learned From Mounting Secrets to Pods on Kubernetes"
image: "/images/image-placeholder.png"
categories: ["AWS", "Terraform"]
tags: ["AWS", "Terraform"]
date: 2024-02-29T14:48:02Z
author: "Unknown Author"
---

![](/assets/images/medium/1*2T2dFm4rt5B-R3hqUqmbZw.png)

Kubernetes secrets are objects conceived to hold sensitive information such as
passwords, tokens and certificates that can be used by pods without the need
to include this sensitive information in the application code or container
image. The pod can use these secrets in different ways, each of which is
different and each method is made for a particular case, and that’s what we’re
going to explore in the following article.

#### 1 — Mounting Secrets as environment variables:

When it comes to managing sensitive information in Kubernetes, a common
approach is to mount secrets as environment variables in pods. This provides a
simple way for applications running in the pod to access sensitive data
without exposing it directly in the container code or image.

    
    
    apiVersion: v1  
    kind: Pod  
    metadata:  
      name: mypod  
    spec:  
      containers:  
        - name: mycontainer  
          image: myimage  
          env:  
            - name: DATABASE_PASSWORD  
              valueFrom:  
                secretKeyRef:  
                  name: mydatabase-secret  
                  key: password

In this example, we’re mounting a the key password from a secret named
mydatabase-secret as an environment variable DATABASE_PASSWORD in the pod.

    
    
    apiVersion: v1  
    kind: Secret  
    metadata:  
      name: mydatabase-secret  
    type: Opaque  
    stringData:  
      username: username  
      password: password

#### Pros :

  * **Direct access:** This method allows pod applications to access sensitive information directly using environment variables.
  * **Easier implementation** : Many applications are designed to read configuration via environment variables, making it easier to integrate secrets into existing code.

#### Cons:

  * **Pod restart required for updates:** A significant downside is that changes to environment variables, including secret updates, require a restart of the pod to take effect. This can lead to downtime or service interruptions during the update process.
  * **Limited to key-value pairs** : Environment variables are generally used for simple key-value pairs. If your secret structure is more complex, this may not be the most appropriate approach.

#### 2 — Mounting Secrets as Volumes:

Another effective approach is to mount secrets as volumes. This method is
particularly useful in scenarios where the application requires access to
multiple files, where secrets are important, or where frequent updates of
secret values are required. The advantage is the ability to support dynamic
updates without the need to restart the pod, ensuring that the application
always has the latest version of the secret.

    
    
    apiVersion: v1  
    kind: Pod  
    metadata:  
      name: mypod  
    spec:  
      containers:  
        - name: mycontainer  
          image: myimage  
          volumeMounts:  
            - name: secret-volume  
              mountPath: /etc/secrets  
      volumes:  
        - name: secret-volume  
          secret:  
            secretName: mydatabase-secret

#### Pros:

  * **Dynamic Updates without Pod Restart:** Unlike environment variables, secrets mounted as volumes support dynamic updates without requiring a pod restart. The application can detect changes in the mounted files and use the updated data without downtime.
  * **Suitable for Multiple Files:** This method is well-suited for scenarios where secrets consist of multiple files or configurations. Each file can be mounted as a separate volume, providing flexibility.

#### Cons:

  * **Complex Integration for Some Applications:** Certain applications may require additional logic to detect and react to changes in mounted volumes. The complexity of handling multiple files might be a consideration.
  * **Potential for Increased Resource Usage:** Mounting secrets as volumes can potentially increase resource usage compared to environment variables, especially if the secrets are large.

#### 3 — Mounting Secrets as Volumes in Kubernetes: Understanding mountPath
and subPath:

    
    
    apiVersion: v1  
    kind: Pod  
    metadata:  
      name: mypod-mountpath  
    spec:  
      containers:  
        - name: mycontainer  
          image: myimage  
          volumeMounts:  
            - name: secret-volume  
              mountPath: /etc/secrets  
      volumes:  
        - name: secret-volume  
          secret:  
            secretName: mydatabase-secret

  * **MountPath:** refers to the base path within the container where the entire content of the secret is mounted. Any change to the secret is automatically reflected in the volume [**after a short delay (60–90 seconds)**](https://ahmet.im/blog/kubernetes-secret-volumes-delay/), and applications can access the updated information without requiring a pod restart.

    
    
    apiVersion: v1  
    kind: Pod  
    metadata:  
      name: mypod-subpath  
    spec:  
      containers:  
        - name: mycontainer  
          image: myimage  
          volumeMounts:  
            - name: secret-volume  
              mountPath: /etc/secrets/key  
              subPath: key  
      volumes:  
        - name: secret-volume  
          secret:  
            secretName: mydatabase-secret

  * **subPath:** allows you to mount only a specific key or file from the secret into a specified path within the container. Changes to the secret key do not automatically propagate to volumes using subPath until the pod is restarted ! Kubernetes updates the symlink for the volume mount point during secret updates but does not update the symlinks for files under the mount point created using subPath.

#### Conclusion:

Mounting secrets as volumes in Kubernetes is an effective solution for
scenarios where dynamic updates and access to multiple files are critical
requirements. When using the mount secrets as volumes approach, understanding
the difference between mountPath and subPath is essential for successful
secret management in Kubernetes.

Same Applies to configMaps as well.

  * [Configure a Pod to Use a ConfigMap](https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap/#mounted-configmaps-are-updated-automatically)
  * [Why Kubernetes secrets take so long to update?](https://ahmet.im/blog/kubernetes-secret-volumes-delay/)

![](/assets/images/medium/stat?event=post.clientViewed&referrerSource=full_rss&postId=ac0bbe8bd2ae)

* * *

[Lessons Learned From Mounting Secrets to Pods on
Kubernetes](https://awsmorocco.com/lessons-learned-from-mounting-secrets-to-
pods-on-kubernetes-ac0bbe8bd2ae) was originally published in [AWS
Morocco](https://awsmorocco.com) on Medium, where people are continuing the
conversation by highlighting and responding to this story.

