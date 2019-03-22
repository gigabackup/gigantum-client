import base64
import graphene
import flask
import os

from gtmcore.dataset import Dataset
from gtmcore.inventory.inventory import InventoryManager
from gtmcore.dispatcher import Dispatcher, jobs
from gtmcore.configuration import Configuration
from gtmcore.logging import LMLogger
from gtmcore.workflows.gitlab import GitLabManager, ProjectPermissions
from gtmcore.workflows import DatasetWorkflow, MergeOverride

from lmsrvcore.api import logged_mutation
from lmsrvcore.auth.identity import parse_token
from lmsrvcore.auth.user import get_logged_in_username, get_logged_in_author
from lmsrvcore.api.mutations import ChunkUploadMutation, ChunkUploadInput

from lmsrvlabbook.api.connections.dataset import DatasetConnection
from lmsrvlabbook.api.objects.dataset import Dataset as DatasetObject

logger = LMLogger.get_logger()


class PublishDataset(graphene.relay.ClientIDMutation):

    class Input:
        owner = graphene.String(required=True)
        dataset_name = graphene.String(required=True)
        set_public = graphene.Boolean(required=False)

    job_key = graphene.String()

    @classmethod
    @logged_mutation
    def mutate_and_get_payload(cls, root, info, owner, dataset_name, set_public=False,
                               client_mutation_id=None):
        # Load Dataset
        username = get_logged_in_username()
        ds = InventoryManager().load_dataset(username, owner, dataset_name,
                                             author=get_logged_in_author())
        # Extract valid Bearer token
        if "HTTP_AUTHORIZATION" in info.context.headers.environ:
            token = parse_token(info.context.headers.environ["HTTP_AUTHORIZATION"])
        else:
            raise ValueError(
                "Authorization header not provided. Must have a valid session to query for collaborators")

        job_metadata = {'method': 'publish_dataset',
                        'dataset': ds.key}
        job_kwargs = {'repository': ds,
                      'username': username,
                      'access_token': token,
                      'id_token': flask.g.id_token,
                      'public': set_public}
        dispatcher = Dispatcher()
        job_key = dispatcher.dispatch_task(jobs.publish_repository, kwargs=job_kwargs, metadata=job_metadata)
        logger.info(f"Publishing Dataset {ds.root_dir} in background job with key {job_key.key_str}")

        return PublishDataset(job_key=job_key.key_str)


class SyncDataset(graphene.relay.ClientIDMutation):

    class Input:
        owner = graphene.String(required=True)
        dataset_name = graphene.String(required=True)
        pull_only = graphene.Boolean(required=False)
        override_method = graphene.String(required=False)

    job_key = graphene.String()

    @classmethod
    @logged_mutation
    def mutate_and_get_payload(cls, root, info, owner, dataset_name, pull_only=False,
                               override_method="abort", client_mutation_id=None):
        # Load Dataset
        username = get_logged_in_username()
        ds = InventoryManager().load_dataset(username, owner, dataset_name,
                                             author=get_logged_in_author())

        # Extract valid Bearer token
        token = None
        if hasattr(info.context.headers, 'environ'):
            if "HTTP_AUTHORIZATION" in info.context.headers.environ:
                token = parse_token(info.context.headers.environ["HTTP_AUTHORIZATION"])

        if not token:
            raise ValueError("Authorization header not provided. Must have a valid session to query for collaborators")

        default_remote = ds.client_config.config['git']['default_remote']
        admin_service = None
        for remote in ds.client_config.config['git']['remotes']:
            if default_remote == remote:
                admin_service = ds.client_config.config['git']['remotes'][remote]['admin_service']
                break

        if not admin_service:
            raise ValueError('admin_service could not be found')

        # Configure git creds
        mgr = GitLabManager(default_remote, admin_service, access_token=token)
        mgr.configure_git_credentials(default_remote, username)

        override = MergeOverride(override_method)
        job_metadata = {'method': 'sync_dataset',
                        'dataset': ds.key}
        job_kwargs = {'repository': ds,
                      'username': username,
                      'pull_only': pull_only,
                      'override': override,
                      'access_token': token,
                      'id_token': flask.g.id_token}

        dispatcher = Dispatcher()
        job_key = dispatcher.dispatch_task(jobs.sync_repository, kwargs=job_kwargs, metadata=job_metadata)
        logger.info(f"Syncing Dataset {ds.root_dir} in background job with key {job_key.key_str}")

        return SyncDataset(job_key=job_key.key_str)


