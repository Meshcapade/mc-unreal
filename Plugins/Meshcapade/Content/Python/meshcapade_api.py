import unreal
import urllib.parse
import logging
import sys
import subprocess
import platform
import os
from datetime import datetime, timezone
from keycloak_auth_wrapper import AuthBridge
import requests
import pandas as pd
from mc_plugin_config import API_LINK
from logger.mcme_logger import logger
import threading
import time
from enum import Enum


GLB_EXPORT_TIMEOUT = 5*60  # seconds timeout for GLB export



class MCMEState:
    # avatars = None
    login_status = False
    avatar_df = pd.DataFrame()
    mesh_df = pd.DataFrame()
    avatars = None
    smart_glb_creator = None


@unreal.uclass()
class MeshcapadeAuthLibrary(unreal.BlueprintFunctionLibrary):

    @unreal.ufunction(static=True, ret=bool)
    def is_logged_in() -> bool:
        """
        Check if the user is logged in.
        """
        url_avatars = f"{API_LINK}/api/v1/avatars?limit=1"
        try:
            response = AuthBridge.authorized_request(method="GET", url=url_avatars)
        except requests.exceptions.RequestException as e:
            return False
        if response.status_code == 401:
            logger.debug("❌ Unauthorized access, user is not logged in.")
            return False
        elif response.status_code == 200:
            logger.debug("✅ User is logged in.")
            return True
        
    @unreal.ufunction(static=True, ret=bool)
    def get_avatars_and_scenes() -> bool:
        """
        Fetch avatars and scenes from the Meshcapade API.
        """
        # get avatars
        url_avatars = f"{API_LINK}/api/v1/avatars?limit=1000"

        url_scenes = f"{API_LINK}/api/v1/scenes?limit=1000&page=1"

        # url = f"{API_LINK}/api/v1/assets?limit=20&page=1&filter[type]=AVATAR,SCENE&filter[state]=READY,ERROR"

        try:
            response = AuthBridge.authorized_request(method="GET", url=url_avatars)
            MCMEState.avatar_df = pd.json_normalize(response.json()["data"])
            # Filter the dataframe based on the list of IDs
            MCMEState.avatar_df = MCMEState.avatar_df[
                MCMEState.avatar_df["attributes.origin"].isin(
                    ["FROM_VIDEO", "FROM_SMPL_MOTION"]
                )
            ]
            logger.info(f"✅ Retrieved {len(MCMEState.avatar_df)} avatars.")

            # get scenes
            response = AuthBridge.authorized_request(method="GET", url=url_scenes)
            scenes_df = pd.json_normalize(response.json()["data"])
            MCMEState.avatar_df = pd.concat(
                [MCMEState.avatar_df, scenes_df], ignore_index=True
            ).sort_values(by=["attributes.created_at"], ascending=False)
            
            logger.info(f"✅ Retrieved {len(scenes_df)} scenes.")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to fetch avatars: {e}")
            return False
    
    @unreal.ufunction(static=True, ret=bool)
    def get_meshes() -> bool:
        """
        Fetch meshes from the Meshcapade API.
        """
        url = f"{API_LINK}/api/v1/meshes?limit=1000&page=1"
        payload = {}
        response = AuthBridge.authorized_request(method="GET", url=url, data=payload)
        if response.status_code != 200:
            logger.error(
                f"❌ Failed to fetch meshes: {response.status_code} - {response.text}"
            )
            return None

        MCMEState.mesh_df = pd.json_normalize(response.json()["data"])
        return True

    @unreal.ufunction(static=True, ret=bool)
    def sync_vault() -> int:

        status_avatars = MeshcapadeAuthLibrary.get_avatars_and_scenes()
        
        status_meshes = MeshcapadeAuthLibrary.get_meshes()
        
        return status_avatars and status_meshes
    
    @unreal.ufunction(static=True, ret=bool, params=[str])
    def mesh_exists_by_mesh_id(id: str) -> bool:
        """
        Check if a mesh exists by its ID.
        """
        if MCMEState.mesh_df.empty:
            logger.warning("⚠️ No mesh data available.")
            return False

        # Get the status of the mesh
        if id in MCMEState.mesh_df["id"].values:
            return True
        else:
            logger.error(f"❌ Mesh with ID {id} does not exist.")
            return False
    

    def get_mesh_ids_by_avatar_id(id: str) -> str:
        """
        Get the mesh ID by avatar ID.
        """
        if MCMEState.mesh_df.empty:
            logger.warning("⚠️ No mesh data available.")
            return []

        # Get the mesh ID for the given avatar ID
        mesh_exists = MCMEState.mesh_df[
            MCMEState.mesh_df["attributes.metadata.parentID"] == id
        ]

        if not mesh_exists.empty:
            mesh_ready = mesh_exists[mesh_exists["attributes.state"] == "READY"]
            if not mesh_ready.empty:
                return unreal.MeshState.MESH_READY, mesh_ready["id"].tolist()
            else:
                return unreal.MeshState.MESH_EXIST_NOT_READY, mesh_exists["id"].tolist()
        else:
            logger.debug(f"❌ No mesh found for avatar ID: {id}")
            return unreal.MeshState.MESH_NOT_EXIST, []


    def delete_mesh_by_id(id: str) -> bool:
        """
        Delete a mesh by its ID.
        """
        if not MeshcapadeAuthLibrary.mesh_exists_by_mesh_id(id):
            logger.error(f"❌ Mesh with ID {id} does not exist.")
            return False

        url = f"{API_LINK}/api/v1/meshes/{id}"
        response = AuthBridge.authorized_request(method="DELETE", url=url)

        if response.status_code == 204:
            logger.info(f"✅ Mesh with ID {id} deleted successfully.")
            return True
        else:
            logger.error(
                f"❌ Failed to delete mesh with ID {id}: {response.status_code} - {response.text}"
            )
            return False
    
    @unreal.ufunction(static=True, ret=int)
    def get_avatar_count() -> int:
        """
        Get the number of avatars in the vault.
        """
        if MCMEState.avatar_df is not None:
            count = len(MCMEState.avatar_df)
            logger.info(f"✅ Avatar count: {count}")
            return count
        else:
            logger.error("❌ No avatar data available.")
            return 0

    @unreal.ufunction(static=True, ret=str, params=[int])
    def get_avatar_name_by_index(index: int) -> str:
        try:
            if MCMEState.avatar_df is not None and 0 <= index < len(
                MCMEState.avatar_df
            ):
                avatar_name = MCMEState.avatar_df.iloc[index]["name"]
                logger.info(f"✅ Avatar name at index {index}: {avatar_name}")
                return avatar_name
            else:
                logger.error("❌ Invalid index or no avatar data available.")
                return ""
        except Exception as e:
            logger.error(f"❌ Failed to fetch avatars: {e}")
            return ""

    @unreal.ufunction(static=True, ret=unreal.Array(unreal.Avatar))
    def create_avatars_from_cache() -> list[unreal.Avatar]:
        df = MCMEState.avatar_df

        result = []
        if df is None:
            logger.warning("⚠️ No avatars loaded.")
            return result
        
        # avatars without mesh will be initiated for glb export
        # avatars_without_mesh = []

        for _, row in df.iterrows():
            a = unreal.Avatar()
            a.name = row.get("attributes.name", "Unnamed")
            a.id = row.get("id", "unknown")
            YMD = (
                datetime.fromtimestamp(int(row.get("attributes.created_at", "0")), timezone.utc)
                .strftime("%Y-%m-%d")
                .split("-")
            )
            a.creation_date = unreal.DateTime(int(YMD[0]), int(YMD[1]), int(YMD[2]))
            
            a.mesh_state, mesh_ids = MeshcapadeAuthLibrary.get_mesh_ids_by_avatar_id(a.id)

            result.append(a)

        MCMEState.avatar_array = unreal.Array(unreal.Avatar)

        MCMEState.avatar_array.extend(result)
        return MCMEState.avatar_array

    @unreal.ufunction(static=True, ret=unreal.Array(unreal.Avatar), params=[unreal.Array(unreal.Avatar)])
    def update_avatars_from_cache(avatar_array: list[unreal.Avatar]) -> list[unreal.Avatar]:
        """
        Update the given avatars from the cache.
        This function will take the avatars and update their status from the dataframes.
        """

        for index, avatar in enumerate(avatar_array):
            # Find the avatar in the dataframe
            df_row = MCMEState.avatar_df[MCMEState.avatar_df["id"] == avatar.id]
            if not df_row.empty:
                # Update the avatar's name and creation date
                avatar.name = df_row.iloc[0]["attributes.name"]
                YMD = (
                datetime.fromtimestamp(int(df_row.get("attributes.created_at", "0")), timezone.utc)
                .strftime("%Y-%m-%d")
                .split("-")
                )
                avatar.creation_date = unreal.DateTime(int(YMD[0]), int(YMD[1]), int(YMD[2]))
                
                # Update mesh state and IDs
                avatar.mesh_state, _ = MeshcapadeAuthLibrary.get_mesh_ids_by_avatar_id(avatar.id)
                
                # Update the avatar in the array
                avatar_array[index] = avatar
            else:
                logger.error(f"❌ Avatar with ID {avatar.id} not found in cache.")

        # Create avatars from the updated cache
        return avatar_array
    
    
    @unreal.ufunction(static=True, ret=bool, params=[unreal.Array(unreal.Avatar)])
    def smart_glb_creator(avatar_array: list[unreal.Avatar]) -> bool:
        """
        Smart GLB creator for avatars.
        This function will check if the GLB is ready, if not, it will initiate the export.
        """
        logger.info("🔄 Starting smart GLB creator thread...")

        avatar_without_mesh = [avatar for avatar in avatar_array if 
                               (avatar.mesh_state == unreal.MeshState.MESH_NOT_EXIST) or 
                               (avatar.mesh_state == unreal.MeshState.MESH_EXIST_NOT_READY)]
        
        while len(avatar_without_mesh) > 0:
            
            # Check if the avatar is ready
            for idx, avatar in enumerate(avatar_without_mesh):
                id = avatar.id
                avatar.mesh_state, mesh_ids = MeshcapadeAuthLibrary.get_mesh_ids_by_avatar_id(id)
                
                avatar_without_mesh[idx] = avatar  # Update the avatar in the list because UE does not support mutable objects in lists

                logger.debug(f"🔄 Checking GLB export status for avatar {avatar.name} with id {id} and mesh exist state is {avatar.mesh_state}, \
                             unreal mesh states are {unreal.MeshState.MESH_NOT_EXIST} and {unreal.MeshState.MESH_EXIST_NOT_READY}")
                
                if avatar.mesh_state == unreal.MeshState.MESH_READY:
                    logger.info(f"✅ GLB for avatar {avatar.name} with id {id} is ready.")
                    logger.debug(f"{avatar_without_mesh[0]}, {avatar}")
                    avatar_without_mesh.remove(avatar)
                    continue
                
                elif avatar.mesh_state == unreal.MeshState.MESH_EXIST_NOT_READY:
                    for mesh_id in mesh_ids:
                        # check for how long it is in AWAITING_PROCESSING state
                        mesh_id = mesh_ids[0]
                        # get time since the mesh was created
                        mesh_creation_time_delta = datetime.now(timezone.utc) - datetime.fromtimestamp(
                            int(
                                MCMEState.mesh_df[
                                    MCMEState.mesh_df["id"] == mesh_id
                                ]["attributes.created_at"].values[0]
                            ), timezone.utc
                        )
                        
                        logger.debug(f"⏳ Mesh {mesh_id} creation time delta: {mesh_creation_time_delta.total_seconds()} seconds")
                        
                        if mesh_creation_time_delta.total_seconds() > GLB_EXPORT_TIMEOUT:
                            # delete this mesh and create a new one
                            if MeshcapadeAuthLibrary.delete_mesh_by_id(mesh_id):
                                logger.info(f"✅ Mesh {mesh_id} was deleted due to timeout. Creating a new GLB for avatar {avatar.name} with id {id}.")
                                MeshcapadeAuthLibrary.initiate_glb_export(avatar)
                                time.sleep(30)  # Sleep for few second to avoid spamming the API
                                
                elif avatar.mesh_state == unreal.MeshState.MESH_NOT_EXIST:
                    if not MeshcapadeAuthLibrary.initiate_glb_export(avatar):
                        logger.error(f"❌ Failed to initiate GLB export for avatar {avatar.name} with id {id}.")
                        continue
                    else:
                        logger.debug("✅ sleeping now")
                        time.sleep(30)  # Sleep for few second to avoid spamming the API
                    
                
                else:
                    logger.error(f"❌ Invalid mesh state for avatar {avatar.name} with id {id}: {avatar.mesh_state}.")
                    continue
                
                if not AuthBridge.is_auth_done():
                    logger.error("❌ AuthManager is not initialized. Smart GLB creator aborted.")
                    return False
            
            time.sleep(5)  # Sleep for a while before checking again
            try:
                MeshcapadeAuthLibrary.sync_vault()  # Sync the vault to get the latest data
            except Exception as e:
                logger.error(f"❌ Failed to sync vault: {e}")
            
            avatar_without_mesh = MeshcapadeAuthLibrary.update_avatars_from_cache(avatar_without_mesh)
        
        MeshcapadeAuthLibrary.download_avatars(avatar_array)
        logger.info("✅ Smart GLB creator thread finished.")
        
        return True
    

    def initiate_glb_export(avatar: unreal.Avatar) -> bool:
        """
        Export an avatar by its ID.
        """
        id = avatar.id
        
        headers = {
            "Content-Type": "application/json",
        }
        
        json_data = {
            "format": "GLB",
            "animation": "scan",
        }
        if (
            MCMEState.avatar_df[MCMEState.avatar_df["id"] == id][
                "attributes.type"
            ].values[0]
            == "SCENE"
        ):
            url = f"{API_LINK}/api/v1/scenes/{id}/export"
        elif (
            MCMEState.avatar_df[MCMEState.avatar_df["id"] == id][
                "attributes.type"
            ].values[0]
            == "AVATAR"
        ):
            url = f"{API_LINK}/api/v1/avatars/{id}/export"
        else:
            logger.error(
                f"❌ Invalid asset type: {MCMEState.avatar_df[MCMEState.avatar_df['id']==id]['attributes.type'].values[0]}. Must be 'avatar' or 'scene'."
            )
            return False

        # response = requests.post(url, headers=headers, json=json_data)
        response = AuthBridge.authorized_request(
            method="POST", url=url, headers=headers, json=json_data
        )
        if response.status_code == 200:
            logger.info(f"✅ Avatar export for {avatar.name} with id {id} initiated successfully.")
            return True
        else:
            logger.warning(
                f"❌ Failed to initiate avatar export for {avatar.name} with id {id}: {response.status_code} - {response.text}"
            )
            return False

    
    def dump_mesh_and_avatar_data(avatar_df, mesh_df):
        """
        Dump the mesh and avatar data to a CSV file.
        """
        if avatar_df.empty:
            logger.warning("⚠️ No avatar data available to dump.")
            return

        # Create the cache directory if it doesn't exist
        cache_dir = os.path.join(
            unreal.SystemLibrary.get_project_content_directory(), "..", "MeshcapadeCache"
        )
        os.makedirs(cache_dir, exist_ok=True)

        # Define the file path
        file_path = os.path.join(cache_dir, "meshcapade_data.csv")

        # Save the DataFrame to a CSV file
        avatar_df.to_csv(file_path, index=False)
        logger.info(f"✅ Mesh and avatar data dumped to {file_path}")

        if mesh_df.empty:
            logger.warning("⚠️ No mesh data available to dump.")
            return

        # Save the mesh DataFrame to a CSV file
        mesh_file_path = os.path.join(cache_dir, "meshcapade_mesh_data.csv")
        mesh_df.to_csv(mesh_file_path, index=False)
        logger.info(f"✅ Mesh data dumped to {mesh_file_path}")

    
    @unreal.ufunction(static=True, ret=bool, params=[str])
    def download_asset_by_id(id: str) -> bool:
        """
        Download an asset by its ID.
        """

        project_path = unreal.SystemLibrary.get_project_content_directory()

        df = MCMEState.avatar_df

        # Extract the filename from the filtered dataframe
        filename = df[df["id"] == id]["attributes.name"].values[0]

        # get list of all meshes
        mesh_data = MCMEState.mesh_df
        
        # ####### DEBUG
        # print(f"Mesh data: {mesh_data}")
        # MeshcapadeAuthLibrary.dump_mesh_and_avatar_data(MCMEState.avatar_df, mesh_data)
        ##########
        
        
        if mesh_data is None:
            logger.error("❌ Failed to fetch mesh data.")
            return False

        # create the cache directory if it doesn't exist
        cache_dir = os.path.join(project_path, "..", "MeshcapadeCache")
        os.makedirs(cache_dir, exist_ok=True)

        mesh_id = mesh_data[mesh_data["attributes.metadata.parentID"] == id]
        
        if mesh_id.empty:
            logger.error(f"❌ No mesh found for ID: {id}.")
            return False
        else:
            mesh_id = mesh_id.iloc[0]  # Get the first matching mesh

        # Download the GLB file
        download_url = mesh_id["attributes.url.path"]

        response = requests.get(download_url, stream=True)
        # response = AuthBridge.authorized_request(method="GET", url=download_url, stream=True)
        if response.status_code == 200:
            with open(os.path.join(cache_dir, f"{filename}-{id}.glb"), "wb") as f:
                for chunk in response.iter_content(chunk_size=1048576):
                    if chunk:
                        f.write(chunk)
            logger.info("✅ {} GLB file downloaded successfully.".format(filename))
        else:
            logger.error(
                f"❌ Failed to download file: {response.status_code} - {response.text}"
            )
            return False

        return True


    @unreal.ufunction(static=True, ret=bool, params=[unreal.Array(unreal.Avatar)])
    def import_assets_by_ids(avatars: list[unreal.Avatar]) -> bool:
        """
        Import assets by their IDs.
        """

        # avatars_without_mesh = []
        # avatars_with_mesh = []

        # # return False if any of the import fails
        # return_status = True

        # for idx, avatar in enumerate(avatars):

        #     mesh_state, _ = MeshcapadeAuthLibrary.get_mesh_ids_by_avatar_id(avatar.id)
        #     if mesh_state == unreal.MeshState.MESH_NOT_EXIST or mesh_state == unreal.MeshState.MESH_EXIST_NOT_READY:
        #         avatars_without_mesh.append(avatar)
        #         logger.warning(
        #             f"⚠️ GLB for Avatar {avatar.name} with ID {avatar.id} is not ready or does not exist"
        #         )
        #     else:
        #         avatars_with_mesh.append(avatar)
        
        # start smart GLB creator thread
        print(MCMEState.smart_glb_creator)
        if MCMEState.smart_glb_creator is None:
            MCMEState.smart_glb_creator = threading.Thread(
                target=MeshcapadeAuthLibrary.smart_glb_creator,
                args=(avatars,),
                daemon=True
            )
            MCMEState.smart_glb_creator.start()
        elif not MCMEState.smart_glb_creator.is_alive():
            MCMEState.smart_glb_creator = threading.Thread(
                target=MeshcapadeAuthLibrary.smart_glb_creator,
                args=(avatars,),
                daemon=True
            )
            MCMEState.smart_glb_creator.start()
            

        # # download and import avatars in UE
        # if len(avatars_with_mesh) > 0:
        #     import_status_batch1 = MeshcapadeAuthLibrary.download_and_import_avatars(avatars_with_mesh)
        # else:
        #     import_status_batch1 = True
        
        # # MCMEState.smart_glb_creator.join()  # Wait for the smart GLB creator thread to finish
        
        # # if len(avatars_without_mesh) > 0:
        # #     import_status_batch2 = MeshcapadeAuthLibrary.download_and_import_avatars(avatars_without_mesh)
        # # else:
        # import_status_batch2 = True
        
        # return_status = import_status_batch1 and import_status_batch2

        return False
    
    
    def download_avatars(avatars_with_mesh):
        """
        Download and import avatars with mesh into Unreal Engine.
        """
        
        return_status = True
        for avatar in avatars_with_mesh:

            # download
            logger.info(f"✅ Downloading {avatar.name} with ID: {avatar.id}")
            if not MeshcapadeAuthLibrary.download_asset_by_id(avatar.id):
                logger.error(f"❌ Failed to download {avatar.name}")
                return_status = False
                continue
                
        return return_status
    
               
    @unreal.ufunction(static=True, ret=bool, params=[unreal.Array(unreal.Avatar)])     
    def import_downloaded_avatars(downloaded_avatars: list[unreal.Avatar]) -> bool:

        tasks = []
        logger.debug(f"✅ Importing {len(downloaded_avatars)} downloaded avatars into Unreal Engine.")
        project_path = unreal.SystemLibrary.get_project_content_directory()
        
        return_status = True
        
        for avatar in downloaded_avatars:
            
            logger.info(f"✅ Importing {avatar.name} with ID: {avatar.id}")

            # remove if asset directory already exists
            destination_path = f"/Game/MeshcapadeVault/{avatar.name}-{avatar.id}"
            if unreal.EditorAssetLibrary.does_directory_exist(destination_path):
                if not unreal.EditorAssetLibrary.delete_directory(destination_path):
                    logger.error(
                        f"❌ Failed to remove existing directory: {destination_path}; remove it manually."
                    )
                    return_status = False
                    continue
                logger.info(f"✅ Removed existing directory: {destination_path}")
                
            # import the asset
            task = unreal.AssetImportTask()
            task.filename = f"{project_path}\..\MeshcapadeCache\{avatar.name}-{avatar.id}.glb"
            task.destination_path = f"/Game/MeshcapadeVault/{avatar.name}-{avatar.id}"
            task.automated = True
            task.save = True
            tasks.append(task)

        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)

        return return_status


    @unreal.ufunction(static=True, ret=bool)
    def is_smart_glb_creator_running() -> bool:
        """
        Check if the smart GLB creator thread is running.
        """
        if MCMEState.smart_glb_creator is None:
            return False
        return MCMEState.smart_glb_creator.is_alive()


    @unreal.ufunction(static=True, params=[str])
    def addToClipBoard(text: str):
        df = pd.DataFrame([text])
        df.to_clipboard(index=False, header=False)

    @unreal.ufunction(static=True, ret=bool, params=[str])
    def delete_meshes_by_avatar_id(id: str) -> bool:
        """
        Delete the mesh associated with the given avatar ID.
        """
        # get mesh assets by avatar ID
        mesh_assets_ids = MeshcapadeAuthLibrary.get_mesh_ids_by_avatar_id(id)[1]
        
        if len(mesh_assets_ids) == 0:
            logger.error(f"❌ No mesh found for avatar ID: {id}.")
            return False
        # delete each mesh asset
        for mesh_id in mesh_assets_ids:
            if not MeshcapadeAuthLibrary.delete_mesh_by_id(mesh_id):
                logger.error(f"❌ Failed to delete mesh with ID: {mesh_id}.")
                return False
            else:
                logger.info(f"✅ Mesh with ID: {mesh_id} deleted successfully.")
                
        return True