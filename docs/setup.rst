#####
Setup
#####

To create a new project run:

.. code-block:: bash

    $ cookiecutter gh:douglasdaly/cookiecutter-blog-post

Follow the prompts to fill in the relevant information about your new
post:

project_name:
    The name of the project/post to create.

repo_name:
    The repository name to use for this new post.

project_location:
    The absolute or relative location to the main project folder.

media_location:
    The location relative to the ``project_location`` where the media
    files can be found.

post_icon_image:
    The name of the post's icon image file to use (place this file in
    the local post's ``media`` folder.

asset_prefix:
    String to prefix all assets used in the post with when uploading
    to the site.

python_interpreter:
    Python interpreter to use on the local system.

package_manager:
    Package manager to use on the local system.

Once you've done this you're ready to get to work on your new blog post!
You can find the initial (blank-ish) ``post.md`` file in the ``posts``
directory.
