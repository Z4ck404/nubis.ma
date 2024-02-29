
---
title: "Monitoring Kubernetes with Prometheus and Alertmanager: Setting Up Alerts with Slack Integration"
image: "/images/image-placeholder.png"
categories: ["AWS", "Terraform"]
tags: ["AWS", "Terraform"]
date: 2024-02-29T14:47:59Z
author: "Unknown Author"
---

![](/assets/images/medium/0*KAcI4WGbxyNHP0o5)Photo by
[Sigmund](https://unsplash.com/@sigmund?utm_source=medium&utm_medium=referral)
on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)

In this tutorial, we will learn how to set up Prometheus rules and configure
Alertmanager to send alerts to a Slack channel. Prometheus is a popular
monitoring and alerting solution in the Kubernetes ecosystem, while
Alertmanager handles alert management and routing. By integrating with Slack,
you can receive real-time notifications for any issues or anomalies in your
Kubernetes cluster. **Let’s get started 👨🏻‍💻!**

#### **Table of Contents:**

  1. Prerequisites
  2. Setting Up Prometheus Rules
  3. Configuring Alertmanager
  4. Integrating with Slack
  5. Testing the Setup
  6. Conclusion

#### 🚦Prerequisites:

  * Access to a Kubernetes cluster
  * Prometheus and Alertmanager installed in the cluster
  * Basic knowledge of Kubernetes and YAML syntax

#### **1 — Setting Up Prometheus Rules** :

Prometheus rules define conditions for generating alerts based on metrics
collected by Prometheus. In this example, we will create a PrometheusRule
resource named **z4ck404-alerts** in the **monitoring** namespace.

    
    
    apiVersion: monitoring.coreos.com/v1  
    kind: PrometheusRule  
    metadata:  
      name: z4ck404-alerts  
      namespace: monitoring  
    spec:  
      groups:  
      - name: blackbox.alerts  
        rules:  
        - alert: backbox probe check failed!   
          expr: |  
            probe_success != 1  
          for: 2m  
          labels:  
            severity: warning  
            namespace: monitoring  
          annotations:  
            summary:  BlackBox prob check failed. Service might be down  
            description: 'Target {{`{{`}} printf "%v" $labels.target {{`}}`}} probe is down.'

Explanation of the provided example YAML:

  * The “apiVersion” and “kind” specify the PrometheusRule resource.
  * Under “metadata,” we set the name and namespace for the rule.
  * The “spec” section contains the rule groups, each with a name and a list of rules.
  * In this example, we define a rule named **blackbox.alerts** with an expression that checks if **probe_success** is not equal to 1.
  * We set the alert duration (**for**) to 2 minutes and define labels and annotations for the alert.

#### 2 — Configuring Alertmanager:

Alertmanager handles the routing and sending of alerts to different receivers.
In this step, we will create an AlertmanagerConfig resource to configure
Alertmanager.

    
    
    apiVersion: monitoring.coreos.com/v1alpha1  
    kind: AlertmanagerConfig  
    metadata:  
      name: z4ck404-alertmanagerconfig  
    spec:  
      route:  
        groupBy: ['alertname', 'job']  
        groupWait: 10s  
        groupInterval: 5m  
        repeatInterval: 12h  
        continue: true  
        matchers:  
          - name: severity  
            matchType: "="  
            value: "warning"  
        receiver: slack  
      receivers:  
        - name: slack  
          slackConfigs:  
            - channel: "#alerts"  
              apiURL:  
                key: slack_webhook  
                name: alertmanager-slack-notification  
              sendResolved: true  
              title: >-  
                {{`{{`}} if eq .Status "firing" {{`}}`}}:fire: *FIRING* {{`{{`}} else {{`}}`}}:ok_hand: *RESOLVED* {{`{{`}} end {{`}}`}}  
              text: >-  
                {{`{{`}} range .Alerts {{`}}`}}  
                    {{`{{`}} if .Annotations.summary {{`}}`}}*Alert:* {{`{{`}} .Annotations.summary {{`}}`}} - `{{`{{`}} .Labels.severity {{`}}`}}`{{`{{`}} end {{`}}`}}  
                    {{`{{`}} if .Annotations.description {{`}}`}}*Description:* {{`{{`}} .Annotations.description {{`}}`}}{{`{{`}} end {{`}}`}}  
                    *Details:*  
                    {{`{{`}} range .Labels.SortedPairs {{`}}`}} • *{{`{{`}} .Name {{`}}`}}:* `{{`{{`}} .Value {{`}}`}}`  
                    {{`{{`}} end {{`}}`}}  
                {{`{{`}} end {{`}}`}}  
              footer: "z4ck404-alertmanager"

Explanation of the provided example YAML:

  * The “apiVersion” and “kind” specify the AlertmanagerConfig resource.
  * Under “metadata,” we set the name for the config.
  * In the “spec” section, we define the routing rules for alerts.
  * The “groupBy” field determines how alerts are grouped in notifications.
  * We set “groupWait,” “groupInterval,” and “repeatInterval” for timing-related configurations.
  * The “matchers” section filters alerts based on label values.
  * The “receiver” field specifies the receiver to use for matched alerts.
  * Under “receivers,” we define a receiver named “slack” with Slack-specific configurations.

#### 3 — Integrating with Slack:

To receive alerts in a Slack channel, we need to configure Alertmanager with
the appropriate Slack webhook URL. We’ll create a Secret resource to store the
webhook URL securely.

    
    
    apiVersion: v1  
    kind: Secret  
    metadata:  
      name: alertmanager-slack-notification  
    type: Opaque  
    data:  
      slack_webhook: "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"

Explanation of the provided example YAML:

  * The “apiVersion” and “kind” specify the Secret resource.
  * Under “metadata,” we set the name and type for the secret.
  * In the “data” section, we encode the Slack webhook URL using Base64 encoding.

#### 4 — Testing the Setup:

After applying the YAML manifests to the Kubernetes cluster, we can test the
setup by triggering an alert condition. For example, if the “probe_success”
metric is not equal to 1, an alert will be generated. Alertmanager will route
the alert to the Slack channel configured in the receiver.

#### Conclusion:

In this tutorial, we covered the process of setting up Prometheus rules and
configuring Alertmanager to send alerts to a Slack channel. By leveraging
these tools, you can ensure timely notifications for any critical issues in
your Kubernetes cluster.

[GitHub - Z4ck404/prometheus-alertmanager-k8s: Examples for setting up
monitoring and alerting using Prometheus and
Alertmanager.](https://github.com/Z4ck404/prometheus-alertmanager-k8s)

![](/assets/images/medium/stat?event=post.clientViewed&referrerSource=full_rss&postId=b6e6413b1120)

* * *

[Monitoring Kubernetes with Prometheus and Alertmanager: Setting Up Alerts
with Slack Integration](https://awsmorocco.com/monitoring-kubernetes-with-
prometheus-and-alertmanager-setting-up-alerts-with-slack-
integration-b6e6413b1120) was originally published in [AWS
Morocco](https://awsmorocco.com) on Medium, where people are continuing the
conversation by highlighting and responding to this story.

