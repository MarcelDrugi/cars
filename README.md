# CAR RENTAL
#### Pre-production. The application is in development (80% complete).
#### live: http://crrental.s3-website-eu-west-1.amazonaws.com
#### API doc: http://crental.pythonanywhere.com/redoc
## Running the application in development mode
#### To start the app, follow the steps below.
###### 1. Clone repo:

    git clone https://github.com/MarcelDrugi/cars

###### 2. Go to backend app directory and  create virtual environment:

    cd cars/backend/ && virtualenv venv

###### 3. Activate venv and install requirements:

    source venv/bin/activate && pip3 install -r  requirements.txt

###### 4. Create database for the project.
You can use any SQL management system, but you need to install it into venv.
From <i>requirements.txt</i> you have already installed mySQL-client. If you want to use it:

    mysql -u [your_username] -p

###### 5. Go to AWS website. 
###### Add a new IAM user to controll your bucket (create group for the user with built-in policy <u>AmazonS3FullAccess</u>).

<u>Remember the data</u>: <b>User</b>, <b>Access key ID</b>, <b>Secret access key</b>.

![Image of Yaktocat](https://hahahaxddd.s3-eu-west-1.amazonaws.com/iam.png)

###### 6. Create .env file in <i>/cars/backend/cars/config/settings</i> (the directory that contains settings files):

    touch cars/config/settings/.env

###### 7. To the .env file enter 7 groups of data:
<ol type="a">
   <li> some secret key, </li>
   <li> settings of the database you created in step 4,</li>
   <li> settings of IAM user you created in step 5,</li>
   <li> the name of the bucket you will create in the next step (the name must be unique in the region, so come up with something unique,</li>
   <li> name of the region where bucket will created (I recomend Ireland).</li>
   <li> name of empty-avatar file (look step 8), default value: <b>no-avatar.png</b>,</li>
   <li> frontend host addres, default value for Angular-CLI: <b>http://localhost:4200/</b></li>
</ol>


For mySQL-database and AWS-Ireland region the file should looks like:

    SECRET_KEY=your_secret_key
    
    ENGINE=django.db.backends.mysql
    DATABASE_NAME=name_of_created_databas
    DATABASE_USER=username
    DATABASE_PASSWORD=password
    
    AWS_ACCESS_KEY_ID=your_access_id
    AWS_SECRET_ACCESS_KEY=your_secret_key_id
    
    BUCKET_NAME=unique_bucket_name
    
    REGION_NAME=eu-west-1
    
    EMPTY_AVATAR=no-avatar.png
    
    FRONTEND_HOST=http://localhost:4200/
    

###### 8. Create new bucket
<ul>
<li>create a s3-bucket</li>
<li>set the policy of the bucket (set as public)</li> 
<li>upload default-avatar file to media directory in the bucket</li>
</ul>

These 3 things you can do by running a prepared script:

    python3 cars/aws_settings/bucket_policy.py

###### 9. Do migrate:

    python3 cars/manage.py migrate

###### 10. Create superuser:

    python3 cars/manage.py createsuperuser

###### 11. Run backend server: 

    python3 cars/manage.py runserver

###### 12. Go to admin panel, log in as superuser and create employy/customer accounts and assign it the permissions:

    car_rental | rights support | employee_permission  <- for employee
    car_rental | rights support | client_permission  <- for customer 

(Customer accounts can also be created from the app templates)

###### 13. Open a new terminal in the main cloned repo directory. Go to frontend app main directory and install dependencies:

    cd frontend/cars && npm install

###### 14. Run frontend localhost (you may need to use root for correct operation): 

    [sudo] ng serve

##### 15. The app should be launched at:

    http://localhost:4200/



### Main technologies and services used:
- Django 3,
- Django REST 3,
- MySQL,
- AWS s3 (boto3, django-storages),
- PayPal,
- Angular 9.
