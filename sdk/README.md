This folder contains e2e example for registering and deploying models in Azure ML. 


The inference server is launched using the runit utility (runsvdir). There is also a sample run file within the docker subdirectory showing launching vllm OpenAI compliant API endpoint along with sample Dockerfile you can customize to build your custom image compatible with Azure ML managed inference endpoints. 
