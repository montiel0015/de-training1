# Project information

project_name = "data-castle-bravo"

region = "us-central1"

zone = "us-central1-a"

location = "US"

# Buckets names

input_bucket_name = "wize-datasets"

staging_prefix = "de-training-staging"

bucket_output_name_prefix = "de-training-output-bucket"

#Cluster information

zeppelin_sh_path = "gs://dcb-initialization-actions/zeppelin.sh"

cluster_prefix = "de-training"

machine_type = "n1-standard-1"

cluster_master_num_local_ssds = 0

cluster_worker_num_local_ssds = 0

cluster_init_timeout = 500

cluster_master_instances = 1

cluster_worker_instances = 2

cluster_master_boot_disk_size = 15

cluster_worker_boot_disk_size = 10

# Number of users
num_users = 2

# Service Accounts list
# The number of accounts should match with the number of users
user_members = [
    "rincondonovan@gmail.com", //This is an example, update with the users gmail accounts. index 0 goes to bucket 0
    "dm9450@gmail.com",
    ]