class ImportRemoteDataset(graphene.relay.ClientIDMutation):
    class Input:
        owner = graphene.String(required=True)
        dataset_name = graphene.String(required=True)
        remote_url = graphene.String(required=True)

    new_dataset_edge = graphene.Field(DatasetConnection.Edge)

    @classmethod
    def mutate_and_get_payload(cls, root, info, owner, dataset_name, remote_url, client_mutation_id=None):
        username = get_logged_in_username()
        logger.info(f"Importing remote dataset from {remote_url}")
        ds = Dataset(author=get_logged_in_author())

        default_remote = ds.client_config.config['git']['default_remote']
        admin_service = None
        for remote in ds.client_config.config['git']['remotes']:
            if default_remote == remote:
                admin_service = ds.client_config.config['git']['remotes'][remote]['admin_service']
                break

        # Extract valid Bearer token
        if hasattr(info.context, 'headers') and "HTTP_AUTHORIZATION" in info.context.headers.environ:
            token = parse_token(info.context.headers.environ["HTTP_AUTHORIZATION"])
        else:
            raise ValueError("Authorization header not provided. Must have a valid session to query for collaborators")

        gl_mgr = GitLabManager(default_remote, admin_service=admin_service, access_token=token)
        gl_mgr.configure_git_credentials(default_remote, username)

        wf = DatasetWorkflow.import_from_remote(remote_url, username=username)
        ds = wf.dataset

        import_owner = InventoryManager().query_owner(ds)
        # TODO: Fix cursor implementation, this currently doesn't make sense
        cursor = base64.b64encode(f"{0}".encode('utf-8'))
        dsedge = DatasetConnection.Edge(node=DatasetObject(owner=import_owner, name=ds.name),
                                        cursor=cursor)
        return ImportRemoteDataset(new_dataset_edge=dsedge)


class SetDatasetVisibility(graphene.relay.ClientIDMutation):
    class Input:
        owner = graphene.String(required=True)
        dataset_name = graphene.String(required=True)
        visibility = graphene.String(required=True)

    new_dataset_edge = graphene.Field(DatasetConnection.Edge)

    @classmethod
    @logged_mutation
    def mutate_and_get_payload(cls, root, info, owner, dataset_name, visibility,
                               client_mutation_id=None):
        # Load Dataset
        username = get_logged_in_username()
        ds = InventoryManager().load_dataset(username, owner, dataset_name,
                                             author=get_logged_in_author())
        # Extract valid Bearer token
        token = None
        if hasattr(info.context.headers, 'environ'):
            if "HTTP_AUTHORIZATION" in info.context.headers.environ:
                token = parse_token(info.context.headers.environ["HTTP_AUTHORIZATION"])

        if not token:
            raise ValueError("Authorization header not provided. Must have a valid session to query for collaborators")

        default_remote = ds.client_config.config['git']['default_remote']
        admin_service = None
        for remote in ds.client_config.config['git']['remotes']:
            if default_remote == remote:
                admin_service = ds.client_config.config['git']['remotes'][remote]['admin_service']
                break

        if not admin_service:
            raise ValueError('admin_service could not be found')

        # Configure git creds
        mgr = GitLabManager(default_remote, admin_service, access_token=token)
        mgr.configure_git_credentials(default_remote, username)

        if visibility not in ['public', 'private']:
            raise ValueError(f'Visibility must be either "public" or "private";'
                             f'("{visibility}" invalid)')
        with ds.lock():
            mgr.set_visibility(namespace=owner, repository_name=dataset_name, visibility=visibility)

        cursor = base64.b64encode(f"{0}".encode('utf-8'))
        dsedge = DatasetConnection.Edge(node=DatasetObject(owner=owner, name=dataset_name),
                                        cursor=cursor)
        return SetDatasetVisibility(new_dataset_edge=dsedge)


