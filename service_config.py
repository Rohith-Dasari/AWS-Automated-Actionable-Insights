SERVICE_CONFIG = {
    "lambda": {
        "namespace": "AWS/Lambda",
        "metrics": [
            ("Invocations", "Sum"),
            ("Duration", "Average"),
            ("Errors", "Sum"),
            ("Throttles", "Sum"),
            ("ConcurrentExecutions", "Maximum")
        ],
        "describe": {
            "method": "get_function",
            "param": "FunctionName",
            "config_key": "Configuration",
            "keys": ["Runtime", "Timeout", "MemorySize", "CodeSize", "Handler"]
        }
    },
    "dynamodb": {
        "namespace": "AWS/DynamoDB",
        "metrics": [
            ("ConsumedReadCapacityUnits", "Sum"),
            ("ConsumedWriteCapacityUnits", "Sum"),
            ("ProvisionedReadCapacityUnits", "Sum"),
            ("ProvisionedWriteCapacityUnits", "Sum"),
            ("ThrottledRequests", "Sum")
        ],
        "describe": {
            "method": "describe_table",
            "param": "TableName",
            "config_key": "Table",
            "keys": ["TableStatus", "BillingModeSummary", "ItemCount", "TableSizeBytes"]
        }
    },
    "rds": {
        "namespace": "AWS/RDS",
        "metrics": [
            ("CPUUtilization", "Average"),
            ("DatabaseConnections", "Average"),
            ("FreeableMemory", "Average"),
            ("FreeStorageSpace", "Minimum"),
            ("ReadIOPS", "Sum"),
            ("WriteIOPS", "Sum"),
            ("ReadLatency", "Average"),
            ("WriteLatency", "Average")
        ],
        "describe": {
            "method": "describe_db_instances",
            "param": "DBInstanceIdentifier",
            "config_key": "DBInstances",
            "keys": [
                "DBInstanceClass",
                "Engine",
                "EngineVersion",
                "AllocatedStorage",
                "StorageType",
                "MultiAZ",
                "BackupRetentionPeriod",
                "StorageEncrypted",
                "PubliclyAccessible"
            ]
        }
    },
    "s3": {
        "namespace": "AWS/S3",
        "metrics": [
            ("BucketSizeBytes", "Average"),
            ("NumberOfObjects", "Average"),
            ("AllRequests", "Sum"),
            ("GetRequests", "Sum"),
            ("PutRequests", "Sum"),
            ("4xxErrors", "Sum"),
            ("5xxErrors", "Sum")
        ],
        "describe": {
            "method": "get_bucket_location",
            "param": "Bucket",
            "config_key": None,
            "keys": ["LocationConstraint"]
        }
    },
    "ebs": {
        "namespace": "AWS/EBS",
        "metrics": [
            ("VolumeReadOps", "Sum"),
            ("VolumeWriteOps", "Sum"),
            ("VolumeReadBytes", "Sum"),
            ("VolumeWriteBytes", "Sum"),
            ("BurstBalance", "Average"),
            ("VolumeIdleTime", "Average")
        ],
        "describe": {
            "method": "describe_volumes",
            "param": "VolumeIds",
            "config_key": "Volumes",
            "keys": [
                "VolumeId",
                "Size",
                "VolumeType",
                "State",
                "Encrypted",
                "SnapshotId",
                "AvailabilityZone"
            ]
        }
    },

    "ecs": {
        "namespace": "AWS/ECS",
        "metrics": [
            ("CPUUtilization", "Average"),
            ("MemoryUtilization", "Average"),
            ("NetworkRxBytes", "Sum"),
            ("NetworkTxBytes", "Sum"),
            ("StorageReadBytes", "Sum"),
            ("StorageWriteBytes", "Sum")
        ],
        "describe": {
            "method": "describe_clusters",
            "param": "clusters",
            "config_key": "clusters",
            "keys": [
                "clusterName",
                "status",
                "runningTasksCount",
                "pendingTasksCount",
                "activeServicesCount",
                "registeredContainerInstancesCount"
            ]
        }
    }
}

