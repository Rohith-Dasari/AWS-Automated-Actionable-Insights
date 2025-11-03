import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta, timezone

cloudwatch=boto3.client('cloudwatch')

resource_arn="arn:aws:lambda:ap-south-1:961341531249:function:sam-app-HelloWorldFunction-JUnbZN1kVzIt"
resource_name=resource_arn.split(':')[-1]
service=resource_arn.split(':')[2]
name_space="AWS/"+service.title()
end = datetime.now(timezone.utc)
start = end - timedelta(days=30)
aws_resource_instance=boto3.client(service)

if service=="lambda":
    metrics_to_fetch=[
        ("Invocations","Sum"),
        ("Duration","Average"),
        ("Errors","Sum"),
        ("Throttles", "Sum"),
        ("ConcurrentExecution","Maximum")
    ]
    name='FunctionName'
    details=aws_resource_instance.get_function(FunctionName=resource_name)
    keys=['Runtime','Timeout', 'EphemeralStorage', 'MemorySize', 'Description', 'CodeSize', 'Handler']
    configuration='Configuration'

data=[]

for metric_name, stat in metrics_to_fetch:
    response=cloudwatch.get_metric_statistics(
        Namespace=service,
        MetricName=metric_name,
        Dimensions=[
            {
                'Name':name,
                'Value':resource_name
            }
        ],
        StartTime=start,
        EndTime=end,
        Period=3600,
        Statistics=[stat]
    )

    datapoints=response['Datapoints']
    if datapoints:
        avg_value=sum(dp[stat] for dp in datapoints)/len(datapoints)
    else:
        avg_value=0
    data.append({
        "Metric":metric_name,
        "Statistic":stat,
        "AverageValue":round(avg_value,2)
    })


print("results:")
print("Service: ", service)

prompt=""
for k in keys:
    value = details[configuration].get(k)
    prompt += f"{k}:{value}\n" 

for d in data:
    prompt+=f"{d['Metric']}: {d['AverageValue']}  {d['Statistic']}\n"

prompt="Base on the following service data, suggest me what actions can be perfomed to optimise cost, performance, configuration or any other useful insights?"+prompt
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


