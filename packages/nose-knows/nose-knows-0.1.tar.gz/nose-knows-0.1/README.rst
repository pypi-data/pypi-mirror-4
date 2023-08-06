==========
nose-knows
==========

**nose-knows** is a nose plugin for figuring out which unit tests you should
run after modifying code. It works by tracing your code while you run unit
tests, and creating an output file that can be used later.

Installing
==========

You can install **nose-knows** through ``pip`` or ``easy-install``::

    pip install nose-knows

Or you can download the `latest development version`_, which may
contain new features.

Using nose-knows
================

**nose-knows** can be invoked in either input or output mode. In output mode
(``--knows-out``) it will generate a ``.knows`` file that contains the mapping
from a file in your code tree to the set of unit tests that run it. In input
mode, it uses the ``.knows`` file to selectively run unit tests based on the
files you pass in.

Creating a ``.knows`` file::

    eyal-01575:src eyal$ nosetests --with-knows --knows-dir=$BASE_DIR --knows-out
    .....................................................................
    ----------------------------------------------------------------------
    Ran 62 tests in 0.444s

    OK

The ``.knows`` file now contains the following::

    warehouse/src/load_data/sql_utils/checkpoints.py:
        src.tests.test_load_data_statements:TestSQLStatement.test_finalize
        src.tests.test_load_data_checkpoints:TestCheckpoints.test_checkpoint_finalize_with_delete
        src.tests.test_load_data_checkpoints:TestCheckpoints.test_checkpoint_finalize
        src.tests.test_load_data_checkpoints:TestCheckpoints.test_checkpoint_with_previous_checkin
        src.tests.test_load_data_checkpoints:TestCheckpoints.test_checkpoint
        src.tests.test_load_data_statements:TestSQLStatement.test_to_sql_import
        src.tests.test_load_data_statements:TestSQLStatement.test_to_sql_schema_update

You can now run **nose-knows** in input mode, passing in
``load_data/sql_utils/checkpoints.py``::

    eyal-01575:src eyal$ nosetests --with-knows --knows-dir=$BASE_DIR load_data/sql_utils/checkpoints.py
    .......
    ----------------------------------------------------------------------
    Ran 7 tests in 0.003s

    OK

There is also (experimental at this point) support for py.test. You can
generate your ``.knows`` file via::

    eyal-01575:src eyal$ py.test --with-knows --knows-dir=$BASE_DIR --knows-out
    ===================== test session starts ======================
    platform darwin -- Python 2.7.1 -- pytest-2.3.4
    plugins: nose-knows
    collected 62 items

    tests/test_load_data_checkpoints.py ....
    tests/test_load_data_from_mysql.py ..
    tests/test_load_data_statements.py .....
    tests/test_process_data_denormalize.py ........
    tests/test_process_data_mapping.py .....
    tests/test_transform_data_daemon.py .
    tests/test_transform_data_table_follower.py .................
    tests/test_transformers/test_avg_data.py ..
    tests/test_transformers/test_count.py ...
    tests/test_transformers/test_join.py ....
    tests/test_transformers/test_json_data.py .....
    tests/test_transformers/test_min_data.py ..
    tests/test_transformers/test_std_data.py ..
    tests/test_transformers/test_sum_data.py ..

    ================== 62 passed in 2.18 seconds ===================

And selectively run specific unit tests like so::

    eyal-01575:src eyal$ py.test --with-knows --knows-dir=$BASE_DIR load_data/sql_utils/checkpoints.py
    ===================== test session starts ======================
    platform darwin -- Python 2.7.1 -- pytest-2.3.4
    plugins: nose-knows
    collected 62 items

    tests/test_load_data_checkpoints.py ....
    tests/test_load_data_statements.py ...

    =================== 7 passed in 0.30 seconds ===================

The best practice here is to have a system like Jenkins run the unit test suite
once in a while to create this map (we have it running daily), and then
creating a bash function/script to download the knows output file from Jenkins
and run it against the set of changed files from a commit. Ours looks like::

    function grab_latest_knows_output() {
        NOW=`date +%s`
        if [ ! -f $KNOWS_FILE_TMP ] ; then
            curl --compressed $KNOWS_FILE_URL > $KNOWS_FILE_TMP
        else
            KNOWS_FILE_AGE=`stat -c %Y $KNOWS_FILE_TMP`
            if [ `expr $NOW - $KNOWS_FILE_AGE` -gt "86400" ] ; then
                curl --compressed $KNOWS_FILE_URL > $KNOWS_FILE_TMP
            else
                echo "Using latest knows output file."
            fi
        fi
    }

    function test_changed() {
        grab_latest_knows_output
        nosetests $KNOWS_FLAGS `git diff --name-only --cached origin | xargs`
    }

    function run_tests_for() {
        grab_latest_knows_output
        nosetests $KNOWS_FLAGS $@
    }

License
========

**nose-knows** is copyright 2013 Eventbrite and Contributors, and is made
available under BSD-style license; see LICENSE for details.

.. _`latest development version`: https://github.com/eventbrite/nose-knows/tarball/master#egg=nose-nose
