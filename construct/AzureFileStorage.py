# Listing the Approved WIR Documents on the Azure File Share
from azure.core.exceptions import (
    ResourceExistsError,
    ResourceNotFoundError
)

from azure.storage.fileshare import (
    ShareServiceClient,
    ShareClient,
    ShareDirectoryClient,
    ShareFileClient
)

def list_files_and_dirs(connection_string, share_name, dir_name):
    try:
        # Create a ShareClient from a connection string
        share_client = ShareClient.from_connection_string(
            connection_string, share_name)
        item_list = []
        for item in list(share_client.list_directories_and_files(dir_name)):
            item_list.append(item["name"])
        return item_list

    except ResourceNotFoundError as ex:
        print("ResourceNotFoundError:", ex.message)