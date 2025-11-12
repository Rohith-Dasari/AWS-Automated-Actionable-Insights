import boto3
from datetime import datetime, timedelta, timezone
from service_config import SERVICE_CONFIG
from botocore.exceptions import ClientError
import pandas as pd


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
    start = end - timedelta(days=30)

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


def generate_prompt(service, name, cost):
    config = get_resource_config(service, name)
    metrics = get_service_metrics(service, name)

    prompt = f"\nService: {service}\nResource: {name}\nCost Incurred:{cost}\n\nConfiguration:\n"
    for k, v in config.items():
        prompt += f"{k}: {v}\n"

    prompt += "\nMetrics:\n"
    for d in metrics:
        prompt += f"{d['Metric']}: {d['AverageValue']} ({d['Statistic']})\n"

    prompt += "\nBased on this data, suggest actions to optimize cost, performance, or configuration. No generic recomendations but based on analysis of given data."
    return prompt

if __name__=="__main__":
    resources=[("arn:aws:s3:::cost-and-usage-rep-s3",0.7)]
    s3=boto3.client('s3')
    bucket_name="cur-data-exports-1"
    object_key = "report1-00001.snappy (1).parquet"
    local_file="cur_report.parquet"
    cost_param="estimated_monthly_cost_after_discount"
    s3.download_file(bucket_name, object_key, local_file)
    df=pd.read_parquet(local_file)
    top5_df = (
    df.groupby("resource_arn", as_index=False)[cost_param]
      .sum()                         
      .sort_values(cost_param, ascending=False)  
      .head(5)                       
    )    

    for _, row in top5_df.iterrows():
        resource_arn=row["resource_arn"]
        service = resource_arn.split(':')[2]
        resource_name = resource_arn.split(':')[-1]
        resource_cost=row[cost_param]

        prompt = generate_prompt(service, resource_name, resource_cost)
        print(prompt)

        client = boto3.client("bedrock-runtime", region_name="us-east-1")
        model_id = "amazon.nova-lite-v1:0"
        conversation = [
            {
                "role": "user",
                "content": [{"text": prompt }],
            }
        ]

        try:
            response = client.converse(
                modelId=model_id,
                messages=conversation,
                inferenceConfig={"maxTokens": 400},
            )

            response_text = response["output"]["message"]["content"][0]["text"]
            print(response_text)

        except (ClientError, Exception) as e:
            print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
            exit(1)


