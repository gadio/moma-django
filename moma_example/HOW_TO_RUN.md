How to run
==========

Cloning
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

Run tests
-----------
1. `./manage.py test testing`
1. Once the tests pass, you can validate that certain collections were created within mongodb. Use mongo console:
   * `show dbs;`
1. To validate that "test_momaexample" was created. Use that db:
   * `use test_momaexample;`
1. Validate that there are certain collections:
   * `show collections;`
   * This would produce testing_testmodel1, testing_testmodel2, testing_testmodel2, test_uniquevisit.
1. Check the content using the following to get a single record of a visitor from South Africa:
   * `db.testing_uniquevisit.find({"location.cr":"South Africa"})`
1. To get to visitors from New York city:
   * `db.testing_uniquevisit.find({"location.ct":"New York"})`

Example application
-------------------
1. In order to run the example:
   * `./manage.py runserver 8000`
1. Once connected to http://localhost:8000/ you can register, login add questions with media, vote for questions and
   review questions

