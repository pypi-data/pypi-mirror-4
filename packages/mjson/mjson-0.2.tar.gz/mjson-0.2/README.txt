=====
mjson
=====

Extended "python -mjson.tool".

::

   $ echo '{"a":1,"b",2}' | python -mmjson.tool  # Same the original
   {
       "a": 1, 
       "b": 2
   }
   $ echo '{"a":1,"b",2}' | python -mmjson.tool -i 2  # Indent
   {
     "a": 1, 
     "b": 2
   }
