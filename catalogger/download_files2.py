"""
This file works to download s3 files under the old system of sending the auto curation parameters which has now been set as the default
If the recordings were uploaded as of 07/25/2025 then use download_files2.py
"""

import boto3
import os
from botocore.client import Config

def download_s3_files(endpoint_url, bucket_name, uuids, local_directory):
    # Initialize the S3 client with the custom endpoint
    s3 = boto3.client('s3', endpoint_url=endpoint_url, config=Config(signature_version='s3v4'))

    #assert that the local directory exists
    assert os.path.exists(local_directory), f"Local directory {local_directory} does not exist!"

    try:
        for uuid in uuids:
            # Construct the prefix for this UUID
            prefix = f"ephys/{uuid}/derived/kilosort2"

            # List objects with this prefix
            response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

            # Download each matching object that ends with _acqm.zip
            for obj in response.get('Contents', []):
                file_key = obj['Key']
                
                # Only download files ending with _acqm.zip
                if file_key.endswith('_acqm.zip'):
                    local_file_path = os.path.join(local_directory, uuid, os.path.relpath(file_key, prefix))

                    # Ensure the subdirectory exists
                    os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

                    # Download the file
                    print(f"Downloading {file_key} to {local_file_path}")
                    s3.download_file(bucket_name, file_key, local_file_path)

        print("Download complete!")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Example usage
endpoint_url = 'https://s3-west.nrp-nautilus.io'
bucket_name = 'braingeneers'
# uuids = [
#     "2024-05-04-e-sakura-day22and24",
#     "2024-05-04-e-sakura-day22and24_dorothy",
#     "2024-05-10-e-all_cell_lines_dorsal_pasca", #sent job for new SNR params    # Downloaded
#     "2024-05-17-e-all_cell_lines_dorsal_pasca",
#     "2024-05-21-e-all_cell_lines_dorsal_pasca", #sent job for new SNR params    # Downloaded some 
#     "2024-05-07-e-c57bl6_dorsal_pasca",
#     "2024-05-07-e-e14_dorsal_pasca",
#     "2024-05-07-e-kh2_dorsal_pasca",
#     "2024-05-24-e-all_cell_lines_dorsal_pasca",
#     "2024-05-28-e-all_cell_lines_dorsal_pasca",
#     "2024-05-31-e-all_cell_lines_dorsal_pasca",
#     "2024-06-11-e-all_cell_lines_dorsal_pasca",
#     "2024-06-14-e-all_cell_lines_dorsal_pasca",
#     "2024-06-18-e-all_cell_lines_dorsal_pasca",
#     "2024-06-19-e-sakura-ventral-day46", 
#     "2024-06-21-e-all_cell_lines_dorsal_pasca", 
#     "2024-06-21-e-cady-sakura-dorsal-ventral", #sent job for new SNR params #downloaded
#     # "2024-06-21-e-sakura-dorsa-ventral/"  #not spike sorted
#     "2024-03-20-e-auto-mouse-slice-22542",
#     "2024-02-06-e-auto-mouse-slice2",
#     "2024-01-31-e-auto-mouse-slice",
#     "2024-04-04-e-p001384-pharma-reupload",
#     "2024-02-09-e-pharma1-20380-HS",
#     "2024-07-01-e-sakura-drugs-22194",
#     "2024-06-24-e-sakura-drugs-22097", # sent job for new SNR params # downloaded 
#     "2024-06-25-e-all_cell_lines_dorsal_pasca", #sent job for new SNR params # downloaded
#     "2024-06-28-e-all_cell_lines_dorsal_pasca",
#     "2024-07-01-e-sakura-drugs-22717",
#     "2024-07-02-e-all_cell_lines_dorsal_pasca", #sent job for new SNR params # downloaded
#     "2024-07-02-e-sakura-drugs-20174a",
#     "2024-07-02-e-sakura-drugs-20264",
#     "2024-07-03-e-sakura-drugs-21985",
#     "2024-07-05-e-all_cell_lines_dorsal_pasca",
        #   '2024-03-29-e-interneurons_44',
        #   '2024-04-10-e-interneurons_56',
        #   '2024-04-11-e-interneurons-pasca-57',
        #   '2024-11-04-e-ventral_day44',
        #   '2024-10-25-e-ventral-day33',
# ]
#missed recordings redownload
uuids = [
        '2024-06-03-e-Dorsal_Recordings_ACUTE_6-3-24',
        '2024-06-03-e-Dorsal_Recordings_ACUTE_6-3-24_2',
        '2024-07-03-e-PascamOrgs_rec_3min_ACUTE_Day60_5-4-24/'
]

local_directory = '/Volumes/hunter_ssd/sakura_ephys_data/recs_low_isi'

download_s3_files(endpoint_url, bucket_name, uuids, local_directory)