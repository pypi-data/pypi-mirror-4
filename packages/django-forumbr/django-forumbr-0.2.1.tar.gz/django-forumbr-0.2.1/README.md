Django ForumBR
==============
Django-forumbr is a project to create a simple, easy-to-use and complete forum
for django projects on the run.

Install instructions
====================
pip install django-forumbr

# then add forum to your settings INSTALLED_APPS
# and url(r'^forum/', include('forum.urls', namespace='forum')) to your urls.py

# create the models and you're done
python manage.py syncdb 