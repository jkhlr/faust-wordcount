## Word Count - using Kafka and Faust

This is a demo implementation of a Word Count pipeline.

The project uses Apache Kafka to persistently store and distribute the processed data, 
and Faust to implement the processing pipeline.

As a demo dataset, a corpus of early modern scientific writing, curated by Alan 
Hogarth and released under the [
Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License
](
http://creativecommons.org/licenses/by-nc-sa/4.0/
) is used (see [here](
https://graphics.cs.wisc.edu/WP/vep/vep-early-modern-science-collection/)
).

### Pipeline Layout
The Pipeline consists of the following components:

- Producer: Scans the filesystem and writes the paths of all files that should 
be analyzed into the `files` stream

- Processors:
    -  `read_files`: receives a path from the `files` stream, reads the content 
    of the corresponding file and creates a `RedisBackedDocument` from it. The 
    document is then written into the `documents` stream. The content of the 
    file is either stored in the document, or (if the size exceeds Kafka's 
    message size limit) stored in Redis, with a reference to the entry stored in 
    the document. The size of a single document is therefore limited by the 
    maximum string size of Redis (512MB).
    - `split_documents`: receives a document from the `documents` stream and 
    splits its content into separate words. The content is pulled from redis if 
    necessary. The words are written into the `words` stream.
    - `count_words`: receives a word from the `words` stream and records its 
    occurrence in a table backed by a Kafka changelog topic. 

- Consumer: Periodically prints the current state of the table to the console, 
consuming the changelog topic populated by `count_words`.
    

### Deployment with `docker-compose`
To start the Kafka cluster and a Faust worker, run
```
docker-compose up --build -d
```
Open the logs with
```
docker-compose logs -f
```
Once the cluster is up (an empty table is printed to the log), run the following 
command to load a small (30KB) document into the pipeline:
```
docker-compose run wordcount load-document-small
```
The count of words (top 10) will be continuousely updated, which can be 
followed through the log.

A larger (1.1MB) document can be loaded into the pipeline with
```
docker-compose run wordcount load-document-large
```
and the whole dataset can be loaded with
```
docker-compose run wordcount load-all-documents
```
To inspect the state of the pipeline, Kafdrop can be accessed at 
`http://localhost:9000`
### Development
The automated `pytest` suite can be run with
```
docker-compose run wordcount test
```

To develop locally, stop the `docker-compose` worker with
```
docker-compose stop wordcount
```
and start a local worker with
```
word_count/app.py worker -l info
```
Python 3.8 and the dependencies (`pip install -r requirements.txt`) need to be 
installed locally.