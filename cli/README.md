## Azure CLI sample to deploy a model and a Gradio App in Azure ML Online Endpoint

### Pre-requisite

* You have an existing Azure subscription and an Azure ML Workspace and have contributor access
* You have the latest Azure CLI and Azure ML extension to CLI installed
* You have set the workspace as the default for the Azure CLI on your local machine. You can do this by running:
```bash
az configure --defaults group=<your-resource-group> workspace=<your-workspace-name> subscription=<your-subscription-id>
```
### Preparation
We will build a Docker image locally which will be used as the environment to run the model and the gradio app. The Dockerfile is provided under the "docker" subdirectory. The subdirectory also has the entrypoint.sh script that starts a VLLM server in background and a basic chatbot Gradio app also packaged in the docker image. 

We will then register the image in the container registry associated with the Azure ML workspace

The steps are:
```
cd docker
docker build -t <your-image-name> . 
docker acr login -n <your-container-registry-name>
docker push <your-container-registry-name>.azurecr.io/<your-image-name>
cd ..
```

### Deployment

1. Create an Online Endpoint
```bash
az ml online-endpoint create -f endpoint.yml
```

2. Create a Online Deployment
You have to edit the deployment.yml file and update the desired model on Huggingface you want to deploy and the container image you just built.

NOTE: In this example we will not register the model in Azure ML and instead the VLLM server will download directly from Huggingface. See the SDK example in this example for a model reistered in the AzureML.

```bash
az ml online-deployment create -f deployment.yml
```
The Azure ML Scoring URI is pointed at the Gradio App port (7860) in this YAML file. The VLLM is not exposed directly. The Gradio app accesses the VLLM inference server via localhost using the OpenAI Python API. 

3. You can access the Gradio Endpoint from your machine. You do need a local proxy as you need to pass the authentication key in the HTTP header. 

Here is a simple node.js proxy server that you can run locally to access the Gradio app:
```javascript
// proxy-server.js
const express = require('express');
const request = require('request');
const app = express();

// You can find the endpoint and key on Azure ML Portal under your workspace and endpoints -> Consume tab
const GRADIO_ENDPOINT = 'YOUR AZURE ML ENDPOINT URL';
const API_KEY = 'YOUR AZURE ML API KEY';

app.use('/', (req, res) => {
  const url = `${GRADIO_ENDPOINT}${req.url}`;
  req.pipe(request({ url, headers: { 'Authorization': `Bearer ${API_KEY}` } })).pipe(res);
});

app.listen(3000, () => console.log('Proxy running on http://localhost:3000'));
```

You can point your browser to `http://localhost:3000` to access the Gradio app. 

### Acknowledgements
This recipe derives a lot of prior examples and especially the wonderful [blog](https://clemenssiebler.com/posts/vllm-on-azure-machine-learning-managed-online-endpoints-deployment/) and repo by Clemens Siebler.

### Limitations
Running Gradio in Online endpoint is not officially supported. This examples demostrates it is possible to run a Gradio app in an Azure ML Online Endpoint, but it may not be suitable for production use and has not been extensively tested. 

