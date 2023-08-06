0.0.5
-----

* Break compatibility with 0.0.4 as ``register_document`` does not generate
  indexes anymore;
* Add ``generate_index`` function;
* Break apart Connection classes:
** ``MongoConnection`` is not anymore tied to a single databases;
** ``SingleDbCOnnection`` is tied to a single database;
* Add an example used for documenting and functional testing.

0.0.4
-----

* registering document ensures index are created.


0.0.0
-----

*  Initial version
