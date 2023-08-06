
User authentication and authorization
=====================================

Registration
------------

An unidentified (anonymous) user of the site is always (in every page of the
site) presented with 2 links, labelled "Sign up" and "Sign in".

The *Sign up* leads the user to a registration form. In this form, the user
has to fill in a username, an email address, a password, and a captcha (from
`recaptcha <http://www.google.com/recaptcha>`_). All fields are required. The
username is validated to ensure that it is unique within the system, and
obviously the captcha is also validated. The user also needs to agree with
the terms of use of this PEER instance.

Once the user submits a valid registration form, the system sends an email to
the address entered in the form, containing a link to a confirmation page
within the site. Only when the user follows this link and visits the
confirmation page, is her account activated.

Authentication
--------------

If a user has an active account on the site, she can log in to the site,
following the *Sign in* link mentioned above and filling in her username and
password in the presented form. Once identified, the *Sign up* and *Sign in*
links disappear, and are replaced by one labelled "Logout" and another
labelled with the user's full name (or username if the full name is not
available). Following the *Logout* link invalidates the authentication
tokens produced through signing in, so that the user becomes anonymous once
again.

In the case the user forgets her password, there is a link named *Forgot
Password?* in the *Sign in* page which takes the user through the process of
resetting her password. Firstly, the user is asked to type the email address
in her personal information. Once the email address is submitted, an email is
sent to such address with a unique URL that is only known to the receiver of
the email. Clicking in such link takes the user to another form where she can
set her new password. From this point the process follows the normal
`Registration`_ procedure.

.. note::
  If the user doesn't remember the email address in her personal information,
  there is no way to recover the password through this process. She'll have to
  contact the system administrator so that he can reset her password.

User profile
------------

The identified user can follow the link labelled with her username, to view
her user profile. In that page she will see a list of her domains and
entities, and a user's menu with a few links:

* **Add domain** will take her to a form that she can use to add new domains.
* **Add entity** will take her to a form that she can use to add new
  entities.
* **Personal information** will take her to a form where she can change her
  email and her password, and can also enter a first and a last name. Her
  full name is the combination of her first and last names.

  .. note::
    If the user changes her email address, she has to ensure that she has
    access to the new email address, otherwise she won't be able to recover
    her password in case she forgets it.

* **Change password** will take her to a form that will allow her to change
  her password. In this form she will be required to enter her old password,
  and (twice) her new password. If the old password is correct, and the new
  password is identical both times she enters it, her password will be
  updated.
* **Invite friend** will take her to a form that will allow her to invite
  people to sign up at this PEER site. In this form she has to enter the
  email address of the person she wants to invite, and can also edit the
  email's body text offered by default. Clicking on *send invitation* will
  immediately send an email to the given address.
* **Manage admin team** is an option only available to administrator users.
  It will take the administrator user to a form where she will be able
  to add and remove other users from the administrator team.

Authorization
-------------

There are 3 types of users in the system: administrators, regular users, and
anonymous users. Administrators are authorized to do anything that the other
2 types of users are, and regular users can do anything that an anonymous
user can (except, of course, signing up).

* **Administrator users**. Users of this type can access the *django admin
  interface*, and through this interface they can manage other users'
  accounts (create, modify and delete them). Administrators has other special
  powers in the PEER interface:

  * They can create entities and assign another user as its owner.
  * They can add and remove regular users to the administrators team. Once
    a user becomes and administrator she has full powers and can add (and
    remove!)  other users to the administrators team.
  * They can validate domains directly without proving they are their
    legitimate owners.
  * They can set other users as members of a domain team, allowing them
    to use such domain like they were its owners.

  As you can see being an administrator users mean having a lot of powers.
  Remember that with great powers comes great responsibilities.
* **Regular users**. These users can create entities, of which they become
  owners. They can also assign ownership of their own entities to another
  user (thereby relinquishing ownership themselves), and delegate management
  of their entities to (sets of) other users. An entity can only have one
  owner, that can delegate the management of it to any number of other users.
* **Anonymous users**. These users can retrieve entities (there are no
  private entities).

So, to modify or remove an entity, a user has to be either its owner, an
administrator, or a delegate manager for it. Anybody can retrieve entities.
