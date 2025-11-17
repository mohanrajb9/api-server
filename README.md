=======================================================================
                                                                                             
    A simple HTTP web server API that interacts with the GitHub API and
    responds to requests on /<USER> with a list of the user’s publicly available Gists        
                                                                                              
=======================================================================
### Requirements.
- docker
- python 3.8+

## Build and Run with Docker.

### Clone the repository.
```
git clone https://github.com/EqualExperts-Assignments/equal-experts-cooperative-stable-friendly-assistance-c00ec87c32d4.git
cd equal-experts-cooperative-stable-friendly-assistance-c00ec87c32d4
```

### Build the Docker image.
```
docker build -t gist-app .
```

### Run the container.
```
docker run -rm -p 8080:8080 --name gist-app-container gist-app
```

### Accessing the application.
```
http://localhost:8080/<USER>
```
or

```
http://localhost:8080/<USER>?page=<num> — page key is optional
```


###  Run tests.

### 1.venv setup(optional).
#### Create and Activate a Virtual Environment.
```
python -m venv venv
```
#####  On Windows:
```
venv\Scripts\activate
```
##### On macOS/Linux:
```
source venv/bin/activate
```


### 2.Install the Project and dependencies.
```
pip install -e .
pip install -r requirements.text
```

### 3.Run Tests.
```
pytest test/
```
