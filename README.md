# simple-slb
this is a simple saftware load balance client for nginx upstream module

## request
make sure that you os have install python<br>
install requied libs<br>
pip install flask<br>
pip install flask-sqlalchemy<br>
pip install flask-wtf<br>
pip install flask-bootstrap<br>

## setup
edit setup.py<br>
change the value of NGINX_CONFIG_DIR and NGINX_CONFIG_DIR<br>
python setup.py<br>

## apis
/api/pool/pool_name/addMember<br>
/api/pool/pool_name/delMember<br>
/api/pool/pool_name/deploy<br>
/api/pool/pool_name/clear<br>
/api/pool/pool_name/delete<br>
/api/pool/add<br>
/api/pool/delete<br>

