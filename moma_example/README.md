Example application
===================
About the application - moma_example
------------------------------------
The example application was developed (in part) to serve as a way for people participating in a lecture or a presentation to feed in questions
or vote on other people's questions. In addition a user the created a question can add any number of media files (currently
images, but it is very simple to extend this to voice, video or just arbitrary files). The application was designed to run
well on a smart phone and should allow taking pictures directly from the phone and uploading them.

The application is mostly a django application where the main model `data.models.Question` is a MongoModel. The question keeps
all question related info, including the text, the list of users that voted for it and the actual media files.

The `data.models.Question` model looks like this:

```python
class Question(MongoModel):
    user = models.ForeignKey(User)
    date = MongoDateTimeField(db_index=True)
    question = models.CharField(max_length=256 )
    docs = DictionaryField(models.CharField())
    image = DictionaryField(models.TextField())
    audio = DictionaryField()
    other = DictionaryField()
    vote_ids = ValuesField(models.IntegerField())
    def __unicode__(self):
        return u'%s[%s %s]' % (self.question, self.date, self.user, )
    class Meta:
        unique_together = ['user', 'question',]
        managed = False
```

Note the following:
* The class inherits from `MongoModel`, but otherwise looks very standard.
* New type of fields `DictionaryField` and `ValuesField` that holds some of the payload.


Using the application
---------------------
The application is simple and self explanatory. It offers a few basic operations:

1. login:

 ![login](http://i.imgur.com/O4A2pZ2.png)

1. Review questions:

 ![review questions](http://i.imgur.com/qz1MIFM.png)

1. Edit your question, vote and un-vote:

 ![edit your question, vote and un-vote](http://i.imgur.com/dW2Ygqo.png)

1. Review and edit question media:

 ![review and edit question media](http://i.imgur.com/cBuv0Z5.png)

The django admin
----------------
You would note that the django admin is working for view on top of the Question MongoModel:

 ![admin1](http://i.imgur.com/YC6M3ni.png)

 ![admin2](http://i.imgur.com/UPWpH7f.png)

Note however, that currently editing questions in the admin interface is not working as a result of missing forms (please
see the top readme file about contributing...)


How to run
==========

Option 1 - use the installed package
-------
This is the "simple option"

1. Following the installation, find your site-packages/moma_django-..... directory. Depending on how you installed it should look like /lib/python2.7/site-packages/moma_django-0.1.0-py2.7.egg/moma_example
2. Copy the moma_example directory into a temporary area
3. It is optional but recommended to run the tests at that point (see below)
4. Create the database:
   * python ./manage.py syncdb
   * Define an admin user in the process of the database creation
5. Run the server:
   * python ./manage.py runserver 8000
6. Use a web browser and point it to http://localhost:8000 to use the application


Option 2 - Cloning
-------
In order to run the example, please follow the next steps:

1. Clone the repository
2. within the installation tree create a soft link from directory moma_django into moma_example/moma_django
3. Dependencies:
4. Make sure that you have mongodb installed and running (version 2.0.2)
5. Make sure that you have the following python modules installed: pymongo, bson, djangotoolbox (0.9.2)
6. Create the database:
   * ./manage.py syncdb
   * Define an admin user in the process of the database creation
7. Run the server:
   * python ./manage.py runserver 8000
8. Use a web browser and point it to http://localhost:8000 to use the application


Run tests
-----------
1. In a terminal under moma_example, run `./manage.py test testing`
1. Once the tests pass, you can validate that certain collections were created within mongodb.
   * Use mongo console and run `show dbs;`
1. To validate that "test_momaexample" was created.
   * Use that db: `use test_momaexample;`
1. Validate that there are certain collections:
   * `show collections;`
   * This would produce testing_testmodel1, testing_testmodel2, testing_testmodel2, test_uniquevisit.
1. Check the content using the following to get a single record of a visitor from South Africa:
   * `db.testing_uniquevisit.find({"location.cr":"South Africa"})`
1. To find visitors from New York city:
   * `db.testing_uniquevisit.find({"location.ct":"New York"})`

Run the example
-----------
1. After cloning, in order to run the example:
   * `./manage.py runserver 8000`
1. Once connected to http://localhost:8000/ you can register, login add questions with media, vote for questions and
   review questions

More information
================
Presentation
------------
http://www.slideshare.net/GadiOren/moma-django-overviewshare

Video
-----
http://youtu.be/cxQKTDLjb-w