class AddDatasetCollaborator(graphene.relay.ClientIDMutation):
    class Input:
        owner = graphene.String(required=True)
        dataset_name = graphene.String(required=True)
        username = graphene.String(required=True)
        permissions = graphene.String(required=True)

    updated_dataset = graphene.Field(DatasetObject)

    @classmethod
    def mutate_and_get_payload(cls, root, info, owner, dataset_name, username, permissions,
                               client_mutation_id=None):
        # Here "username" refers to the intended recipient username.
        # Todo: it should probably be renamed here and in the frontend to "collaboratorUsername"
        logged_in_username = get_logged_in_username()
        lb = InventoryManager().load_dataset(logged_in_username, owner, dataset_name,
                                             author=get_logged_in_author())

        # TODO: Future work will look up remote in LabBook data, allowing user to select remote.
        default_remote = lb.client_config.config['git']['default_remote']
        admin_service = None
        for remote in lb.client_config.config['git']['remotes']:
            if default_remote == remote:
                admin_service = lb.client_config.config['git']['remotes'][remote]['admin_service']
                break

        # Extract valid Bearer token
        if "HTTP_AUTHORIZATION" in info.context.headers.environ:
            token = parse_token(info.context.headers.environ["HTTP_AUTHORIZATION"])
        else:
            raise ValueError("Authorization header not provided. "
                             "Must have a valid session to query for collaborators")

        if permissions == 'readonly':
            perm = ProjectPermissions.READ_ONLY
        elif permissions == 'readwrite':
            perm = ProjectPermissions.READ_WRITE
        elif permissions == 'owner':
            perm = ProjectPermissions.OWNER
        else:
            raise ValueError(f"Unknown permission set: {permissions}")

        # Add collaborator to remote service
        mgr = GitLabManager(default_remote, admin_service, token)

        existing_collabs = mgr.get_collaborators(owner, dataset_name)

        if username not in [n[1] for n in existing_collabs]:
            logger.info(f"Adding user {username} to {owner}/{dataset_name}"
                        f"with permission {perm}")
            mgr.add_collaborator(owner, dataset_name, username, perm)
        else:
            logger.warning(f"Changing permission of {username} on"
                           f"{owner}/{dataset_name} to {perm}")
            mgr.delete_collaborator(owner, dataset_name, username)
            mgr.add_collaborator(owner, dataset_name, username, perm)
        create_data = {"owner": owner,
                       "name": dataset_name}

        return AddDatasetCollaborator(updated_dataset=DatasetObject(**create_data))


class DeleteDatasetCollaborator(graphene.relay.ClientIDMutation):
    class Input:
        owner = graphene.String(required=True)
        dataset_name = graphene.String(required=True)
        username = graphene.String(required=True)

    updated_dataset = graphene.Field(DatasetObject)

    @classmethod
    def mutate_and_get_payload(cls, root, info, owner, dataset_name, username, client_mutation_id=None):
        logged_in_username = get_logged_in_username()
        ds = InventoryManager().load_dataset(logged_in_username, owner, dataset_name,
                                             author=get_logged_in_author())

        # TODO: Future work will look up remote in LabBook data, allowing user to select remote.
        default_remote = ds.client_config.config['git']['default_remote']
        admin_service = None
        for remote in ds.client_config.config['git']['remotes']:
            if default_remote == remote:
                admin_service = ds.client_config.config['git']['remotes'][remote]['admin_service']
                break

        # Extract valid Bearer token
        if "HTTP_AUTHORIZATION" in info.context.headers.environ:
            token = parse_token(info.context.headers.environ["HTTP_AUTHORIZATION"])
        else:
            raise ValueError("Authorization header not provided. Must have a valid session to query for collaborators")

        # Add collaborator to remote service
        mgr = GitLabManager(default_remote, admin_service, token)
        mgr.delete_collaborator(owner, dataset_name, username)

        create_data = {"owner": owner,
                       "name": dataset_name}

        return DeleteDatasetCollaborator(updated_dataset=DatasetObject(**create_data))


class ExportDataset(graphene.relay.ClientIDMutation):
    class Input:
        owner = graphene.String(required=True)
        dataset_name = graphene.String(required=True)

    job_key = graphene.String()

    @classmethod
    def mutate_and_get_payload(cls, root, info, owner, dataset_name, client_mutation_id=None):
        username = get_logged_in_username()
        working_directory = Configuration().config['git']['working_directory']
        ds = InventoryManager().load_dataset(username, owner, dataset_name,
                                             author=get_logged_in_author())

        job_metadata = {'method': 'export_dataset_as_zip',
                        'dataset': ds.key}
        job_kwargs = {'dataset_path': ds.root_dir,
                      'ds_export_directory': os.path.join(working_directory, 'export')}
        dispatcher = Dispatcher()
        job_key = dispatcher.dispatch_task(jobs.export_dataset_as_zip,
                                           kwargs=job_kwargs,
                                           metadata=job_metadata)

        return ExportDataset(job_key=job_key.key_str)


class ImportDataset(graphene.relay.ClientIDMutation, ChunkUploadMutation):
    class Input:
        chunk_upload_params = ChunkUploadInput(required=True)

    import_job_key = graphene.String()

    @classmethod
    def mutate_and_wait_for_chunks(cls, info, **kwargs):
        return ImportDataset()

    @classmethod
    def mutate_and_process_upload(cls, info, upload_file_path, upload_filename, **kwargs):
        if not upload_file_path:
            logger.error('No file uploaded')
            raise ValueError('No file uploaded')

        username = get_logged_in_username()
        job_metadata = {'method': 'import_dataset_from_zip'}
        job_kwargs = {
            'archive_path': upload_file_path,
            'username': username,
            'owner': username
        }
        dispatcher = Dispatcher()
        job_key = dispatcher.dispatch_task(jobs.import_dataset_from_zip,
                                           kwargs=job_kwargs,
                                           metadata=job_metadata)

        return ImportDataset(import_job_key=job_key.key_str)
