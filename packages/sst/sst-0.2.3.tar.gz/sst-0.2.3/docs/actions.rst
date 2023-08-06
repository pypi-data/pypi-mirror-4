
=========================
 SST - Actions Reference
=========================

Tests are comprised of Python scripts. Files whose names begin with an
underscore will *not* be executed as test scripts.

Test scripts drive the browser with Selenium WebDriver by importing and
using SST actions.

The standard set of actions are imported by starting the test scripts with::

    from sst.actions import *


Actions that work on page elements take either an element id or an
element object as their first argument. If the element you are working with
doesn't have a specific id you can get the element object with the
`get_element` action. `get_element` allows you to find an element by its
id, tag, text, class or other attributes. See the `get_element` documentation.


----------------
    Actions:
----------------



accept_alert
------------

::

   accept_alert(expected_text=None, text_to_write=None)

Accept a JavaScript alert, confirmation or prompt.

Optionally, it takes the expected text of the Popup box to check it,
and the text to write in the prompt.

Note that the action that opens the alert should not wait for a page with
a body element. This means that you should call functions like
click_element with the argument wait=Fase.

add_cleanup
-----------

::

   add_cleanup(func, *args, **kwargs)

Add a function, with arguments, to be called when the test is
completed. Functions added are called on a LIFO basis and are
called on test failure or success.

They allow a test to clean up after itself.


assert_attribute
----------------

::

   assert_attribute(id_or_elem, attribute, value, regex=False)

assert that the specified `attribute` on the element is equal to the
`value`.

If `regex` is True (default is False) then the value will be compared to
the attribute using a regular expression search.


assert_button
-------------

::

   assert_button(id_or_elem)

Assert that the specified element is a button.

Takes an id or an element object.
Raises a failure exception if the element specified doesn't exist or isn't
a button

assert_checkbox
---------------

::

   assert_checkbox(id_or_elem)

Assert that the element is a checkbox.

Takes an id or an element object.
Raises a failure exception if the element specified doesn't exist or isn't
a checkbox.

assert_checkbox_value
---------------------

::

   assert_checkbox_value(id_or_elem, value)

Assert checkbox value. Takes an element id or object plus either True or
False. Raises a failure exception if the element specified doesn't exist
or isn't a checkbox.

assert_css_property
-------------------

::

   assert_css_property(id_or_elem, property, value, regex=False)

assert that the specified `css property` on the element is equal to the
`value`.

If `regex` is True (default is False) then the value will be compared to
the property using a regular expression search.


assert_displayed
----------------

::

   assert_displayed(id_or_elem)

Assert that the element is displayed.

Takes an id or an element object.
Raises a failure exception if the element specified doesn't exist or isn't
displayed. Returns the element if it is displayed.

assert_dropdown
---------------

::

   assert_dropdown(id_or_elem)

Assert the specified element is a select drop-list.

assert_dropdown_value
---------------------

::

   assert_dropdown_value(id_or_elem, text_in)

Assert the specified select drop-list is set to the specified value.

assert_element
--------------

::

   assert_element(tag=None, css_class=None, id=None, text=None, text_regex=None, **kwargs)

Assert an element exists by any of several attributes.

You can specify as many or as few attributes as you like.

assert_equal
------------

::

   assert_equal(first, second)

Assert two objects are equal.

assert_link
-----------

::

   assert_link(id_or_elem)

Assert that the element is a link.

Raises a failure exception if the element specified doesn't exist or
isn't a link

assert_not_equal
----------------

::

   assert_not_equal(first, second)

Assert two objects are not equal.

assert_radio
------------

::

   assert_radio(id_or_elem)

Assert the specified element is a radio button.

Takes an id or an element object.
Raises a failure exception if the element specified doesn't exist or isn't
a radio button

assert_radio_value
------------------

::

   assert_radio_value(id_or_elem, value)

Assert the specified element is a radio button with the specified value;
True for selected and False for unselected.

Takes an id or an element object.
Raises a failure exception if the element specified doesn't exist or isn't
a radio button

assert_table_has_rows
---------------------

::

   assert_table_has_rows(id_or_elem, num_rows)

