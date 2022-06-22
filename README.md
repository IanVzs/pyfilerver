# pyfilerver
<p>
    <a href="https://pypi.org/project/pyfilerver/" target="_blank">
        <img src="https://img.shields.io/pypi/v/pyfilerver" />
    </a>
    <a href="https://github.com/IanVzs/pyfilerver/blob/main/.github/workflows/ci.yml" target="_blank">
        <img src="https://img.shields.io/github/workflow/status/ianvzs/pyfilerver/CI" />
    </a>
    <a href="https://app.codecov.io/gh/ianvzs/pyfilerver" target="_blank">
        <img src="https://img.shields.io/codecov/c/github/ianvzs/pyfilerver" />
    </a>
    <img src="https://img.shields.io/github/license/ianvzs/pyfilerver" />
    <a href="https://pepy.tech/project/pyfilerver" target="_blank">
        <img src="https://pepy.tech/badge/pyfilerver" />
    </a>
</p>

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
