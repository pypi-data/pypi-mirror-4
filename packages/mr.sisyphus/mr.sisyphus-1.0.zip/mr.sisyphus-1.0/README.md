mr.sisyphus
===========

*His pointless toil will never end.*

Mr. Sisyphus is a tool to improve the permissions for github organisations. It will allow users to create repositories without having to made admins of repositories. It requires an organisation in GitHub with three teams. 

* The Owners team is created by default
* A team that holds all the developers in the organisation, with Push and Pull rights set
* A new team for this package that has Push, Pull and Admin rights set.
 
This new team should **not** be administered by the organisation admins, they should just administer the Owners and Developers teams.

Usage
-----

You will need to customise the `mr.sisyphus.cfg` file with information about your organisation. A default is provided for the organisation `collective`. In this organisation the teams listed above are named, respectively:

* Owners
* --auto-contributors
* CanAdd

therefore the configuration file looks like::

    [sisyphus]
    organization = collective
    developer_team = --auto-contributors
    stub_team = CanAdd

The first time you run the script it will prompt for your GitHub username and password. The user you authenticate as **must** be a member of the Owners team in the organisation you want to administer. It will then create an OAuth token and store it in the mr.sisyphus.cfg file. From this point on the configuration file should be considered secret, as there is no way to get an OAuth token that applies just to one organisation. If someone finds this token they'd gain admin access to your private repos. The OAuth token can be disabled from your GitHub user profile, but you won't be prompted to log in again unless you delete it from the config file.

From this point on the script can be run in non-interactive mode

Dry Run
-------

To see what mr.sisyphus is planning to do invoke it as `./bin/mr.sisyphus.cfg -n` and it will skip making the actual calls to github.
