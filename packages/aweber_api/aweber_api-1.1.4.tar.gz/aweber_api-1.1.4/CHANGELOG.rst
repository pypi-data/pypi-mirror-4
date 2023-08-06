Changelog
---------
2013-01-03: v1.1.4
  * Support version 1.0.17 of the API. (Broadcast Stats)
  * See https://labs.aweber.com/docs/changelog for details
  * See https://labs.aweber.com/snippets/campaigns for code snippets and documentation

2012-12-10: v1.1.3
  * Added a parameter to the Move Subscriber method for last followup message number sent.
    * to support version 1.0.16 of the API.  See https://labs.aweber.com/docs/changelog

2012-05-30: v1.1.2
  * Fixed SSL Certificate validation issue with httplib >= 0.7.0

 2011-10-04: v1.1.1
  * Fixed bug where __len__ returns a type error on empty collections returned from custom methods on collections or entries.

 2011-08-26: v1.1.0
  * Modified OAuthAdapter to raise an APIException when any API errors occur.
  * Added get_activity() method to return subscriber analytics activity.
  * Modified create() method to return the instance of the newly created Resource instead of true.
  * Modified create() method tests to be more generic.
  * Fixed bug in POST and GET where dictionaries and lists were not properly json serialized.
  * Fixed bug in find and findSubscribers methods when no matches are found by the api.
