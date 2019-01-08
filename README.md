# AquaDB Lambda
An AWS lambda function.

###  Environement Setup:

```shell
pip install -U -r requirements.txt -t ./
```

### Packaging

```shell
zip -r ../aquadb-0.0.6.zip .
```

### Installation in AWS Lambda
In the aws account, replace the existing code for the 'AquaDBToElasticsearch' lambda
function with the newly created zip file and click 'Save'.

