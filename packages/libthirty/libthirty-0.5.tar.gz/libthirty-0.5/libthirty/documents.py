from docar import Document, Collection
from docar import fields
from docar.backends.http import HttpBackendManager

from libthirty.state import uri, app_uri, service_uri, resource_collection_uri
from libthirty.validators import naming, max_25_chars, naming_with_dashes

import os


HttpBackendManager.SSL_CERT = os.path.join(
        os.path.dirname(__file__), "ssl", "StartSSL_CA.pem")


class User(Document):
    username = fields.StringField(validators=[naming, max_25_chars])
    email = fields.StringField()
    is_active = fields.BooleanField()


class Account(Document):
    name = fields.StringField(validators=[naming, max_25_chars])
    #users = fields.CollectionField(User)

    class Meta:
        backend_type = 'http'
        identifier = 'name'


class CnameRecord(Document):
    record = fields.StringField()

    class Meta:
        backend_type = 'http'
        identifier = 'record'


class CnameRecords(Collection):
    document = CnameRecord


class EnvironmentVariable(Document):
    id = fields.NumberField(render=False, optional=True)
    name = fields.StringField()
    value = fields.StringField()

    class Meta:
        backend_type = 'http'


class EnvironmentVariables(Collection):
    document = EnvironmentVariable


class Postgres(Document):
    name = fields.StringField(validators=[naming_with_dashes, max_25_chars],
            read_only=True, optional=True)
    label = fields.StaticField(value="postgres")
    variant = fields.ChoicesField(choices=['postgres_micro'],
            default="postgres_micro")
    username = fields.StringField(optional=True, read_only=True)
    password = fields.StringField(optional=True, read_only=True)
    host = fields.StringField(optional=True, read_only=True)
    port = fields.NumberField(optional=True, read_only=True)
    published = fields.BooleanField(default=False, read_only=True)

    class Meta:
        backend_type = 'http'
        identifier = 'name'
        context = ['account']

    def post_uri(self):
        return '%s/services' % app_uri()

    def uri(self):
        return service_uri(service='postgres')


class PostgresCollection(Collection):
    document = Postgres

    def uri(self):
        return resource_collection_uri(label='postgres')


class Mongodb(Document):
    name = fields.StringField(validators=[naming_with_dashes, max_25_chars],
            read_only=True, optional=True)
    label = fields.StaticField(value="mongodb")
    variant = fields.ChoicesField(choices=['mongodb_micro'],
            default='mongodb_micro')
    username = fields.StringField(optional=True, read_only=True)
    password = fields.StringField(optional=True, read_only=True)
    host = fields.StringField(optional=True, read_only=True)
    port = fields.NumberField(optional=True, read_only=True)
    published = fields.BooleanField(default=False, read_only=True)

    class Meta:
        backend_type = 'http'
        identifier = 'name'
        context = ['account']

    def post_uri(self):
        return '%s/services' % app_uri()

    def uri(self):
        return service_uri(service='mongodb')


class MongodbCollection(Collection):
    document = Mongodb

    def uri(self):
        return resource_collection_uri(label='mongodb')


class Repository(Document):
    name = fields.StringField(validators=[naming_with_dashes, max_25_chars],
            read_only=True, optional=True, render=False)
    label = fields.StaticField(value="repository")
    variant = fields.ChoicesField(choices=['git'], default='git')
    location = fields.StringField()
    ssh_key = fields.StringField(optional=True)

    class Meta:
        backend_type = 'http'
        identifier = 'name'
        context = ['account']

    def post_uri(self):
        return '%s/services' % app_uri()

    def uri(self):
        return service_uri(service='repository')


class RepositoryCollection(Collection):
    document = Repository

    def uri(self):
        return resource_collection_uri(label='repository')


class Worker(Document):
    name = fields.StringField(validators=[naming_with_dashes, max_25_chars],
            read_only=True, render=False, optional=True)
    label = fields.StaticField(value="worker")
    variant = fields.ChoicesField(choices=['python'], default='python')
    instances = fields.NumberField(default=1)
    published = fields.BooleanField(default=False, read_only=True)
    envvars = fields.CollectionField(EnvironmentVariables, inline=True)

    class Meta:
        backend_type = 'http'
        identifier = 'name'
        context = ['account']

    def post_uri(self):
        return '%s/services' % app_uri()

    def uri(self):
        return service_uri(service='worker')


class WorkerCollection(Collection):
    document = Worker

    def uri(self):
        return resource_collection_uri(label='worker')


class App(Document):
    name = fields.StringField(validators=[naming, max_25_chars])
    label = fields.StaticField(value="app")
    variant = fields.ChoicesField(default='python',
            choices=['static', 'python'])
    repository = fields.ForeignDocument(Repository)
    postgres = fields.ForeignDocument(Postgres, optional=True)
    mongodb = fields.ForeignDocument(Mongodb, optional=True)
    worker = fields.ForeignDocument(Worker, optional=True)
    repo_commit = fields.StringField(default='HEAD')
    region = fields.ChoicesField(default="eu-nl", choices=['eu-nl', 'ams1'])
    instances = fields.NumberField(default=1)
    dns_record = fields.StringField(optional=True)
    cnames = fields.CollectionField(CnameRecords, inline=True)
    published = fields.BooleanField(default=False, read_only=True)
    envvars = fields.CollectionField(EnvironmentVariables, inline=True)

    class Meta:
        backend_type = 'http'
        identifier = 'name'
        context = ['account']

    def post_uri(self):
        return '%s/apps' % uri()

    def uri(self):
        return app_uri(appname=self.name)


class AppCollection(Collection):
    document = App

    def uri(self):
        return '%s/apps' % uri()
