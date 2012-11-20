#==========================================================================
# Copyright 2012 Lucidel, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this work except in compliance with the License.
# You may obtain a copy of the License in the LICENSE file, or at:
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#==========================================================================

from django.db import models, router
from django.db.models.deletion import Collector
from .manager import MongoManager
from .fields import MongoIdField
import pymongo

class MongoModel(models.Model):
    id = MongoIdField()
    
    objects = MongoManager()
    
    class Meta:
        abstract = True
        managed = False #don't forget this to prevent Django create table in DB
        
    def delete(self, using=None):
        using = using or router.db_for_write(self.__class__, instance=self)
        assert self._get_pk_val() is not None, "%s object can't be deleted because its %s attribute is set to None." % (self._meta.object_name, self._meta.pk.attname)

        # Find all the objects than need to be deleted.
        collector = Collector(using=using)
        collector.collect([self])

        #hack to prevent ORM delet object via sql
        #it does not use QuerySet - directly sql module :(
        to_delete = {}
        for k in collector.data.keys()[:]:
            if issubclass(k,MongoModel):
                to_delete.update({k:collector.data.pop(k)})

        for key, object_set in to_delete.items():
            for obj in object_set:
                cls = obj.__class__
                if not cls._meta.auto_created:
                    models.signals.pre_delete.send(sender=cls, instance=obj)

                cls._default_manager.filter(pk=obj.pk).delete()

                if not cls._meta.auto_created:
                    models.signals.post_delete.send(sender=cls, instance=obj)


        # Delete other objects.
        collector.delete()
#        delete_objects(seen_objs, using)

    delete.alters_data = True
    
    @classmethod
    def ensure_indexes(cls, verbosity=1):
        #FIXME: add supporind mongo index features like asceding indexing
        opt = cls._meta

        if cls._requires_indexing(verbosity) is False:
            if verbosity >= 1:
                print u'Skipping index installation for %s model (indexes already aligned with the model).' % opt
            return

        if verbosity >= 1:
            print u'Installing index for %s model' % opt

        cls.objects.drop_indexes()

        for unique_fields in opt.unique_together:
            if verbosity >= 2:
                print u'Ensure uniquer indexes for %s' % opt, unique_fields
            
            args = []
            
            for f in unique_fields:
                column = opt.get_field(f).get_attname_column()[1]
                args.append((column, pymongo.DESCENDING))

            cls.objects.ensure_index(args, unique=True, dropDups=True, name=('%s_%s' % (cls.__name__,'unique_together')))
        
        for field in opt.fields:
            if field.db_index:
                column = field.get_attname_column()[1]
                if field.unique:
                    if verbosity >= 2:
                        print 'Ensure unique index for', cls.__name__, field.name
                    cls.objects.ensure_index([(column, pymongo.DESCENDING)], unique=True, dropDups=True)
                else:
                    if verbosity >= 2:
                        print 'Ensure index for', cls.__name__, field.name                    
                    cls.objects.ensure_index([(column, pymongo.DESCENDING)])

    @classmethod
    def _requires_indexing(cls, verbosity=1):
        prevIndexes = cls.objects.index_information()
        newIndexes = {}

        key = u'_id_'
        item = {u'key':[(u'_id',1)], u'v':1}
        newIndexes.update({key:item})

        opt = cls._meta
        unique_together_index_name=('%s_%s' % (cls.__name__,'unique_together'))

        for unique_fields in opt.unique_together:
            if verbosity >= 2:
                print u'Ensure uniquer indexes for %s' % opt, unique_fields

            args = []

            for f in unique_fields:
                column = opt.get_field(f).get_attname_column()[1]
                args.append((u'%s'%column, pymongo.DESCENDING))

            item = {u'dropDups':True, u'key':args, u'unique':True, u'v':1}
            newIndexes.update({unique_together_index_name:item})


        for field in opt.fields:
            if field.db_index:
                column = field.get_attname_column()[1]
                if field.unique:
                    if verbosity >= 2:
                        print 'Ensure unique index for', cls.__name__, field.name
                    key = u'%s_%s' % (column, pymongo.DESCENDING)
                    item = {u'dropDups':True, u'key':[(u'%s'%column, pymongo.DESCENDING)], u'unique':True, u'v':1}
                    newIndexes.update({key:item})
                else:
                    if verbosity >= 2:
                        print 'Ensure index for', cls.__name__, field.name
                    key = u'%s_%s' % (column, pymongo.DESCENDING)
                    item = {u'key':[(u'%s'%column, pymongo.DESCENDING)], u'v':1}
                    newIndexes.update({key:item})

        if prevIndexes == newIndexes:
            return False
        return True



def post_syncdb_mongo_handler(**kwargs):
    """
    This handler should be added once if you have indexes in MongoModels:
    
    `models.signals.post_syncdb.connect(post_syncdb_mongo_handler)`
    """
    app = kwargs.get('app')
    for model in models.get_models(app):
        if issubclass(model, MongoModel):
            model.ensure_indexes(kwargs.get('verbosity'))
