# simple-slb
This is a simple saftware load balance client for nginx upstream module

## Lib requests
make sure that you os have install python<br>
install requied libs<br>
pip install flask<br>
pip install flask-sqlalchemy<br>
pip install flask-wtf<br>
pip install flask-bootstrap<br>

## Apis
/api/pool/pool_name/addMember<br>
/api/pool/pool_name/delMember<br>
/api/pool/pool_name/deploy<br>
/api/pool/pool_name/clear<br>
/api/pool/pool_name/delete<br>
/api/pool/add<br>
/api/pool/delete<br>

## How to run
run bash restart.sh to start the server<br>
It will start gunicorn with port 8888<br>
Make sure you have permission to run nginx or you can run as root user<br>
go to http://127.0.0.1:8888/admin/config/edit and config the right value<br>
make sure that your nginx.conf has include the NGINX_CONFIG_DIR<br>
click the Deploy button at the right of navigation bar to reload the nginx config
