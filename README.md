[MoMa-Django](http://twitter.github.com/gadio/moma-django)
=================

MoMa-Django is a Mongo Manager for Django. It provides native Django ORM support for Mongo DB.

MoMa-Django provides a framework to bridge between a SQL DB and the NonSQL MongoDB using a simple and powerful framework allowing an application to have models both on SQL database *and* on Mongo, and a quick experimentation / migration path from SQL only to a mixed model. Created and maintained by [Gadi Oren](http://twitter.com/gadioren), as a part of the [Lucidel](http://lucidel.com) product.


Features
--------
* Adoption: changing a model to reside on MongoDB is as simple as changing the inheritance from django.db.models.Model to MongoModel!
* Model features: large subset of the model capabilities is supported (e.g. unique together)
* Enhanced model: Mongo models can include lists and dictionaries as a field
* Django administration: most of the administration functions are supported for Mongo based models
* Testing: support the creation of an alternative mongodb collection for unit tests
* Relationships between models on SQL db and Mongo: limited support. ForeignKeys can be defined but transactions or cascading delete is not supported
* Django query: support for queries (e.g. `date__gte` notation) as well as Q statements. Not supported yet: annotations and aggregations
* Enhanced Django query: queries can include "drill into" objects. E.g. for a record `entry = {a:3, b:{k1:4, k2:3,km:'a'}}` you can query: `qs = Entry.objects.filter(a__gte=2,b__km__regexp='^a$') )` (note the `b__km__regexp` "drill into")


Why?
----
There are other packages out there that create tight integration between MongoDB and django. **Why use this one?**
This package was originally created as a part of very careful experimentation with MongoDB, and developed in small increments. The reason was
that we couldn't afford a radical change like replacing the entire Django or moving completely to a NoSQL type of environment.
This package allowed us to enjoy both worlds without massive impact on the project. It is used in production, as part of a high scale & performance project.
If that is the type of decision and constraints that you are facing, this package may be a good option.


Dependencies
------------
* Django 1.4.1
* PyMongo 2.1.1
* djangotoolbox 0.9.2


Quick start
-----------

Clone the repo, `git clone git://github.com/gadio/moma-django.git`, [download the latest release](https://github.com/).



Versioning
----------

Releases will be numbered with the following format:

`<major>.<minor>.<patch>`

And constructed with the following guidelines:

* Breaking backward compatibility bumps the major (and resets the minor and patch)
* New additions without breaking backward compatibility bumps the minor (and resets the patch)
* Bug fixes and misc changes bumps the patch



Bug tracker
-----------

Have a bug? Please create an issue here on GitHub that conforms with [the guidelines](https://github.com/).

https://github.com/gadio/moma-django/issues



Twitter account
---------------

Please follow us on Twitter, [@lucidinsights](http://twitter.com/lucidinsights).
Keep up to date on announcements and more by following Gadi on Twitter, [@gadioren](http://twitter.com/gadioren).



Blog
----

Lucidel blog can be found [here](http://blog.lucidel.com).
Read more detailed announcements, discussions, and more on [The Official Blog](http://blog.gadioren.com).



Mailing list
------------

Have a question? Ask on our mailing list!



Developers
----------

How to test: TBD



Contributing
------------

Please submit all pull requests against *-wip branches. When relevant, you must include relevant unit tests. Thanks!



Authors
-------

**Gadi Oren**

+ http://twitter.com/gadioren
+ http://github.com/gadio

Additional contributor https://github.com/Alerion (as part of a contract position with Lucidel)


Copyright and license
---------------------

Copyright 2012 Lucidel, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this work except in compliance with the License.
You may obtain a copy of the License in the LICENSE file, or at:

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
