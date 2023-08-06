# -*- encoding: utf-8 -*-
import tempfile
import os
import logging
import shelve
import json
import re
import socket
import httplib
import ConfigParser
import boto
from boto.s3.key import Key
from boto.glacier.exceptions import UnexpectedHTTPResponseError
from boto.exception import S3ResponseError

from bakthat.conf import config, dump_truck, DEFAULT_DESTINATION, DEFAULT_LOCATION, CONFIG_FILE

log = logging.getLogger(__name__)

class glacier_shelve(object):
    """Context manager for shelve.

    Deprecated, here for backward compatibility.

    """

    def __enter__(self):
        self.shelve = shelve.open(os.path.expanduser("~/.bakthat.db"))

        return self.shelve

    def __exit__(self, exc_type, exc_value, traceback):
        self.shelve.close()

class BakthatBackend:
    """Handle Configuration for Backends."""
    def __init__(self, conf=None, profile="default", **kwargs):
        self.conf = conf
        if not conf:
            self.conf = config.get(profile)
            if not self.conf:
                log.error("No {0} profile defined in {1}.".format(profile, CONFIG_FILE))
            if not "access_key" in self.conf or not "secret_key" in self.conf:
                log.error("Missing access_key/secret_key in {0} profile ({1}).".format(profile, CONFIG_FILE))

class RotationConfig(BakthatBackend):
    """Hold backups rotation configuration."""
    def __init__(self, conf=None, profile="default"):
        BakthatBackend.__init__(self, conf, profile)
        self.conf = self.conf.get("rotation")

class S3Backend(BakthatBackend):
    """Backend to handle S3 upload/download."""
    def __init__(self, conf=None, profile="default"):
        BakthatBackend.__init__(self, conf)

        con = boto.connect_s3(self.conf["access_key"], self.conf["secret_key"])

        region_name = self.conf["region_name"]
        if region_name == DEFAULT_LOCATION:
            region_name = ""

        try:
            self.bucket = con.get_bucket(self.conf["s3_bucket"])
        except S3ResponseError, e:
            if e.code == "NoSuchBucket":
                self.bucket = con.create_bucket(self.conf["s3_bucket"], location=region_name)
            else:
                raise e

        self.container = self.conf["s3_bucket"]
        self.container_key = "s3_bucket"

    def download(self, keyname):
        k = Key(self.bucket)
        k.key = keyname

        encrypted_out = tempfile.TemporaryFile()
        k.get_contents_to_file(encrypted_out)
        encrypted_out.seek(0)
        
        return encrypted_out

    def cb(self, complete, total):
        """Upload callback to log upload percentage."""
        percent = int(complete * 100.0 / total)
        log.info("Upload completion: {0}%".format(percent))

    def upload(self, keyname, filename, cb=True):
        k = Key(self.bucket)
        k.key = keyname
        upload_kwargs = {}
        if cb:
            upload_kwargs = dict(cb=self.cb, num_cb=10)
        k.set_contents_from_filename(filename, **upload_kwargs)
        k.set_acl("private")

    def ls(self):
        return [key.name for key in self.bucket.get_all_keys()]

    def delete(self, keyname):
        k = Key(self.bucket)
        k.key = keyname
        self.bucket.delete_key(k)


class GlacierBackend(BakthatBackend):
    """Backend to handle Glacier upload/download."""
    def __init__(self, conf=None, profile="default"):
        BakthatBackend.__init__(self, conf, profile)

        con = boto.connect_glacier(aws_access_key_id=self.conf["access_key"],
                                    aws_secret_access_key=self.conf["secret_key"],
                                    region_name=self.conf["region_name"])

        self.vault = con.create_vault(self.conf["glacier_vault"])
        self.backup_key = "bakthat_glacier_inventory"
        self.container = self.conf["glacier_vault"]
        self.container_key = "glacier_vault"

    def load_archives(self):
        return dump_truck.dump("inventory")

    def backup_inventory(self):
        """Backup the local inventory from shelve as a json string to S3."""
        if config.get("aws", "s3_bucket"):
            archives = self.load_archives()

            s3_bucket = S3Backend(self.conf).bucket
            k = Key(s3_bucket)
            k.key = self.backup_key

            k.set_contents_from_string(json.dumps(archives))

            k.set_acl("private")

    def load_archives_from_s3(self):
        """Fetch latest inventory backup from S3."""
        s3_bucket = S3Backend(self.conf).bucket
        try:
            k = Key(s3_bucket)
            k.key = self.backup_key

            return json.loads(k.get_contents_as_string())
        except S3ResponseError, exc:
            return {}