Assert the specified table has the specified number of rows (<tr> tags
inside the <tbody>).


assert_table_headers
--------------------

::

   assert_table_headers(id_or_elem, headers)

Assert table `id_or_elem` has headers (<th> tags) where the text matches
the sequence `headers`.


assert_table_row_contains_text
------------------------------

::

   assert_table_row_contains_text(id_or_elem, row, contents, regex=False)

Assert the specified row (starting from 0) in the specified table
contains the specified contents.

contents should be a sequence of strings, where each string is the same
as the text of the corresponding column.

If `regex` is True (the default is False) then each cell is checked
with a regular expression search.

The row will be looked for inside the <tbody>, to check headers use
`assert_table_headers`.


assert_text
-----------

::

   assert_text(id_or_elem, text)

Assert the specified element text is as specified.

Raises a failure exception if the element specified doesn't exist or isn't
as specified

assert_text_contains
--------------------

::

   assert_text_contains(id_or_elem, text, regex=False)

Assert the specified element contains the specified text.

set `regex=True` to use a regex pattern.

assert_textfield
----------------

::

   assert_textfield(id_or_elem)

Assert that the element is a textfield, textarea or password box.

Takes an id or an element object.
Raises a failure exception if the element specified doesn't exist
or isn't a textfield.

assert_title
------------

::

   assert_title(title)

Assert the page title is as specified.

assert_title_contains
---------------------

::

   assert_title_contains(text, regex=False)

Assert the page title contains the specified text.

set `regex=True` to use a regex pattern.

assert_url
----------

::

   assert_url(url)

Assert the current url is as specified. Can be an absolute url or
relative to the base url.

assert_url_contains
-------------------

::

   assert_url_contains(text, regex=False)

Assert the current url contains the specified text.

set `regex=True` to use a regex pattern.

assert_url_network_location
---------------------------

::

   assert_url_network_location(netloc)

Assert the current url's network location is as specified.

    `netloc` is a string containing 'domain:port'.
    In the case of port 80, `netloc` may contain domain only.

check_flags
-----------

::

   check_flags(*args)

A test will only run if all the flags passed to this action were supplied
at the command line. If a required flag is missing the test is skipped.

Flags are case-insensitive.


clear_cookies
-------------

::

   clear_cookies()

Clear the cookies of current session.

click_button
------------

::

   click_button(id_or_elem, wait=True)

Click the specified button.

By default this action will wait until a page with a body element is
available after the click. You can switch off this behaviour by passing
`wait=False`.

click_element
-------------

::

   click_element(id_or_elem, wait=True)

Click on an element of any kind not specific to links or buttons.

By default this action will wait until a page with a body element is
available after the click. You can switch off this behaviour by passing
`wait=False`.

click_link
----------

::

   click_link(id_or_elem, check=False, wait=True)

Click the specified link. As some links do redirects the location you end
up at is not checked by default. If you pass in `check=True` then this
action asserts that the resulting url is the link url.

By default this action will wait until a page with a body element is
available after the click. You can switch off this behaviour by passing
`wait=False`.

close_window
------------

::

   close_window()

Closes the current window 

debug
-----

::

   debug()

Start the debugger, a shortcut for `pdb.set_trace()`.

dismiss_alert
-------------

::

   dismiss_alert(expected_text=None, text_to_write=None)

Dismiss a JavaScript alert.

Optionally, it takes the expected text of the Popup box to check it.,
and the text to write in the prompt.

Note that the action that opens the alert should not wait for a page with
a body element. This means that you should call functions like
click_element with the argument wait=Fase.

end_test
--------

::

   end_test()

If called it ends the test. Can be used conditionally to exit a
test under certain conditions.

execute_script
--------------

::

   execute_script(script, *args)

Executes JavaScript in the context of the currently selected
frame or window.

Within the script, use `document` to refer to the current document.

For example::

    execute_script('document.title = "New Title"')

args will be made available to the script if given.


exists_element
--------------

::

   exists_element(tag=None, css_class=None, id=None, text=None, text_regex=None, **kwargs)

This function will find if an element exists by any of several
attributes. It returns True if the element is found or False
if it can't be found.

