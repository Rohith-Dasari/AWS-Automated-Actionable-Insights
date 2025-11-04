import boto3
from datetime import datetime, timedelta, timezone
from service_config import SERVICE_CONFIG


def get_resource_client(service):
    return boto3.client(service)

def get_resource_config(service, name):
    info = SERVICE_CONFIG.get(service)
    if not info:
        return {}

    client = get_resource_client(service)
    desc = info['describe']

    try:
        response = getattr(client, desc['method'])(**{desc['param']: name})
        details = response.get(desc['config_key'], {})
        return {k: details.get(k) for k in desc['keys']}
    except Exception as e:
        print(f"Error getting config for {service}: {e}")
        return {}

def get_service_metrics(service, name):
    info = SERVICE_CONFIG.get(service)
    if not info:
        return []
    
    cloudwatch = boto3.client('cloudwatch')
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=7)

    metrics_to_fetch = info["metrics"]
    data = []

    for metric_name, stat in metrics_to_fetch:
        response = cloudwatch.get_metric_statistics(
            Namespace=info["namespace"],
            MetricName=metric_name,
            Dimensions=[{'Name': info["describe"]["param"].replace("Name", ""), 'Value': name}],
            StartTime=start,
            EndTime=end,
            Period=3600,
            Statistics=[stat]
        )

        datapoints = response["Datapoints"]
        avg_value = sum(dp[stat] for dp in datapoints) / len(datapoints) if datapoints else 0
        data.append({"Metric": metric_name, "Statistic": stat, "AverageValue": round(avg_value, 2)})

    return data


def generate_prompt(service, name):
    config = get_resource_config(service, name)
    metrics = get_service_metrics(service, name)

    prompt = f"\nService: {service}\nResource: {name}\n\nConfiguration:\n"
    for k, v in config.items():
        prompt += f"{k}: {v}\n"

    prompt += "\nMetrics:\n"
    for d in metrics:
        prompt += f"{d['Metric']}: {d['AverageValue']} ({d['Statistic']})\n"

    prompt += "\nBased on this data, suggest actions to optimize cost, performance, or configuration."
    return prompt

resource_arn = "arn:aws:lambda:ap-south-1:961341531249:function:sam-app-HelloWorldFunction-JUnbZN1kVzIt"
service = resource_arn.split(':')[2]
resource_name = resource_arn.split('/')[-1]

prompt = generate_prompt(service, resource_name)
print(prompt)

# client = boto3.client("bedrock-runtime", region_name="us-east-1")
# model_id = "amazon.nova-lite-v1:0"
# conversation = [
#     {
#         "role": "user",
#         "content": [{"text": prompt }],
#     }
# ]

# try:
#     response = client.converse(
#         modelId=model_id,
#         messages=conversation,
#         inferenceConfig={"maxTokens": 400},
#     )

#     response_text = response["output"]["message"]["content"][0]["text"]
#     print(response_text)

# except (ClientError, Exception) as e:
#     print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
#     exit(1)


