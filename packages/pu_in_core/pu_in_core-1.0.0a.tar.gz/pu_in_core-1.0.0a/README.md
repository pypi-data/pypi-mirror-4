Python United Intranet Core
===========================

The PU core package offers JSON based views for Django to do inline
actions in your front-end, or in other words: actions that result only
in a small part of the page to be renewed to reflect the result of the
action. Think: 'make favorite', 'tweet', etc. To enable this behavior,
you can create a link in your html with the class "action-inline".

Action results can be sent to a specific target, either an element id,
or a jQuery expression. Callbacks are supported, appending to lists,
etc. Check the JS file for details.