#    def restore_inventory(self):
#        """Restore inventory from S3 to DumpTruck."""
#        if config.get("aws", "s3_bucket"):
#            loaded_archives = self.load_archives_from_s3()

#            # TODO faire le restore
#        else:
#            raise Exception("You must set s3_bucket in order to backup/restore inventory to/from S3.")

    def restore_inventory(self):
        """Restore inventory from S3 to local shelve."""
        if config.get("aws", "s3_bucket"):
            loaded_archives = self.load_archives_from_s3()

            with glacier_shelve() as d:
                archives = {}
                for a in loaded_archives:
                    print a
                    archives[a["filename"]] = a["archive_id"]
                d["archives"] = archives
        else:
            raise Exception("You must set s3_bucket in order to backup/restore inventory to/from S3.")


    def upload(self, keyname, filename):
        archive_id = self.vault.concurrent_create_archive_from_file(filename, keyname)

        dump_truck.upsert({"filename": keyname, "archive_id": archive_id}, "inventory")

        self.backup_inventory()

    def get_archive_id(self, filename):
        """Get the archive_id corresponding to the filename."""
        res = dump_truck.execute('SELECT archive_id FROM inventory WHERE filename == "{0}"'.format(filename))
        if res:
            return res[0].get("archive_id")

    def get_job_id(self, filename):
        """Get the job_id corresponding to the filename.

        :type filename: str
        :param filename: Stored filename.

        """
        res = dump_truck.execute('SELECT job_id FROM jobs WHERE filename == "{0}"'.format(filename))
        if res:
            return res[0].get("job_id")
    
    def delete_job(self, filename):
        """Delete the job entry for the filename.

        :type filename: str
        :param filename: Stored filename.

        """
        dump_truck.execute("DELETE FROM jobs WHERE filename == '{0}'".format(filename))

    def download(self, keyname, job_check=False):
        """Initiate a Job, check its status, and download the archive if it's completed."""
        archive_id = self.get_archive_id(keyname)
        if not archive_id:
            return
        
        job = None

        job_id = self.get_job_id(keyname)

        if job_id:
            try:
                job = self.vault.get_job(job_id)
            except UnexpectedHTTPResponseError: # Return a 404 if the job is no more available
                self.delete_job(keyname)

        if not job:
            job = self.vault.retrieve_archive(archive_id)
            job_id = job.id
            dump_truck.upsert({"filename": keyname, "job_id": job_id}, "inventory")

        log.info("Job {action}: {status_code} ({creation_date}/{completion_date})".format(**job.__dict__))

        if job.completed:
            log.info("Downloading...")
            encrypted_out = tempfile.TemporaryFile()

            # Boto related, download the file in chunk
            chunk_size = 4 * 1024 * 1024
            num_chunks = int(math.ceil(job.archive_size / float(chunk_size)))
            job._download_to_fileob(encrypted_out, num_chunks, chunk_size,
                                     True, (socket.error, httplib.IncompleteRead))

            encrypted_out.seek(0)

            return encrypted_out
        else:
            log.info("Not completed yet")
            if job_check:
                return job
            return

    def retrieve_inventory(self, jobid):
        """Initiate a job to retrieve Galcier inventory or output inventory."""
        if jobid is None:
            return self.vault.retrieve_inventory(sns_topic=None, description="Bakthat inventory job")
        else:
            return self.vault.get_job(jobid)

    def retrieve_archive(self, archive_id, jobid):
        """Initiate a job to retrieve Galcier archive or download archive."""
        if jobid is None:
            return self.vault.retrieve_archive(archive_id, sns_topic=None, description='Retrieval job')
        else:
            return self.vault.get_job(jobid)


    def ls(self):
        return [ivt.get("filename") for ivt in dump_truck.dump("inventory")]

    def delete(self, keyname):
        archive_id = self.get_archive_id(keyname)
        if archive_id:
            self.vault.delete_archive(archive_id)
            with glacier_shelve() as d:
                archives = d["archives"]

                if keyname in archives:
                    del archives[keyname]

                d["archives"] = archives

            dump_truck.execute("DELETE FROM inventory WHERE filename == '{0}'".format(keyname))

            self.backup_inventory()

    def upgrade_to_dump_truck(self):
        try:
            with glacier_shelve() as d:
                archives = d["archives"]
                if "archives" in d:
                    print archives
                    for key, archive_id in archives.items():
                        #print {"filename": key, "archive_id": archive_id}
                        dump_truck.upsert({"filename": key, "archive_id": archive_id}, "inventory")
                        del archives[key]
                d["archives"] = archives
        except Exception, exc:
            log.exception(exc)