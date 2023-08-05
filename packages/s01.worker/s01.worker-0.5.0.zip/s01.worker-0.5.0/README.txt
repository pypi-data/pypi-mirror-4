This package provides a daemon which is able to run buildout based scrapy
spider packages. (see s01.demo). The daemon processes pending crawl jobs stored
in mongodb. The daemon also provides a WSGI server providing a JSON-RPC 2.0 API.
The JSON-RPC proxy from the s01.client package can be used for install packages
and add new crawl jobs to the mongodb which is the queue.
