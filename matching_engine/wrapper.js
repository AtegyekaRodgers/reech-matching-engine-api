const http = require('http');

class Wrapper
{
    constructor(hostname,port)
    {
        //error handling
        if (typeof hostname !== 'string') {
            throw new Error('hostname must be a string');
        }
      
        if (typeof port !== 'number' || !Number.isInteger(port)) {
        throw new Error('port must be an integer');
        }

        this.host = hostname;
        this.port = port;
    }

    getJobTitleEmbedding(jobTitle) 
    {
        //checking if a valid string was entered
        if (typeof jobTitle !== 'string' || jobTitle.trim().length === 0) {
            return Promise.reject(new Error('jobTitle must be a non-empty string'));
          }
        
        //creating a resolve that will return the data if function ran successfully  
        return new Promise((resolve, reject) => {
            const options = {
            hostname: this.host,
            port: this.port,
            path: `/utilities/embed_job_title/?jobTitle=${encodeURIComponent(jobTitle)}`,
            method: 'GET'
            };

        //making the request
        const req = http.request(options, res => {
        let data = '';
        res.on('data', chunk => {
            data += chunk;
        });
        res.on('end', () => {
            const embedding = JSON.parse(data);
            resolve(embedding);
        });
        });

        //if theres an error display the error
        req.on('error', error => {
        reject(error);
        });

        req.end();
    });
    }

}


//creating ML model wrapper
const model = new Wrapper('127.0.0.1',8080)

//testing out the function
model.getJobTitleEmbedding('')
  .then(embedding => {
    console.log(embedding); // Do something with the embedding here
  })
  .catch(error => {
    console.error(error);
  });



