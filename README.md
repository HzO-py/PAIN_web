Welcome to the pain assessment website platform. It is established for doctors to make their assessments and to browse the dataset.
The web is running at http://for-safe.top:8001

Run the web in the server of for-safe.top:
source ~/miniconda3/bin/activate&&cd /hdd/sdb1/lzq/mofarm/projects&&source activate python36
cd /hdd/sdb1/lzq/PAIN/PAIN&&killall -9 uwsgi&&uwsgi --ini uwsgi.ini&&tail -f uwsgi_v2.log

Change the configuration file in PAIN/PAIN/uwsgi.ini
Change the backend interface in PAIN/patient/views.py
Change the mysqlModel file in PAIN/patient/models.py and run：
python manage.py migrate
python manage.py makemigrations
