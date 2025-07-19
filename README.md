# Auto-sqlancer
A suite of automation scripts that streamline the sqlancer testing process.


## Minimum Requirements
- Python 3.7 or above
- Java 11 or above
- Docker

## Using Auto-sqlancer
### 1. Build Images
#### Build all DBMS images
```bash
python3 start.py build --dbms all 
```

- --dbms all: build all the database images


#### Build a single DBMS

```bash
python3 start.py build --dbms <dbms_name> 

```

- <dbms_name>: e.g., mysql, postgres, sqlite, etc.


- Example: 
```
python3 start.py build --dbms mysql 
```

#### Build sqlancer image
```bash
python3 start.py build --sqlancer
```

### 2. Test 
#### Test all DBMSs
```bash
python3 start.py test --dbms all [--cache]
```

- --dbms all: test all the databases

- --cache(optional): skip pulling/building Docker image

#### Test a single DBMS

```bash
python3 start.py test --dbms <dbms_name> --config <path/to/config.json> [--cache]

```

- <dbms_name>: e.g., mysql, postgres, sqlite, etc.

- --config: Path to the config file for the selected DBMS.

- Example: 
```
python3 start.py test --dbms mysql --config mysql/config.json
```

#### Test a Custom Dockerfile-Based DBMS Container
```bash
python3 start.py test --dockerfile <path/to/Dockerfile> --config <path/to/config.json> [--cache]
```

- --dockerfile: Path to the custom Dockerfile to build the DBMS image.

- --config: Path to the DBMS config file.

- Example: 
```
python3 start.py test --dockerfile ./Dockerfile --config ./config.json
```