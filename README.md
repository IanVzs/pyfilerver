# pyfilerver
python http file server

## Install & Run
### Source
```bash
git clone git@github.com:IanVzs/pyfilerver.git
cd pyfilerver
python pyfilerver/main.py 
```

### Pip
Make sure you have pip installed.

```bash
pip install pyfilerver
```
#### Local
```
git clone git@github.com:IanVzs/pyfilerver.git
cd pyfilerver
pip install .
pyfilerver
```

## Use
When the program is running, use the web browser to access `http://127.0.0.1:8000/`. You can see

![demo png](https://github.com/IanVzs/pyfilerver/blob/main/demo.png)

### Custom Port
```
pyfilerver 9000
```
So you will need access `http://127.0.0.1:9000/`, All just like `http.server`.