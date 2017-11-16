# DummyProject
Most of the project is missing here, sorry. Will have to update soon. So far, check the [wiki](https://www.github.com/project11a/DummyProject/wiki) for intel.

## Installation
Installation of this thing is weird. Initial configs need to take place and things may need to be arranged in a way, which is nowhere documented. However, once it is copy-installed with configs included, no extra steps are required but few things may not be set up in a way you want it. Have a look at those specific parts to fix it.

## Usage
This software is designed to run as a service. It takes a "debug" argument which would do anything iirc. StdIn is useless and StdOut is a messy place.

To access it, use the configured interfaces. Obviously, the only graphical interfaces provided so far, are interactive web pages running on the http driver. So far the default address used to be [127.0.0.1:7505](http://127.0.0.1:7505/insight?app=system.gui.x.logon.Base&theme=access) (no SSL - use a reverse proxy?). The address may change in all terms (IP/hostname, port, path, url parameters). /insight is just a linker to an internal construct which has no default app. `system.gui.x.logon.Base` will bring you to a login screen (it's not yet really good) which allows to choose from all apps. It was also supposed to hold the suspension capability but it's not there yet. You can directly pass the desired app instead (`system.gui.x.desktop` for instance).  
*A small note here: the desktop is very limitted. You can start apps in the textfield (in the lower right corner).*
**Beware of needing websockets to use it**. Ajax and JSocket have been in (in an earlier "build") but we got over it.

Additional raw TCP interfaces:   
Most likely the **debug.sockets** service will be enabled as well in default setups (for now).  
It's running on **127.0.0.1:9345** by default.
