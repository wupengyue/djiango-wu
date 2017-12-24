###django project repo ###
> app_docker is a docker manager platform 
> app_node is a server manager platform


###Tips ###
> we can use proxy to download pypi packages, i.e.:
 ```bash
    pip install django -i https://pypi.douban.com/simple
 ```

> dependence js css file are in package app_temple.zip
        

> ssh login with private key
  
 ```bash
     scp -p ~/.ssh/id_rsa.pub root@<remote_ip>:/root/.ssh/authorized_keys
 ```

# url map

>* administration:  http://127.0.0.1:8000/admin   user/password:admin/adminadmin



# how to start the project 

```
   source .venv/bin/activate
   python manage.py makemigrations 
   python manage.py migrate
   python manage.py sqlmigrate
   python manage.py createsuperuser
   
   python manage.py runserver
```
