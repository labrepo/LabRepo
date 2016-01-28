Install
=======


Getting started
--------
Labpepo is a complicated software which uses a lot of dependencies, such as ElasticSearch, Nginx or Gulp. So we recommend to use Ansible to install Labrepo in one command.

First you should install Ansible_.
Next, you should fill hosts file in the deploy/ansible directory. You can use hosts.example file as the example.

Next, fill your enviroment settings in group_vars directory. You can use production.example file as the example.

Deploy::

    cd deploy/ansible
    ansible-playbook  -i hosts labrepo.yml






.. _Ansible: http://docs.ansible.com/ansible/index.html