How to run
==========

Cloning
-------
In order to run the example, please follow the next steps
1. Clone the repository
2. within the installation tree create a soft link from directory moma_django into moma_example/moma_django
3. Dependencies:
3.1 Make sure that you have mongodb installed and running (version 2.0.2)
3.2 Make sure that you have the following python modules installed: pymongo, bson, djangotoolbox (0.9.2)
4. Create the database
   ./manage.py syncdb
   Define an admin user in the process of the database creation

Run testing
-----------
5. Run tests:
   ./manage.py test testing
   Once the tests pass, you can validate that certain collections were created within mongodb. Use mongo console:
   show dbs;
   to validate that "test_momaexample" was created. Use that db:
   use test_momaexample;
   and validate that there are certain collections:
   show collections;
   This would produce testing_testmodel1, testing_testmodel2, testing_testmodel2, test_uniquevisit. Check the content using:
   db.testing_uniquevisit.find({"location.cr":"South Africa"})
   to get a single record of a visitor from South Africa, or visitor from New York city:
   db.testing_uniquevisit.find({"location.ct":"New York"})

Example application
-------------------
6. Run the example:
   ./manage.py runserver 8000
   Once connected to http://localhost:8000/ you can register, login add questions with media, vote for questions and
   review questions

