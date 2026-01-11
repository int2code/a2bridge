
# A2Bridge

This is the A2bridge SDK project. You can use it to develop and run on the A2Bridge your own code.

If you want to experience more about how to use A2Bridge please refer to our User Guide: https://int2code.github.io/a2bridge/

If you want to order A2Bridge hardware please contact us at: sales@int2code.com 


# Clone and build 

The build works only under Linux or WSL. 



## Docker 
By default the project is setup to be build in the docker container. 

### Install configure docker:

```bash
sudo apt-get install docker.io
sudo groupadd docker
sudo usermod -aG docker ${USER}
```

***NOTE***: restart WSL afterwards

Check if the docker works correctly: 
```bash
docker run hello-world
```

### Build docker container 




To clone and build the project please 