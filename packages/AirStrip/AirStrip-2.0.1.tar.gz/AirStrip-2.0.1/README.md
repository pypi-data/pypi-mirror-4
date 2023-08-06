AirStrip.js
=============

About
-------------

This project is meant to ease dealing with third-party javascript dependencies in ambitious client-side web projects.

Conceptually, Airstrip has similarities with Twitter's Bower, and npm component (https://npmjs.org/package/component).

For the impatients
-------------

Read.


Problem
-------------

Modern javascript projects usually depend on numerous third-party libraries and frameworks 
(say: requirejs, handlebars, i18n, emberjs, jasmine).

Picking these, building, minifying, tracking versions, possibly patching or forking them, maintaining dependencies, then integrating into a project can quickly become borringly repetitive and tedious.

Solution
-------------

The idea here is to help do that, by providing tools to quickly assemble dependencies from numerous, widely used libraries, build them uniformly, list various versions, then "dispatching" the results in a build directory to be then used by said projects - and obviously tools that help you do that for your own libraries.


Installation
-------------

`pip install airstrip`
`pip install airstrip --upgrade`


API
-------------

Once the airstrip binary has been installed, you should cd to your project root source folder and may use the following commands.


Command:
```airstrip show ember```

Result:
  Details about EmberJS, and list of available versions


Command:
```airstrip require emberjs```

Result:
  Add emberjs (in version "master") to your project dependencies. This will create or update the project "airfile.json" listing said dependencies.

Command:
```airstrip require emberjs SOMEVERSION```

Result:
  Same as above, but explicitely require a specific version. The "master" version (eg: trunk) keywords should always exist for any library.
  Multiple different versions of the same library can be required.
  Note that requiring a project that depends on other projects will require them as well, in the recommended version (XXX, not done yet).

Command:
```airstrip remove emberjs```
```airstrip remove emberjs SOMEVERSION```

Result:
  Will remove the library from the project dependencies list, if present (possibly in the specified version).


Command:
```airstrip require```

Result:
  List currently required libraries for your project, along with versions.

Command:
```airstrip build```

Result:
  Build all required libraries for your project, and output them into a "dependencies" folder.

Command:
```airstrip build ember```

Result:
  Build, or rebuild only the specified library (that you requested).


Command:
```airstrip use```

Result:
  List configuration flags, possibly with their default value if overriden.


Command:
```airstrip use key value```

Result:
  Locally (to your project) override a specific configuration key.



API: risky, untested, undocumented, internal
-------------

Command:
```airstrip seed```

Result:
  Initialize a new project inside the current working directory, by adding a number of convenient boilerplates files.


Command:
```airstrip init owner repository```

Result:
  Initialize (or update) a formula from a project on github ("repository") whose owner is "owner". Will fetch tags and stuff like that.


Command:
```airstrip edit somelibrary```

Result:
  Edit an existing or create a new empty "formula" for a given library, locally to your project so you can add new library (XXX untested).

Command:
```airstrip edit somelibrary true```

Result:
  Edit an existing or create a new empty "formula" for a given library, globally for airstrip (XXX untested and not recommended).



License
-------------

MIT.