You can specify as many or as few attributes as you like.

fails
-----

::

   fails(action, *args, **kwargs)

This action is particularly useful for *testing* other actions, by
checking that they fail when they should do. `fails` takes a function
(usually an action) and any arguments and keyword arguments to call the
function with. If calling the function raises an AssertionError then
`fails` succeeds. If the function does *not* raise an AssertionError then
this action raises the appropriate failure exception. Alll other
exceptions will be propagated normally.

get_argument
------------

::

   get_argument(name, default=default)

Get an argument from the one the test was called with.

    A test is called with arguments when it is executed by
    the `run_test`. You can optionally provide a default value
    that will be used if the argument is not set. If you don't
    provide a default value and the argument is missing an
    exception will be raised.


get_base_url
------------

::

   get_base_url()

Return the base url used by `go_to`.

get_cookies
-----------

::

   get_cookies()

Gets the cookies of current session (set of dicts).

get_current_url
---------------

::

   get_current_url()

Gets the URL of the current page.

get_element
-----------

::

   get_element(tag=None, css_class=None, id=None, text=None, text_regex=None, **kwargs)

This function will find and return an element by any of several
attributes. If the element cannot be found from the attributes you
provide, or the attributes match more than one element, the call will fail
with an exception.

Finding elements is useful for checking that the element exists, and also
for passing to other actions that work with element objects.

You can specify as many or as few attributes as you like, so long as they
uniquely identify one element.

`text_regex` finds elements by doing a regular expression search against
the text of elements. It cannot be used in conjunction with the `text`
argument and cannot be the *only* argument to find elements.

get_element_by_css
------------------

::

   get_element_by_css(selector)

Find an element by css selector.

get_element_by_xpath
--------------------

::

   get_element_by_xpath(selector)

Find an element by xpath.

get_element_source
------------------

::

   get_element_source(id_or_elem)

Gets the innerHTML source of an element.

get_elements
------------

::

   get_elements(tag=None, css_class=None, id=None, text=None, text_regex=None, **kwargs)

This function will find and return all matching elements by any of several
attributes. If the elements cannot be found from the attributes you
provide, the call will fail with an exception.

You can specify as many or as few attributes as you like.

`text_regex` finds elements by doing a regular expression search against
the text of elements. It cannot be used in conjunction with the `text`
argument and cannot be the *only* argument to find elements.

get_elements_by_css
-------------------

::

   get_elements_by_css(selector)

Find all elements that match a css selector.

get_elements_by_xpath
---------------------

::

   get_elements_by_xpath(selector)

Find all elements that match an xpath.

get_link_url
------------

::

   get_link_url(id_or_elem)

Return the URL from a link.

get_page_source
---------------

::

   get_page_source()

Gets the source of the current page.

get_wait_timeout
----------------

::

   get_wait_timeout()

Get the timeout, in seconds, used by `wait_for`.

get_window_size
---------------

::

   get_window_size()

Get the current window size (width, height) in pixels.

go_back
-------

::

   go_back(wait=True)

Go one step backward in the browser history.

By default this action will wait until a page with a body element is
available after the click. You can switch off this behaviour by passing
`wait=False`.

go_to
-----

::

   go_to(url='', wait=True)

Go to a specific URL. If the url provided is a relative url it will be
added to the base url. You can change the base url for the test with
`set_base_url`.

By default this action will wait until a page with a body element is
available after the click. You can switch off this behaviour by passing
`wait=False`.


refresh
-------

::

   refresh(wait=True)

Refresh the current page.

By default this action will wait until a page with a body element is
available after the click. You can switch off this behaviour by passing
`wait=False`.


reset_base_url
--------------

::

   reset_base_url()

Restore the base url to the default. This is called automatically for
you when a test script completes.

retry_on_stale_element
----------------------

::

   retry_on_stale_element(func)

Decorate ``func`` so StaleElementReferenceException triggers a retry.

    ``func`` is retried only once.

    selenium sometimes raises StaleElementReferenceException which leads to
    spurious failures. In those cases, using this decorator will retry the
    function once and avoid the spurious failure. This is a work-around until
    selenium is properly fixed and should not be abused (or there is a
    significant risk to hide bugs in the user scripts).


run_test
--------

::

   run_test(name, **kwargs)

Execute a named test, with the specified arguments.

Arguments can be retrieved by the test with `get_argument`.

The `name` is the test file name without the '.py'.

You can specify tests in an alternative directory with
relative path syntax. e.g.::

    run_test('subdir/foo', spam='eggs')

Tests can return a result by setting the name `RESULT`
in the test.

Tests are executed with the same browser (and browser
session) as the test calling `test_run`. This includes
whether or not Javascript is enabled.

Before the test is called the timeout and base url are
reset, but will be restored to their orginal value
when `run_test` returns.

save_page_source
----------------

::

   save_page_source(filename='pagedump.html', add_timestamp=True)

Save the source of the currently opened page.
Called automatically on failures when running `-s` mode.

Return the path to the saved file.


set_base_url
------------

::

   set_base_url(url)

Set the url used for relative arguments to the `go_to` action.

set_checkbox_value
------------------

::

   set_checkbox_value(id_or_elem, new_value)

Set a checkbox to a specific value, either True or False. Raises a failure
exception if the element specified doesn't exist or isn't a checkbox.

set_dropdown_value
------------------

::

   set_dropdown_value(id_or_elem, text=None, value=None)

Set the select drop-list to a text or value specified.

set_radio_value
---------------

::

   set_radio_value(id_or_elem)

Select the specified radio button.

set_wait_timeout
----------------

::

   set_wait_timeout(timeout, poll=None)

Set the timeout, in seconds, used by `wait_for`. The default at the start
of a test is always 10 seconds.

The optional second argument, is how long (in seconds) `wait_for` should
wait in between checking its condition (the poll frequency). The default
at the start of a test is always 0.1 seconds.

set_window_size
---------------

::

   set_window_size(width, height)

Resize the current window (width, height) in pixels.

simulate_keys
-------------

::

   simulate_keys(id_or_elem, key_to_press)

Simulate key sent to specified element.
(available keys located in `selenium/webdriver/common/keys.py`)

e.g.::

    simulate_keys('text_1', 'BACK_SPACE')



skip
----

::

   skip(reason='')

Skip the test. Unlike `end_test` a skipped test will be reported
as a skip rather than a pass.

sleep
-----

::

   sleep(secs)

Delay execution for the given number of seconds.

    The argument may be a floating point number for subsecond precision.


switch_to_frame
---------------

::

   switch_to_frame(index_or_name=None)

Switch focus to the specified frame (by index or name).

if no frame is given, switch focus to the default content frame.

switch_to_window
----------------

::

   switch_to_window(index_or_name=None)

Switch focus to the specified window (by index or name).

if no window is given, switch focus to the default window.

take_screenshot
---------------

::

   take_screenshot(filename='screenshot.png', add_timestamp=True)

Take a screenshot of the browser window. Called automatically on failures
when running in `-s` mode.

Return the path to the saved screenshot.

toggle_checkbox
---------------

::

   toggle_checkbox(id_or_elem)

Toggle the checkbox value. Takes an element id or object. Raises a failure
exception if the element specified doesn't exist or isn't a checkbox.

wait_for_and_refresh
--------------------

::

   wait_for_and_refresh(condition, *args, **kwargs)

Wait for an action to pass. Useful for checking the results of actions
that may take some time to complete. The difference to wait_for() is, that
wait_for_and_refresh() refresh the current page with refresh() after every
condition check.

This action takes a condition function and any arguments it should be
called with. The condition function can either be an action or a function
that returns True for success and False for failure. For example::

    wait_for_and_refresh(assert_title, 'Some page title')

If the specified condition does not become true within 10 seconds then
`wait_for_and_refresh` fails.

You can set the timeout for `wait_for_and_refresh` by calling
`set_wait_timeout`.


write_textfield
---------------

::

   write_textfield(id_or_elem, new_text, check=True, clear=True)

Set the specified text into the textfield. If the text fails to write (the
textfield contents after writing are different to the specified text) this
function will fail. You can switch off the checking by passing
`check=False`.  The field is cleared before written to. You can switch this
off by passing `clear=False`.

